#!/usr/bin/env python3
"""Build multi_dnn_top and run the multi-DNN golden mix under one scheduler.

Usage: python tb/golden/run_golden_multi.py --sched FIFO|AIMT|BATCHDNN_PP
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

FRAMEWORK = Path(os.environ.get("GOLDEN_FRAMEWORK_ROOT",
                                Path(os.path.abspath(__file__)).parents[2]))
sys.path.insert(0, str(FRAMEWORK))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sched", default="FIFO",
                    choices=["FIFO", "LIFO", "AIMT", "BATCHDNN", "BATCHDNN_PP"])
    ap.add_argument("--array", default="8x8")
    args = ap.parse_args()
    H, W = (int(t) for t in args.array.split("x"))

    from cocotb_tools.runner import get_runner

    build_root = Path(os.environ.get("GOLDEN_BUILD_ROOT",
                                     Path.home() / "sim_builds"))
    build_dir = build_root / "golden" / f"mdt_OS_STAMP_{H}x{W}"
    sources = [FRAMEWORK / line.strip()
               for line in (FRAMEWORK / "rtl" / "all_sources.f").read_text().splitlines()
               if line.strip() and not line.strip().startswith("#")]

    runner = get_runner("verilator")
    runner.build(
        sources=sources,
        hdl_toplevel="multi_dnn_top",
        build_dir=str(build_dir),
        always=False,
        parameters={"DATAFLOW": 0, "MEMORY": 0,
                    "ARRAY_HEIGHT": H, "ARRAY_WIDTH": W},
        build_args=["-Wno-fatal", "-Wno-DECLFILENAME", "-Wno-UNUSED",
                    "--timescale", "1ns/1ps",
                    "-I" + str(FRAMEWORK / "rtl" / "pkg"),
                    "-I" + str(FRAMEWORK / "rtl" / "interfaces")],
    )

    result_json = (FRAMEWORK / "results" / "golden_check" / "raw"
                   / f"multi_{args.sched}_{H}x{W}.json")
    runner.test(
        hdl_toplevel="multi_dnn_top",
        test_module="test_golden_multi",
        build_dir=str(build_dir),
        test_dir=str(build_dir / f"test_{args.sched}"),
        extra_env={
            "GOLDEN_SCHED":       args.sched,
            "GOLDEN_RESULT_JSON": str(result_json),
            "GOLDEN_FRAMEWORK":   str(FRAMEWORK),
            "GOLDEN_ARRAY_H":     str(H),
            "GOLDEN_ARRAY_W":     str(W),
            "GOLDEN_FRAC_X":      "14",
            "GOLDEN_FRAC_W":      "14",
            "PYTHONPATH": str(FRAMEWORK / "tb" / "golden") + os.pathsep
                          + str(FRAMEWORK),
        },
    )

    res = json.loads(result_json.read_text())
    status = "PASS" if res["all_pass"] else "FAIL"
    order = [o["task"] for o in res["dispatch_order"]]
    print(f"[{status}] multi {args.sched}: completions={res['completions']} "
          f"order={order} cycles={res['total_cycles']}")
    for t in res["tasks"]:
        print(f"    task{t['task']} {t['layer']} px{t['pixel']}: "
              f"max_err={t['max_err_pct_fs']:.3f}%FS "
              f"dispatches={t['dispatches']} "
              f"{'PASS' if t['passed'] else 'FAIL'}")
    return 0 if res["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
