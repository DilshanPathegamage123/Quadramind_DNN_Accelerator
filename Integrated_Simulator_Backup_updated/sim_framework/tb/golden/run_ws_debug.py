#!/usr/bin/env python3
import os
import sys
from pathlib import Path

FRAMEWORK = Path(os.environ.get("GOLDEN_FRAMEWORK_ROOT",
                                Path(os.path.abspath(__file__)).parents[2]))
sys.path.insert(0, str(FRAMEWORK))

from cocotb_tools.runner import get_runner

W = int(sys.argv[1]) if len(sys.argv) > 1 else 2
build_root = Path(os.environ.get("GOLDEN_BUILD_ROOT", Path.home() / "sim_builds"))
build_dir = build_root / "golden" / f"sdt_WS_STAMP_8x{W}_b4"

sources = [FRAMEWORK / line.strip()
           for line in (FRAMEWORK / "rtl" / "all_sources.f").read_text().splitlines()
           if line.strip() and not line.strip().startswith("#")]

runner = get_runner("verilator")
runner.build(
    sources=sources,
    hdl_toplevel="single_dnn_top",
    build_dir=str(build_dir),
    always=False,
    parameters={"DATAFLOW": 2, "MEMORY": 0, "ARRAY_HEIGHT": 8, "ARRAY_WIDTH": W},
    build_args=["-Wno-fatal", "-Wno-DECLFILENAME", "-Wno-UNUSED",
                "--timescale", "1ns/1ps",
                "-I" + str(FRAMEWORK / "rtl" / "pkg"),
                "-I" + str(FRAMEWORK / "rtl" / "interfaces")],
)
runner.test(
    hdl_toplevel="single_dnn_top",
    test_module="test_ws_debug",
    build_dir=str(build_dir),
    test_dir=str(build_dir / "test_ws_debug"),
    extra_env={
        "GOLDEN_LAYER_DIR":   str(FRAMEWORK / "models/tiny_cnn/layer_00"),
        "GOLDEN_RESULT_JSON": str(FRAMEWORK / "results/golden_check/raw/ws_debug.json"),
        "GOLDEN_DATAFLOW":    "WS",
        "GOLDEN_LAYOUT":      "CHANNEL_MAJOR",
        "GOLDEN_MEMORY":      "STAMP",
        "GOLDEN_ARRAY_H":     "8",
        "GOLDEN_ARRAY_W":     str(W),
        "GOLDEN_FRAC_X":      "14",
        "GOLDEN_FRAC_W":      "14",
        "PYTHONPATH": str(FRAMEWORK / "tb" / "golden") + os.pathsep + str(FRAMEWORK),
    },
)
