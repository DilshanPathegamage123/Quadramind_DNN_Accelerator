#!/usr/bin/env python3
"""Build results/golden_check/estimated_vs_actual_cycles.csv from the
verdict/raw JSONs produced by run_golden.py / run_golden_multi.py.

Estimated cycles come from pysim.software_ref.estimate_cycles (the Python
model's per-layer estimate for the given dataflow and array). Actual cycles
are the RTL cycle counts measured by cocotb in the same runs.

The Python estimate models an idealized full-array execution of the whole
layer in a single pass; the RTL harness executes one output pixel (OS/WS)
or one MAC-tuple (IS) per invocation, so both the total and the
per-invocation actuals are reported.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

FRAMEWORK = Path(os.environ.get("GOLDEN_FRAMEWORK_ROOT",
                                Path(os.path.abspath(__file__)).parents[2]))
sys.path.insert(0, str(FRAMEWORK))

from pysim.sim_config import LayerConfig                    # noqa: E402
from pysim.software_ref import estimate_cycles              # noqa: E402

RAW = FRAMEWORK / "results" / "golden_check" / "raw"
OUT = FRAMEWORK / "results" / "golden_check" / "estimated_vs_actual_cycles.csv"


def main() -> int:
    rows = []
    for vpath in sorted(RAW.glob("*_verdict.json")):
        v = json.loads(vpath.read_text())
        if "isprobe" in vpath.name or "probe" in vpath.name or "regr" in vpath.name:
            continue
        layer_dir = FRAMEWORK / v["layer"]
        cfg = LayerConfig(**json.loads((layer_dir / "config.json").read_text()))
        H, W = (int(t) for t in v["array"].split("x"))
        est = estimate_cycles(cfg, v["dataflow"], H, W)
        act_total = v["rtl_cycles_total"]
        n_inv = v["rtl_runs"]
        act_per = act_total / n_inv if n_inv else 0
        agree_total = min(est, act_total) / max(est, act_total) * 100 if act_total else 0
        agree_per = min(est, act_per) / max(est, act_per) * 100 if act_per else 0
        rows.append({
            "run": vpath.stem.replace("_verdict", ""),
            "kind": "single_dnn",
            "layer": v["layer"],
            "dataflow": v["dataflow"],
            "layout": v["layout"],
            "memory": v["memory"],
            "array": v["array"],
            "passed": v["passed"],
            "estimated_cycles_python": est,
            "actual_cycles_rtl_total": act_total,
            "rtl_invocations": n_inv,
            "actual_cycles_per_invocation": round(act_per, 1),
            "agreement_est_vs_total_pct": round(agree_total, 2),
            "agreement_est_vs_per_invocation_pct": round(agree_per, 2),
        })

    for mpath in sorted(RAW.glob("multi_*.json")):
        m = json.loads(mpath.read_text())
        est = 0
        for t in m["tasks"]:
            cfg = LayerConfig(**json.loads(
                (FRAMEWORK / t["layer"] / "config.json").read_text()))
            est += estimate_cycles(cfg, "OS", 8, 8)
        act = sum(t["cycles"] for t in m["tasks"])
        rows.append({
            "run": mpath.stem,
            "kind": "multi_dnn",
            "layer": ";".join(t["layer"] for t in m["tasks"]),
            "dataflow": "OS",
            "layout": "CHANNEL_MAJOR",
            "memory": "STAMP",
            "array": "8x8",
            "passed": m["all_pass"],
            "estimated_cycles_python": est,
            "actual_cycles_rtl_total": act,
            "rtl_invocations": len(m["tasks"]),
            "actual_cycles_per_invocation": round(act / len(m["tasks"]), 1),
            "agreement_est_vs_total_pct": round(
                min(est, act) / max(est, act) * 100, 2) if act else 0,
            "agreement_est_vs_per_invocation_pct": "",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    for r in rows:
        print(f"  {r['run']}: est={r['estimated_cycles_python']} "
              f"actual_total={r['actual_cycles_rtl_total']} "
              f"(x{r['rtl_invocations']} inv, {r['actual_cycles_per_invocation']}/inv) "
              f"agree_total={r['agreement_est_vs_total_pct']}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
