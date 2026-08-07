#!/usr/bin/env python3
"""Comprehensive sweep of the static (STAMP) memory management scheme.

Scope: the on-chip memory management module only. This script does not touch
the systolic array, scheduler or loop-optimizer experiments.

Nothing here is a hardcoded performance factor. For every point in the grid the
script actually runs the stamp compiler on that layer, then replays the emitted
delta-op stream through the cycle-accurate controller model. The reported
numbers are what those two produce.

Grid:
    layer shape      x   scratchpad capacity   x   systolic array size

Outputs (results/exp4_memory_management/):
    sweep_stamp.csv          one row per grid point
    capacity_limits.csv      which (layer, scratchpad) pairs do not fit

Usage:
    PYTHONPATH=. python scripts/sweep_memory_schemes.py
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REPO = ROOT.parent
STAMP_DIR = REPO / "static_hash_and_tagless_memory"

import pandas as pd

from pysim.stamp_ref import run_stream


def load_compiler():
    """Import stamp_compiler.py from the memory-management tree."""
    spec = importlib.util.spec_from_file_location(
        "stamp_compiler", STAMP_DIR / "stamp_compiler.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Representative convolution shapes taken from real networks, chosen to span
# the axes that actually change reuse behaviour: spatial size, channel depth,
# and kernel size.
LAYERS = [
    # name,            C,   H,   W,   K,  KH, KW, stride, pad
    ("early-conv 3x3",  16,  28,  28,  32,  3,  3, 1, 1),
    ("mid-conv 3x3",    32,  14,  14,  64,  3,  3, 1, 1),
    ("late-conv 3x3",   64,   7,   7, 128,  3,  3, 1, 1),
    ("pointwise 1x1",   64,  14,  14,  64,  1,  1, 1, 0),
    ("wide-spatial",     8,  56,  56,  16,  3,  3, 1, 1),
    ("large-kernel 5x5",16,  14,  14,  32,  5,  5, 1, 1),
]

SPAD_KB = [8, 16, 32, 64]
ARRAYS = [(4, 4), (8, 8)]
BYTES_PER_ELEM = 4


def layer_cfg(C, H, W, K, KH, KW, stride, pad):
    oh = (H + 2 * pad - KH) // stride + 1
    ow = (W + 2 * pad - KW) // stride + 1
    return {
        "input_channels": C, "input_height": H, "input_width": W,
        "output_channels": K, "output_height": oh, "output_width": ow,
        "kernel_height": KH, "kernel_width": KW,
        "stride": stride, "padding": pad,
    }


def run_point(sc_mod, name, dims, spad_bytes, array):
    """Compile one (layer, scratchpad, array) point. Returns a row or None."""
    cfg = layer_cfg(*dims)
    comp = sc_mod.StampCompiler(on_chip_size=spad_bytes, data_width=BYTES_PER_ELEM)
    comp.create_conv_phases(cfg, array)
    comp.allocate_stamps()          # raises ValueError if a phase does not fit
    comp.compute_deltas()

    ops = [d.operations for d in comp.deltas]
    stats = run_stream(
        [[{"op_type": o.op_type, "src_addr": o.src_addr,
           "dst_addr": o.dst_addr, "size": o.size} for o in phase]
         for phase in ops],
        data_width_bits=BYTES_PER_ELEM * 8,
    )

    # Baseline: a tag-based scheme re-reads every input and weight tile at
    # every phase. Output tiles are never a DRAM read under either scheme.
    naive = sum(loc.tile.size_bytes
                for s in comp.stamps for loc in s.locations
                if loc.tile.tile_type != sc_mod.TileType.OUTPUT)
    naive_cycles = (naive // BYTES_PER_ELEM) * 10   # 10 cycles/word DRAM

    return {
        "layer": name,
        "spad_kb": spad_bytes // 1024,
        "array": f"{array[0]}x{array[1]}",
        "phases": len(comp.phases),
        "delta_ops": stats.loads + stats.moves + stats.keeps + stats.allocs + stats.zeros,
        "loads": stats.loads, "moves": stats.moves, "keeps": stats.keeps,
        "allocs": stats.allocs, "zeros": stats.zeros,
        "bytes_dram": stats.bytes_loaded,
        "bytes_moved": stats.bytes_moved,
        "bytes_zeroed": stats.bytes_zeroed,
        "bytes_naive": naive,
        "reduction_pct": round(100.0 * (1 - stats.bytes_loaded / naive), 2) if naive else 0.0,
        "ctrl_cycles": stats.cycles,
        "naive_cycles": naive_cycles,
        "cycle_saving_pct": round(100.0 * (1 - stats.cycles / naive_cycles), 2) if naive_cycles else 0.0,
        "axi_bursts": stats.axi_bursts,
        # Metadata RAM the scheme needs on-chip: 128 bits per delta operation.
        "metadata_bytes": 16 * (stats.loads + stats.moves + stats.keeps
                                + stats.allocs + stats.zeros),
        "avg_stamp_bytes": int(sum(s.total_size for s in comp.stamps) / max(len(comp.stamps), 1)),
        "spad_util_pct": round(100.0 * sum(s.total_size for s in comp.stamps)
                               / max(len(comp.stamps), 1) / spad_bytes, 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "results" / "exp4_memory_management"))
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    sc = load_compiler()

    rows, limits = [], []
    total = len(LAYERS) * len(SPAD_KB) * len(ARRAYS)
    done = 0

    for name, *dims in LAYERS:
        for kb in SPAD_KB:
            for arr in ARRAYS:
                done += 1
                try:
                    row = run_point(sc, name, dims, kb * 1024, arr)
                    rows.append(row)
                    print(f"  [{done:3d}/{total}] {name:18s} {kb:3d}KB {arr[0]}x{arr[1]}  "
                          f"phases={row['phases']:4d}  reduction={row['reduction_pct']:5.1f}%")
                except ValueError as exc:
                    # A phase's working set exceeds the scratchpad. That is a
                    # real capacity limit of the configuration, not a failure.
                    limits.append({"layer": name, "spad_kb": kb,
                                   "array": f"{arr[0]}x{arr[1]}",
                                   "reason": str(exc).split("!")[0].strip()})
                    print(f"  [{done:3d}/{total}] {name:18s} {kb:3d}KB {arr[0]}x{arr[1]}  "
                          f"DOES NOT FIT")

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "sweep_stamp.csv", index=False)
    print(f"\nWrote {out_dir/'sweep_stamp.csv'}  ({len(df)} configurations)")

    if limits:
        dl = pd.DataFrame(limits)
        dl.to_csv(out_dir / "capacity_limits.csv", index=False)
        print(f"Wrote {out_dir/'capacity_limits.csv'}  ({len(dl)} infeasible points)")

    if len(df):
        print("\nOff-chip traffic reduction across the sweep:")
        print(f"  min {df.reduction_pct.min():.1f}%   "
              f"mean {df.reduction_pct.mean():.1f}%   "
              f"max {df.reduction_pct.max():.1f}%")
        print("\nBy scratchpad capacity:")
        print(df.groupby("spad_kb")["reduction_pct"].mean().round(1).to_string())


if __name__ == "__main__":
    main()
