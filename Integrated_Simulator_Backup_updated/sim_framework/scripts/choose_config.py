#!/usr/bin/env python3
"""
choose_config.py
================
Analytical configuration chooser CLI.  Scores all 27 combinations of
stationary scheme (OS/WS/IS) x memory layout (RM/CM/ChM) x casting scheme
(MULTICAST/UNICAST/HYBRID) with the validated analytical cost model
(pysim/config_chooser.py) and prints the recommended configuration plus the
full ranked table.  No RTL is run.

Usage (from sim_framework/):
  PYTHONPATH=. python scripts/choose_config.py \
      --workload models/tiny_cnn --array 8x8 --mem 256KB --goal offchip
  PYTHONPATH=. python scripts/choose_config.py \
      --workload my_layers.json --array 8x8 --mem 256KB --goal weighted \
      --weights offchip=0.5,latency=0.3,energy=0.2

--workload accepts either:
  * a model directory containing layer_XX/config.json files
    (e.g. models/tiny_cnn), or
  * a JSON file: {"name": ..., "layers": [{LayerConfig fields}, ...]}
    or a bare list of layer dicts.

The ranked table is exported as CSV (default: results/chooser/).
Column notes: off-chip elements is the primary metric (model); latency_rank
is a RANK score, not a cycle prediction (the estimator ranks configurations,
per results/golden_check/GOLDEN_CHECK_SUMMARY.md sec.7).
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

from pysim.sim_config import LayerConfig
from pysim.config_chooser import GOALS, choose, goal_value, ties_at_best

_LAYER_FIELDS = set(LayerConfig.__dataclass_fields__)


def _layer_from_dict(d: dict) -> LayerConfig:
    return LayerConfig(**{k: v for k, v in d.items() if k in _LAYER_FIELDS})


def load_workload(path: str) -> tuple[str, list[LayerConfig]]:
    p = Path(path)
    if p.is_dir():
        cfgs = sorted(p.glob("layer_*/config.json"))
        if not cfgs:
            raise SystemExit(f"no layer_*/config.json under {p}")
        return p.name, [_layer_from_dict(json.load(open(c))) for c in cfgs]
    data = json.load(open(p))
    if isinstance(data, dict):
        name = data.get("name", p.stem)
        layers = data["layers"]
    else:
        name, layers = p.stem, data
    return name, [_layer_from_dict(d) for d in layers]


def parse_array(s: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d+)x(\d+)", s.strip().lower())
    if not m:
        raise SystemExit(f"--array must look like 8x8, got {s!r}")
    return int(m.group(1)), int(m.group(2))


def parse_mem(s: str) -> int:
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(b|kb|mb|gb)?", s.strip().lower())
    if not m:
        raise SystemExit(f"--mem must look like 256KB / 1MB, got {s!r}")
    mult = {"b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3}[m.group(2) or "b"]
    return int(float(m.group(1)) * mult)


def parse_weights(s: str) -> dict:
    out = {}
    for part in s.split(","):
        k, _, v = part.partition("=")
        if k.strip() not in ("offchip", "latency", "energy"):
            raise SystemExit(f"unknown weight key {k!r}")
        out[k.strip()] = float(v)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Analytical configuration chooser: ranks all 27 "
                    "stationary x layout x casting combinations (no RTL run).")
    ap.add_argument("--workload", required=True,
                    help="model dir (models/tiny_cnn) or layer-shapes JSON")
    ap.add_argument("--array", default="8x8", help="array HxW (default 8x8)")
    ap.add_argument("--mem", default="256KB",
                    help="on-chip memory provision (default 256KB)")
    ap.add_argument("--goal", default="offchip", choices=GOALS)
    ap.add_argument("--weights", default=None,
                    help="weighted-goal weights: offchip=1,latency=1,energy=1")
    ap.add_argument("--data-width", type=int, default=16)
    ap.add_argument("--csv", default=None,
                    help="output CSV path (default results/chooser/)")
    args = ap.parse_args()

    name, layers = load_workload(args.workload)
    ah, aw = parse_array(args.array)
    mem_bytes = parse_mem(args.mem)
    weights = parse_weights(args.weights) if args.weights else None

    best, ranked, secs = choose(layers, ah, aw, mem_bytes, args.goal, weights,
                                args.data_width)

    print(f"\nConfiguration chooser -- workload={name} ({len(layers)} layers), "
          f"array={ah}x{aw}, mem={args.mem}, goal={args.goal}")
    print(f"Scored 27 combinations analytically in {secs*1e3:.1f} ms "
          f"(no RTL run).\n")
    print(f"RECOMMENDED: {best.dataflow} + {best.layout} + {best.casting}")
    print(f"  off-chip elements : {best.offchip_elements:,.0f}  (model)")
    print(f"  latency rank score: {best.latency_rank:,.0f}  "
          f"(rank only -- not a cycle prediction)")
    print(f"  energy            : {best.energy_pJ/1e6:,.2f} uJ  (model)")

    tied = ties_at_best(ranked, args.goal)
    if len(tied) > 1:
        print(f"\n  NOTE: {len(tied)} configurations tie exactly at "
              f"{goal_value(best, args.goal):,.0f} on --goal {args.goal}: "
              + ", ".join(s.label for s in tied))
        print("  Tie broken by latency rank, then energy "
              f"(latency ranks: "
              + ", ".join(f"{s.label} {s.latency_rank:,.0f}" for s in tied)
              + ").")
    print()

    hdr = (f"{'#':>3} {'config':<14} {'offchip elems':>14} "
           f"{'latency rank':>13} {'energy (uJ)':>12} {'weighted':>9}")
    print(hdr)
    print("-" * len(hdr))
    for i, s in enumerate(ranked, 1):
        print(f"{i:>3} {s.label:<14} {s.offchip_elements:>14,.0f} "
              f"{s.latency_rank:>13,.0f} {s.energy_pJ/1e6:>12,.2f} "
              f"{s.weighted:>9.3f}")

    csv_path = Path(args.csv).expanduser().resolve() if args.csv else (
        ROOT / "results/chooser" / f"ranked_{name}_{args.goal}.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(["rank", "dataflow", "mem_layout", "casting",
                      "offchip_elements", "offchip_bytes", "latency_rank",
                      "energy_pJ", "prefetch_beats", "weighted", "source"])
        for i, s in enumerate(ranked, 1):
            wtr.writerow([i, s.dataflow, s.layout, s.casting,
                          f"{s.offchip_elements:.0f}",
                          f"{s.offchip_bytes:.0f}",
                          f"{s.latency_rank:.0f}", f"{s.energy_pJ:.0f}",
                          f"{s.prefetch_beats:.0f}", f"{s.weighted:.4f}",
                          "model"])
    try:
        shown = csv_path.relative_to(ROOT)
    except ValueError:
        shown = csv_path
    print(f"\nRanked table exported: {shown}")


if __name__ == "__main__":
    main()
