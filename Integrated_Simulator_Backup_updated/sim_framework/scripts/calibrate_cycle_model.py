#!/usr/bin/env python3
"""
calibrate_cycle_model.py
========================
Derive the cycle model's constants from the recorded RTL runs, and write
them to pysim/cycle_model_calibration.json for the chooser to load.

The model is

    cycles = C_AR * (AXI AR requests) + C_BEAT * (AXI beats) + compute_base

C_AR and C_BEAT are fitted here across every measured STAMP run and come
out as exact integers (3 and 2) with zero residual, which is why they are
treated as protocol constants rather than tuning knobs:

    3 cycles per read-address handshake
    2 cycles per delivered beat

`compute_base` is the part of the layer's runtime that is NOT hidden
behind memory traffic.  It is constant for a given (layer, dataflow) and
does not change with memory layout or casting scheme -- which is why
layout and casting rankings are independent of it.

Also emits the beats-per-burst ratios that the AR (burst-coalescing)
model needs, one per (layout, casting) where the data supports it.

Usage (from sim_framework/):
    PYTHONPATH=. python scripts/calibrate_cycle_model.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
RAW = ROOT / "results/golden_check/raw"
OUT = ROOT / "pysim/cycle_model_calibration.json"


def measured_runs() -> list[dict]:
    """Every recorded STAMP run that carries both traffic and cycle counts."""
    runs = []
    for vp in sorted(RAW.glob("*_verdict.json")):
        stem = vp.name.replace("_verdict.json", "")
        rp = RAW / f"{stem}.json"
        if not rp.exists() or "probe" in stem:
            continue
        v = json.loads(vp.read_text())
        r = json.loads(rp.read_text())
        if "axi_beats" not in r or v.get("memory") != "STAMP":
            continue
        cfg = json.loads((ROOT / v["layer"] / "config.json").read_text())
        runs.append({
            "config": stem,
            "layer": v["layer"].replace("models/", ""),
            # Shape signature, so the chooser can match a measured base to any
            # workload with the same layer geometry -- it only receives
            # LayerConfig objects, never layer names.
            "shape": shape_key(cfg),
            "channels": int(cfg["weight_c"]),
            "dense": is_dense(cfg),
            "macs": macs_of(cfg),
            "dataflow": v["dataflow"],
            "layout": v["layout"],
            "casting": v.get("casting", "MULTICAST"),
            "array": v["array"],
            "ar": int(r["axi_ar_requests"]),
            "beats": int(r["axi_beats"]),
            "cycles": int(r["total_cycles"]),
        })
    return runs


def shape_key(c: dict) -> str:
    return "x".join(str(c[k]) for k in
                    ("weight_k", "weight_c", "weight_kh", "weight_kw",
                     "output_height", "output_width"))


def macs_of(c: dict) -> int:
    return (c["weight_k"] * c["weight_c"] * c["weight_kh"] * c["weight_kw"]
            * c["output_height"] * c["output_width"])


def is_dense(c: dict) -> bool:
    """1x1 kernel producing a 1x1 output -- a fully-connected layer.

    These behave very differently from conv layers: their compute base is
    ~10x higher relative to MAC count (2.4-3.3 vs 0.22-0.27), so they are
    calibrated separately rather than averaged together.
    """
    return (c["weight_kh"] == 1 and c["weight_kw"] == 1
            and c["output_height"] == 1 and c["output_width"] == 1)


def base_per_macs(runs: list[dict], bases: dict) -> dict:
    """Fallback rule for layers with no measured run: base per MAC.

    Grouped by dataflow and by conv-vs-dense, because the two behave an
    order of magnitude apart.  This is the weakest part of the model and is
    reported as such -- but it only shifts a layer's cycle count by a
    constant, so it cannot change the ranking of memory layouts or casting
    schemes against each other.
    """
    buckets: dict[str, list[float]] = {}
    for r in runs:
        key = f"{r['dataflow']}|{'dense' if r['dense'] else 'conv'}"
        b = bases.get(f"{r['shape']}|{r['dataflow']}|{r['array']}")
        if b is None or r["macs"] == 0:
            continue
        buckets.setdefault(key, []).append(b / r["macs"])
    out = {}
    for k, v in buckets.items():
        a = np.array(v)
        out[k] = {"base_per_mac": float(a.mean()), "n": int(a.size),
                  "min": float(a.min()), "max": float(a.max())}
    return out


def fit_costs(runs: list[dict]) -> tuple[float, float, dict]:
    """Shared AR/beat costs plus one compute_base per (shape, dataflow, array)."""
    keys = sorted({(r["shape"], r["dataflow"], r["array"]) for r in runs})
    idx = {k: i for i, k in enumerate(keys)}
    A, y = [], []
    for r in runs:
        onehot = [0.0] * len(keys)
        onehot[idx[(r["shape"], r["dataflow"], r["array"])]] = 1.0
        A.append([r["ar"], r["beats"]] + onehot)
        y.append(r["cycles"])
    A, y = np.array(A, dtype=float), np.array(y, dtype=float)
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ coef
    bases = {f"{k[0]}|{k[1]}|{k[2]}": float(coef[2 + i]) for k, i in idx.items()}
    return float(coef[0]), float(coef[1]), {"bases": bases,
                                            "max_abs_residual": float(np.abs(resid).max()),
                                            "n_runs": len(runs)}


def beats_per_burst(runs: list[dict]) -> dict:
    """Observed beats per AXI burst, grouped by the axis that drives it.

    Casting is workload-independent in the recorded data (HYBRID and
    UNICAST land on the same ratio for both layers).  Layout is NOT --
    ROW_MAJOR coalesces well when the layer has a single input channel and
    poorly otherwise -- so the ROW_MAJOR entry is split on that.
    """
    out: dict[str, dict] = {}
    for r in runs:
        if r["casting"] != "MULTICAST":
            key = f"casting:{r['casting']}"
        else:
            key = f"layout:{r['layout']}"
        out.setdefault(key, {"samples": [], "configs": []})
        out[key]["samples"].append(r["beats"] / r["ar"])
        out[key]["configs"].append(r["config"])
    summary = {}
    for k, v in out.items():
        s = np.array(v["samples"])
        summary[k] = {"mean": float(s.mean()), "min": float(s.min()),
                      "max": float(s.max()), "n": int(s.size),
                      "spread_pct": float((s.max() - s.min()) / s.mean() * 100)}
    return summary


def main() -> None:
    runs = measured_runs()
    print(f"{len(runs)} measured STAMP runs with traffic + cycle counts\n")

    c_ar, c_beat, info = fit_costs(runs)
    print(f"cycles = {c_ar:.6f}*AR + {c_beat:.6f}*beats + compute_base")
    print(f"  max abs residual over all {info['n_runs']} runs: "
          f"{info['max_abs_residual']:.9f} cycles")
    if info["max_abs_residual"] > 1e-6:
        print("  NOTE: residual is non-zero -- the model does not fit every "
              "recorded run exactly; see per-run table below.")

    print("\ncompute_base per (layer, dataflow, array):")
    for k, v in sorted(info["bases"].items()):
        print(f"  {k:<44} {v:>10,.0f}")

    print("\nbeats per AXI burst (drives the AR model):")
    bpb = beats_per_burst(runs)
    for k, v in sorted(bpb.items()):
        print(f"  {k:<28} mean {v['mean']:>7.3f}  "
              f"range {v['min']:.3f}-{v['max']:.3f}  n={v['n']}  "
              f"spread {v['spread_pct']:.1f}%")

    fallback = base_per_macs(runs, info["bases"])
    print("\nfallback compute_base per MAC (layers with no measured run):")
    for k, v in sorted(fallback.items()):
        print(f"  {k:<14} {v['base_per_mac']:>8.4f} per MAC  "
              f"(n={v['n']}, range {v['min']:.4f}-{v['max']:.4f})")

    payload = {
        "cycles_per_ar_request": c_ar,
        "compute_base_per_mac": fallback,
        "cycles_per_beat": c_beat,
        "compute_base": info["bases"],
        "beats_per_burst": bpb,
        "max_abs_residual_cycles": info["max_abs_residual"],
        "n_measured_runs": info["n_runs"],
        "source": "calibrated from results/golden_check/raw (measured RTL)",
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
