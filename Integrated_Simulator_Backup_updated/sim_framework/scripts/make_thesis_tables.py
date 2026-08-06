#!/usr/bin/env python3
"""
make_thesis_tables.py
=====================
Build two enriched tables for the thesis notebook, both from MEASURED RTL
data only:

  1. correctness_detail.csv
     Per configuration: the worst-deviating output element with its
     MEASURED (RTL) value, its GOLDEN (TensorFlow) value and the error
     between them in separate columns, with units stated.  The existing
     f2_correctness_margin.csv only carries the relative error percentage,
     which cannot be read back to actual values.

     Every reconstructed row is CROSS-CHECKED against the aggregate the
     RTL run already recorded in its *_verdict.json.  A row whose
     recomputed max-abs-error disagrees with the recorded one is reported
     as a mismatch rather than silently written out.

  2. config_axes_performance.csv
     Stationary scheme x memory layout x casting scheme, compared on the
     metrics those knobs actually change: execution cycles, AXI read
     bursts and AXI data beats.  Correctness is deliberately NOT the
     comparison metric on these axes -- see the module note below.

WHY CORRECTNESS CANNOT RANK THESE THREE KNOBS
----------------------------------------------
Every configuration of a given layer produces the SAME numerical error
(e.g. all eight mnist_cnn layer_00 configurations record
max_rel_err_pct = 0.008926...).  That is expected: the error is
fixed-point quantisation error of the layer's arithmetic, and stationary
scheme / layout / casting only change the ORDER and ROUTE by which
identical operands reach the PEs.  So a correctness chart across these
axes is flat by construction.  It is still worth plotting -- as an
INVARIANCE result proving the three knobs are performance choices with no
accuracy cost -- but it cannot rank them.  Ranking needs the performance
table.

Usage (from sim_framework/):
    PYTHONPATH=. python scripts/make_thesis_tables.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "results/golden_check/raw"
OUT = ROOT / "results/thesis_notebook/tables"
BUNDLE = ROOT / "results/thesis_notebook/data_bundle/golden_check/figures"

# Output activations are dimensionless real numbers reconstructed from the
# RTL's fixed-point words (Q with frac_x + frac_w fractional bits).  Kept
# short so column headers stay readable; the "dimensionless" nature is
# explained in the notebook prose rather than repeated in every header.
UNITS = "activation units"


def _layer_dir(layer_rel: str) -> Path:
    return ROOT / layer_rel


def _load_expected(layer_rel: str) -> np.ndarray | None:
    p = _layer_dir(layer_rel) / "expected.npy"
    return np.load(p) if p.exists() else None


def _configs() -> list[tuple[str, dict, dict]]:
    """All (stem, verdict, raw) triples, covering BOTH recorded layouts.

    Most runs write a separate <stem>_verdict.json.  The STAMP-vs-PAGED
    divergence runs instead embed {"verdict": {...}} inside the raw file
    and carry no frac_x/frac_w -- those are handled here so they are not
    silently missing from the table (they appear in
    f2_correctness_margin.csv, so dropping them would under-report).
    """
    out = []
    for verdict_path in sorted(RAW.glob("*_verdict.json")):
        stem = verdict_path.name.replace("_verdict.json", "")
        raw_path = RAW / f"{stem}.json"
        if raw_path.exists():
            out.append((stem, json.loads(verdict_path.read_text()),
                        json.loads(raw_path.read_text())))

    for raw_path in sorted(RAW.glob("divergence_*.json")):
        raw = json.loads(raw_path.read_text())
        if "verdict" not in raw:
            continue
        v = dict(raw["verdict"])
        layer = raw["layer"]
        if "models/" in layer:                    # stored as an absolute path
            layer = "models/" + layer.split("models/", 1)[1]
        # These runs do not record dataflow/layout/casting.  The values below
        # are read off the test that produced them, not guessed:
        # tb/golden/test_scheme_divergence.py runs "the full OS tile sequence"
        # (docstring, line 3) with LAYOUTS["CHANNEL_MAJOR"] (line 148) and the
        # default MULTICAST casting.  Flagged in "Attribute source" so a
        # reader can tell these apart from fields the run itself recorded.
        v.update({"layer": layer, "dataflow": "OS", "layout": "CHANNEL_MAJOR",
                  "memory": raw.get("scheme", "STAMP"), "casting": "MULTICAST",
                  "array": "8x8",
                  "_attr_source": "from test source "
                                  "(test_scheme_divergence.py: OS tile "
                                  "sequence, CHANNEL_MAJOR)"})
        out.append((raw_path.stem, v, raw))
    return out


def _relu_by_layer(configs) -> dict[str, bool]:
    """Which layers have ReLU folded into the golden comparison.

    Most verdicts record `relu` explicitly; the divergence runs do not.
    Rather than guessing, take the flag from the runs that DO record it for
    the same layer.  The cross-check against the recorded error still has
    the final say.
    """
    out: dict[str, bool] = {}
    for _stem, v, _raw in configs:
        if "relu" in v:
            out[v["layer"]] = bool(v["relu"]) or out.get(v["layer"], False)
    return out


# Canonical axis orders used across this project (config_chooser.DATAFLOWS
# etc.), so tables read OS/IS/WS rather than alphabetical IS/OS/WS.
AXIS_ORDER = {
    "Stationary scheme": ["OS", "IS", "WS"],
    "Memory layout": ["ROW_MAJOR", "COLUMN_MAJOR", "CHANNEL_MAJOR"],
    "Casting scheme": ["MULTICAST", "HYBRID", "UNICAST"],
    "Memory backend": ["STAMP", "PAGED"],
}


def _order_by_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """Sort so the configuration space is legible, not so errors cluster.

    Sorting by error puts every identically-quantised run next to its twins,
    which makes a systematic sweep look like repeated rows.  Ordering by the
    axes themselves shows at a glance which combinations were covered.
    """
    out = df.copy()
    keys = []
    for col, order in AXIS_ORDER.items():
        if col in out.columns:
            kc = f"_sort_{col}"
            out[kc] = pd.Categorical(out[col], categories=order, ordered=True)
            keys.append(kc)
    sort_cols = (["Workload / layer"] + keys
                 + ["Array size (PEs)", "Memory banks (count)",
                    "Configuration"])
    sort_cols = [c for c in sort_cols if c in out.columns]
    out = out.sort_values(sort_cols, kind="mergesort").reset_index(drop=True)
    return out.drop(columns=[c for c in out.columns
                             if c.startswith("_sort_")])


def coverage_summary(df: pd.DataFrame) -> pd.DataFrame:
    """How many runs cover each value of each configuration axis."""
    rows = []
    for col, order in AXIS_ORDER.items():
        if col not in df.columns:
            continue
        counts = df[col].value_counts()
        for value in order:
            if value in counts.index:
                rows.append({"Configuration axis": col, "Setting": value,
                             "Runs covering it (count)": int(counts[value])})
    return pd.DataFrame(rows)


def build_correctness_detail() -> pd.DataFrame:
    rows, skipped, mismatches = [], [], []
    configs = _configs()
    relu_map = _relu_by_layer(configs)

    for stem, v, raw in configs:
        if "out_fixed" not in raw:
            skipped.append((stem, "raw file carries no output tensor"))
            continue

        expected = _load_expected(v["layer"])
        if expected is None:
            skipped.append((stem, f"no golden tensor for {v['layer']}"))
            continue

        # The divergence runs record no frac_x/frac_w.  Assume the project's
        # standard Q14.14 and let the cross-check below prove or reject it:
        # a wrong assumption cannot reproduce the recorded error exactly.
        frac = raw.get("frac_x", 14) + raw.get("frac_w", 14)
        measured = np.asarray(raw["out_fixed"], dtype=np.float64) / (1 << frac)
        golden = np.asarray(expected, dtype=np.float64)

        # trim to the channels the run actually captured
        n_ch = measured.shape[-1]
        golden_cmp = golden[..., :n_ch]
        if measured.shape != golden_cmp.shape:
            skipped.append((stem, f"shape {measured.shape} vs {golden_cmp.shape}"))
            continue
        if v.get("relu", relu_map.get(v["layer"], False)):
            measured = np.maximum(measured, 0.0)

        err = np.abs(measured - golden_cmp)
        idx = np.unravel_index(np.argmax(err), err.shape)
        full_scale = float(np.abs(golden_cmp).max())
        max_abs = float(err.max())

        # Cross-check against what the RTL run itself recorded.  Prefer the
        # absolute error where present; the divergence runs record only the
        # relative one.
        tol_frac = float(v.get("tol_frac_of_fullscale", 0.05))
        rel_pct = max_abs / full_scale * 100.0
        tol_abs = tol_frac * full_scale

        if "max_abs_err" in v:
            recorded, got, what = float(v["max_abs_err"]), max_abs, "abs err"
        else:
            recorded, got, what = float(v["max_rel_err_pct"]), rel_pct, "rel err%"
        if not np.isclose(got, recorded, rtol=1e-6, atol=1e-12):
            mismatches.append((stem, what, got, recorded))
            continue

        # Debug probes from the F1/F4 investigations are recorded alongside
        # the validation runs.  They are kept (dropping them silently would
        # be cherry-picking) but labelled, so the headline table can show the
        # validation set without hiding that the probes exist.
        run_type = "debug probe" if "probe" in stem else "validation"

        rows.append({
            "Configuration": stem,
            "Run type": run_type,
            "Workload / layer": v["layer"].replace("models/", ""),
            "Stationary scheme": v["dataflow"],
            "Memory layout": v["layout"],
            "Casting scheme": v.get("casting", "MULTICAST"),
            "Memory backend": v["memory"],
            "Array size (PEs)": v["array"],
            # Without this the bank sweep (2/4/8/16 banks) looks like four
            # identical rows -- the runs differ only on this axis.
            "Memory banks (count)": int(v.get("num_banks",
                                              raw.get("num_banks_build", 4))),
            "Output elements compared (count)":
                int(v.get("n_total", golden_cmp.size)),
            "Elements within tolerance (count)":
                int(v.get("n_within_tol", int((err <= tol_abs).sum()))),
            "Worst element (row, col, channel)": str(tuple(int(i) for i in idx[-3:])),
            f"Measured value, RTL ({UNITS})": float(measured[idx]),
            f"Golden value, TensorFlow ({UNITS})": float(golden_cmp[idx]),
            f"Absolute error ({UNITS})": max_abs,
            f"Full-scale reference ({UNITS})": full_scale,
            f"Tolerance ({UNITS})": tol_abs,
            "Relative error (% of full scale)": rel_pct,
            "Tolerance (% of full scale)": tol_frac * 100.0,
            "Safety margin (times below tolerance)": tol_abs / max_abs,
            "Result": "PASS" if max_abs <= tol_abs else "FAIL",
            "Data source": "measured (RTL) vs golden (TensorFlow)",
            "Attribute source": v.get("_attr_source", "recorded in result file"),
        })

    if mismatches:
        print("  MISMATCH vs recorded verdict (not written):")
        for stem, what, got, want in mismatches:
            print(f"    {stem}: recomputed {what} {got:.6g} vs "
                  f"recorded {want:.6g}")
    if skipped:
        print(f"  skipped {len(skipped)} config(s):")
        for stem, why in skipped[:8]:
            print(f"    {stem}: {why}")

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = _order_by_coverage(df)

    # A validation run that FAILED would be a real finding, not a table
    # formatting problem -- surface it loudly rather than let it blend in.
    bad = df[(df["Run type"] == "validation") & (df["Result"] == "FAIL")]
    if not bad.empty:
        print(f"  *** {len(bad)} VALIDATION run(s) FAILED tolerance:")
        for c in bad["Configuration"]:
            print(f"      {c}")
    n_probe = int((df["Run type"] == "debug probe").sum())
    print(f"  {len(df) - n_probe} validation runs, {n_probe} debug probes "
          f"(labelled, not dropped)")
    return df


def build_config_axes_performance() -> pd.DataFrame:
    """Stationary x layout x casting, on the metrics they actually change.

    Only STAMP runs at a fixed array size are included, so the three knobs
    are compared against each other and not against the memory-backend
    study (which f5_memory_management.csv already covers).
    """
    rows = []
    for verdict_path in sorted(RAW.glob("*_verdict.json")):
        v = json.loads(verdict_path.read_text())
        stem = verdict_path.name.replace("_verdict.json", "")
        raw_path = RAW / f"{stem}.json"
        if not raw_path.exists():
            continue
        raw = json.loads(raw_path.read_text())
        if v["memory"] != "STAMP":
            continue                      # memory-backend axis lives in f5
        if "axi_beats" not in raw:
            continue
        rows.append({
            "Configuration": stem,
            "Workload / layer": v["layer"].replace("models/", ""),
            "Stationary scheme": v["dataflow"],
            "Memory layout": v["layout"],
            "Casting scheme": v.get("casting", "MULTICAST"),
            "Array size (PEs)": v["array"],
            "Execution time (clock cycles)": int(raw["total_cycles"]),
            "Off-chip read bursts (AXI AR requests)": int(raw["axi_ar_requests"]),
            "Off-chip data transferred (AXI beats)": int(raw["axi_beats"]),
            "Relative error (% of full scale)":
                float(v["max_rel_err_pct"]),
            "Data source": "measured (RTL)",
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["Workload / layer", "Stationary scheme",
                             "Memory layout", "Casting scheme"]
                            ).reset_index(drop=True)
    return df


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    print("Building correctness_detail.csv (measured vs golden per config)")
    detail = build_correctness_detail()
    print(f"  {len(detail)} configurations reconstructed and cross-checked")

    print("\nBuilding config_axes_performance.csv "
          "(stationary x layout x casting)")
    perf = build_config_axes_performance()
    print(f"  {len(perf)} STAMP configurations")
    if not perf.empty:
        n_err = perf.groupby("Workload / layer")[
            "Relative error (% of full scale)"].nunique()
        for layer, n in n_err.items():
            print(f"    {layer}: {n} distinct error value(s) across all "
                  f"stationary/layout/casting configs")

    cov = coverage_summary(detail[detail["Run type"] == "validation"])
    print("\n  Axis coverage (validation runs):")
    for _, r in cov.iterrows():
        print(f"    {r['Configuration axis']:<20} {r['Setting']:<15} "
              f"{r['Runs covering it (count)']}")

    for target in (OUT, BUNDLE):
        target.mkdir(parents=True, exist_ok=True)
        detail.to_csv(target / "correctness_detail.csv", index=False)
        perf.to_csv(target / "config_axes_performance.csv", index=False)
        cov.to_csv(target / "axis_coverage.csv", index=False)
        try:
            shown = target.relative_to(ROOT)
        except ValueError:
            shown = target
        print(f"  wrote both tables to {shown}")


if __name__ == "__main__":
    main()
