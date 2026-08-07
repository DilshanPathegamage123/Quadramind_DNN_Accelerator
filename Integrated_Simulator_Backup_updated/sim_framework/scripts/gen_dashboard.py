#!/usr/bin/env python3
"""Build the standalone results dashboard for the final evaluation.

Unlike gen_viva_page.py (a narrative report with static figures), this produces
an operable dashboard: the measured counters are embedded as JSON and every
chart is drawn as inline SVG in the browser, so it is interactive, ~60 KB
instead of ~500 KB, and stays sharp at any projector resolution.

No network, no server, no dependencies. Double-click the output file.

Usage:
    PYTHONPATH=. python scripts/gen_dashboard.py [-o OUT.html]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REPO = ROOT.parent

STAMP_DIR = REPO / "static_hash_and_tagless_memory"
METADATA = STAMP_DIR / "stamp_metadata.json"
XSIM_LOG = ROOT / "results" / "vivado" / "stamp_controller_xsim.log"
EXP_DIR = ROOT / "results" / "exp4b_stamp_vs_paged"

TEMPLATE_PATH = Path(__file__).with_name("dashboard_template.html")


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path) as fh:
        return list(csv.DictReader(fh))


def num(v, default=0):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def collect() -> dict:
    from pysim.stamp_ref import naive_baseline_bytes, run_metadata

    with open(METADATA) as fh:
        meta = json.load(fh)
    ctrl = run_metadata(meta)
    naive = naive_baseline_bytes(meta)

    # --- compiler's own bookkeeping, independent of the FSM model ------
    comp = {k: 0 for k in ("loads", "moves", "keeps", "allocs", "zeros",
                           "load_bytes", "move_bytes", "keep_bytes", "zero_bytes")}
    for d in meta["deltas"]:
        for k in comp:
            comp[k] += d["stats"].get(k, 0)

    # --- Vivado xsim counters -----------------------------------------
    rtl: dict = {}
    if XSIM_LOG.exists():
        log = XSIM_LOG.read_text(errors="replace")
        for key in ("loads", "moves", "keeps", "allocs", "zeros",
                    "bytes_loaded", "bytes_moved", "bytes_zeroed", "bad_ops"):
            m = re.search(rf"stats_{key}\s*=\s*(\d+)\s*$", log, re.M)
            if m:
                rtl[key] = int(m.group(1))
        m = re.search(r"phases replayed\s*=\s*(\d+)\s*/\s*(\d+)", log)
        if m:
            rtl["phases_replayed"], rtl["phases_total"] = int(m.group(1)), int(m.group(2))
        m = re.search(r"delta ops executed\s*=\s*(\d+)", log)
        if m:
            rtl["ops_executed"] = int(m.group(1))
        rtl["passes"] = len(re.findall(r"PASS", log))
        rtl["fails"] = len(re.findall(r"FAIL {2}", log))

    # --- measured scheme comparison -----------------------------------
    schemes = []
    for r in read_csv(EXP_DIR / "stamp_vs_paged.csv"):
        schemes.append({
            "layer": r["layer"], "scheme": r["scheme"],
            "compute_cycles": num(r["compute_cycles"]),
            "program_cycles": num(r["program_cycles"]),
            "replay_cycles": num(r["replay_cycles"]),
            "axi_ar_requests": num(r["axi_ar_requests"]),
            "axi_beats": num(r["axi_beats"]),
            "bank_conflicts": num(r["bank_conflicts"]),
            "stall_port_cycles": num(r["stall_port_cycles"]),
        })

    banks = []
    for r in read_csv(EXP_DIR / "bank_conflict_sweep.csv"):
        banks.append({
            "n_banks": num(r["n_banks"]), "pattern": r["pattern"],
            "stall_port_cycles": num(r["stall_port_cycles"]),
            "reads_served": num(r["reads_served"]),
            "window_cycles": num(r["window_cycles"]),
        })

    tiny_s = next((s for s in schemes if s["layer"] == "tiny L0" and s["scheme"] == "STAMP"), None)
    tiny_p = next((s for s in schemes if s["layer"] == "tiny L0" and s["scheme"] == "PAGED"), None)
    ratio = (tiny_p["bank_conflicts"] / tiny_s["bank_conflicts"]
             if tiny_s and tiny_s["bank_conflicts"] else 0)

    ex_ops = meta["deltas"][0]["operations"]

    # --- measured Vivado out-of-context synthesis --------------------------
    area = []
    for r in read_csv(STAMP_DIR / "synth" / "work" / "out" / "area_results.csv"):
        area.append({
            "config": r["config"], "scheme": r["scheme"],
            "knob": r["knob"], "knob_value": num(r["knob_value"]),
            "luts": num(r["luts"]), "ffs": num(r["ffs"]),
            "brams": num(r["brams"]), "fmax": float(r.get("fmax_mhz") or 0),
        })

    # --- design-space sweep of the compiler -------------------------------
    sweep = []
    for r in read_csv(ROOT / "results" / "exp4_memory_management" / "sweep_stamp.csv"):
        sweep.append({
            "layer": r["layer"], "spad_kb": num(r["spad_kb"]),
            "array": r["array"], "phases": num(r["phases"]),
            "reduction": float(r["reduction_pct"]),
            "bytes_dram": num(r["bytes_dram"]),
            "metadata_bytes": num(r["metadata_bytes"]),
        })
    limits = read_csv(ROOT / "results" / "exp4_memory_management" / "capacity_limits.csv")

    return {
        "phases": meta["num_phases"],
        "deltas": len(meta["deltas"]),
        "totalOps": sum(len(d["operations"]) for d in meta["deltas"]),
        "spadBytes": meta["on_chip_size"],
        "naiveBytes": naive,
        "stampBytes": ctrl.bytes_loaded,
        "reductionPct": round(100.0 * (1 - ctrl.bytes_loaded / naive), 1) if naive else 0,
        "conflictRatio": round(ratio),
        "opMix": [
            {"op": "keep", "count": ctrl.keeps, "bytes": comp["keep_bytes"], "dram": False},
            {"op": "move", "count": ctrl.moves, "bytes": ctrl.bytes_moved, "dram": False},
            {"op": "load", "count": ctrl.loads, "bytes": ctrl.bytes_loaded, "dram": True},
            {"op": "alloc", "count": ctrl.allocs, "bytes": 0, "dram": False},
            {"op": "zero", "count": ctrl.zeros, "bytes": ctrl.bytes_zeroed, "dram": False},
        ],
        "verify": [
            {"label": "LOAD operations", "c": comp["loads"], "m": ctrl.loads, "r": rtl.get("loads")},
            {"label": "MOVE operations", "c": comp["moves"], "m": ctrl.moves, "r": rtl.get("moves")},
            {"label": "KEEP operations", "c": comp["keeps"], "m": ctrl.keeps, "r": rtl.get("keeps")},
            {"label": "ALLOC operations", "c": comp["allocs"], "m": ctrl.allocs, "r": rtl.get("allocs")},
            {"label": "ZERO operations", "c": comp["zeros"], "m": ctrl.zeros, "r": rtl.get("zeros")},
            {"label": "Bytes read from DRAM", "c": comp["load_bytes"], "m": ctrl.bytes_loaded, "r": rtl.get("bytes_loaded")},
            {"label": "Bytes moved on-chip", "c": comp["move_bytes"], "m": ctrl.bytes_moved, "r": rtl.get("bytes_moved")},
            {"label": "Bytes zero-filled", "c": comp["zero_bytes"], "m": ctrl.bytes_zeroed, "r": rtl.get("bytes_zeroed")},
        ],
        "schemes": schemes,
        "banks": banks,
        "rtl": rtl,
        "area": area,
        "sweep": sweep,
        "sweepStats": {
            "n": len(sweep),
            "infeasible": len(limits),
            "min": round(min((s["reduction"] for s in sweep), default=0), 1),
            "mean": round(sum(s["reduction"] for s in sweep) / len(sweep), 1) if sweep else 0,
            "max": round(max((s["reduction"] for s in sweep), default=0), 1),
        },
        "example": [{"op": o["op_type"], "tile": o["tile_type"], "size": o["size"]} for o in ex_ops],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", default=str(ROOT / "results" / "memory_dashboard.html"))
    args = ap.parse_args()

    data = collect()
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    html = template.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}  ({len(html)/1024:.0f} KB)")
    if not data["rtl"]:
        print("NOTE: no Vivado log found - RTL column will show dashes.")


if __name__ == "__main__":
    main()
