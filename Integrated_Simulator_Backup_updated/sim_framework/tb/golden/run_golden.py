#!/usr/bin/env python3
"""Build single_dnn_top under Verilator and run the golden-reference cocotb
test for one layer/config. Compares the RTL fixed-point output against the
TF expected.npy via pysim.golden_compare with a 5%-of-full-scale tolerance.

Usage:
  python tb/golden/run_golden.py --layer models/tiny_cnn/layer_00 \
      [--dataflow OS] [--layout CHANNEL_MAJOR] [--memory STAMP] \
      [--array 8x8] [--relu] [--num-banks 4] [--tol 0.05]

Prints one summary line and writes a JSON verdict next to the build.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

FRAMEWORK = Path(os.environ.get("GOLDEN_FRAMEWORK_ROOT",
                                Path(os.path.abspath(__file__)).parents[2]))
sys.path.insert(0, str(FRAMEWORK))

from pysim.golden_compare import compare_arrays  # noqa: E402

DATAFLOW_CODE = {"OS": 0, "IS": 1, "WS": 2}
MEMORY_CODE   = {"STAMP": 0, "PAGED": 1}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", required=True)
    ap.add_argument("--dataflow", default="OS", choices=["OS", "IS", "WS"])
    ap.add_argument("--layout", default="CHANNEL_MAJOR",
                    choices=["CHANNEL_MAJOR", "ROW_MAJOR", "COLUMN_MAJOR"])
    ap.add_argument("--memory", default="STAMP", choices=["STAMP", "PAGED"])
    ap.add_argument("--casting", default="MULTICAST",
                    choices=["MULTICAST", "UNICAST", "HYBRID"])
    ap.add_argument("--array", default="8x8")
    ap.add_argument("--num-banks", type=int, default=4)
    ap.add_argument("--frac-x", type=int, default=14)
    ap.add_argument("--frac-w", type=int, default=14)
    ap.add_argument("--tol", type=float, default=0.05,
                    help="relative tolerance as fraction of max|expected|")
    ap.add_argument("--relu", action="store_true",
                    help="apply ReLU to RTL output before comparing")
    ap.add_argument("--tag", default="", help="extra tag for result filename")
    args = ap.parse_args()

    H, W = (int(t) for t in args.array.split("x"))
    layer_dir = FRAMEWORK / args.layer
    assert (layer_dir / "expected.npy").exists(), f"no golden in {layer_dir}"

    from cocotb_tools.runner import get_runner

    # Verilator's makefiles refuse directories containing spaces, so builds
    # live outside the repo in a space-free location.
    build_root = Path(os.environ.get("GOLDEN_BUILD_ROOT",
                                     Path.home() / "sim_builds"))
    build_dir = build_root / "golden" / (
        f"sdt_{args.dataflow}_{args.memory}_{H}x{W}_b{args.num_banks}")
    sources = [FRAMEWORK / line.strip()
               for line in (FRAMEWORK / "rtl" / "all_sources.f").read_text().splitlines()
               if line.strip() and not line.strip().startswith("#")]

    runner = get_runner("verilator")
    runner.build(
        sources=sources,
        hdl_toplevel="single_dnn_top",
        build_dir=str(build_dir),
        always=False,
        parameters={
            "DATAFLOW": DATAFLOW_CODE[args.dataflow],
            "MEMORY":   MEMORY_CODE[args.memory],
            "ARRAY_HEIGHT": H, "ARRAY_WIDTH": W,
            "NUM_BANKS": args.num_banks,
        },
        build_args=["-Wno-fatal", "-Wno-DECLFILENAME", "-Wno-UNUSED",
                    "--timescale", "1ns/1ps",
                    "-I" + str(FRAMEWORK / "rtl" / "pkg"),
                    "-I" + str(FRAMEWORK / "rtl" / "interfaces")],
    )

    slug = (f"{layer_dir.parent.name}_{layer_dir.name}_{args.dataflow}_"
            f"{args.layout}_{args.memory}_{H}x{W}_b{args.num_banks}"
            + (f"_{args.casting}" if args.casting != "MULTICAST" else "")
            + (f"_{args.tag}" if args.tag else ""))
    result_json = FRAMEWORK / "results" / "golden_check" / "raw" / f"{slug}.json"

    t0 = time.time()
    runner.test(
        hdl_toplevel="single_dnn_top",
        test_module="test_golden_single",
        build_dir=str(build_dir),
        test_dir=str(build_dir / f"test_{slug}"),
        extra_env={
            "GOLDEN_LAYER_DIR":   str(layer_dir),
            "GOLDEN_RESULT_JSON": str(result_json),
            "GOLDEN_DATAFLOW":    args.dataflow,
            "GOLDEN_LAYOUT":      args.layout,
            "GOLDEN_MEMORY":      args.memory,
            "GOLDEN_CASTING":     args.casting,
            "GOLDEN_ARRAY_H":     str(H),
            "GOLDEN_ARRAY_W":     str(W),
            "GOLDEN_FRAC_X":      str(args.frac_x),
            "GOLDEN_FRAC_W":      str(args.frac_w),
            "PYTHONPATH": str(FRAMEWORK / "tb" / "golden") + os.pathsep
                          + str(FRAMEWORK),
        },
    )
    wall = time.time() - t0

    raw = json.loads(result_json.read_text())
    out_fixed = np.array(raw["out_fixed"], dtype=np.int64)
    actual = out_fixed.astype(np.float64) / (1 << (args.frac_x + args.frac_w))
    if args.relu:
        actual = np.maximum(actual, 0.0)

    expected = np.load(layer_dir / "expected.npy").astype(np.float64)
    fs = float(np.abs(expected).max())
    cmp = compare_arrays(actual, expected, tol=args.tol * fs)

    err = np.abs(actual.reshape(expected.shape) - expected)
    verdict = {
        "layer": str(layer_dir.relative_to(FRAMEWORK)),
        "dataflow": args.dataflow, "layout": args.layout,
        "memory": args.memory, "casting": args.casting, "array": f"{H}x{W}",
        "num_banks": args.num_banks, "relu": bool(args.relu),
        "tol_frac_of_fullscale": args.tol,
        "full_scale": fs,
        "passed": bool(cmp.passed),
        "assembly": raw.get("assembly", "hardware_full"),
        "n_total": cmp.n_total, "n_within_tol": cmp.n_within_tol,
        "max_abs_err": cmp.max_abs_err, "mean_abs_err": cmp.mean_abs_err,
        "max_rel_err_pct": float(err.max() / fs * 100.0),
        "mean_rel_err_pct": float(err.mean() / fs * 100.0),
        "rtl_cycles_total": raw["total_cycles"],
        "stats_bank_conflicts": raw.get("stats_bank_conflicts"),
        "stats_bank_conflict_stall_cycles": raw.get("stats_bank_conflict_stall_cycles"),
        "stats_loads_or_hits": raw.get("stats_loads_or_hits"),
        "stats_moves_or_misses": raw.get("stats_moves_or_misses"),
        "stats_keeps": raw.get("stats_keeps"),
        "stats_bytes_loaded": raw.get("stats_bytes_loaded"),
        "stats_bytes_moved": raw.get("stats_bytes_moved"),
        "rtl_runs": raw["n_runs"],
        "wall_seconds": round(wall, 1),
    }
    vpath = FRAMEWORK / "results" / "golden_check" / "raw" / f"{slug}_verdict.json"
    vpath.write_text(json.dumps(verdict, indent=2))

    status = "PASS" if cmp.passed else "FAIL"
    print(f"[{status}] {slug}: max_err={verdict['max_rel_err_pct']:.3f}% "
          f"mean_err={verdict['mean_rel_err_pct']:.4f}% of FS "
          f"({cmp.n_within_tol}/{cmp.n_total} within tol, "
          f"cycles={raw['total_cycles']}, runs={raw['n_runs']})")
    return 0 if cmp.passed else 1


if __name__ == "__main__":
    sys.exit(main())
