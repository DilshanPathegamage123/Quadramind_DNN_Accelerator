#!/usr/bin/env python3
"""
choose_scheduler.py
===================
Analytical multi-DNN scheduler chooser CLI.  Ranks all 14 schedulers the
RTL implements (FIFO/LIFO/SJF/RR/PRI/EDF/LRU, SRTF/HRRN/MLQ/MLFQ, AI-MT,
BATCH-DNN, BATCH-DNN++) for a workload mix on a fixed array + memory
provision and prints the recommended scheduler plus the full ranked table.
No RTL and no synthesis is run per query.

Usage (from sim_framework/):
  PYTHONPATH=. python scripts/choose_scheduler.py --mix mix3 --array 8x8 \
      --mem 256KB --goal turnaround
  PYTHONPATH=. python scripts/choose_scheduler.py \
      --mix models/tiny_cnn,models/mnist_cnn --array 8x8 --goal weighted \
      --weights makespan=0.5,turnaround=0.3,wait=0.2

--mix accepts:
  * a named mix from scripts/workloads.py: mix1 .. mix6 (SCHED_EVAL_MIXES --
      the representative set: task counts 2/3/3/4/4/6, per-task model cost
      1,620 .. 131,412 cycles)
  * a comma-separated list of model dirs (models/tiny_cnn,models/mnist_cnn)
  * a JSON file: {"name":..., "tasks":[{"name":..., "layers":[...],
      "arrival":0, "priority":0, "deadline":1000}, ...]}

Column labels (see results/sched_chooser/SCHEDULER_CHOOSER_REPORT.md):
  makespan / turnaround / wait  -- MODEL (rank scores built on
      software_ref.estimate_cycles, which ranks; it does not predict cycles)
  LUT / FF / power / Fmax       -- MEASURED (Vivado 2025.2 OOC synthesis)
  throughput / energy           -- DERIVED (model cycles x measured Fmax,
      x measured dynamic power)
Schedulers that do not synthesise carry NO hardware number and are excluded
from hardware-based goals rather than being given a substitute value.
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
from pysim.scheduler_chooser import (GOALS, SCHEDULERS, build_tasks, choose,
                                     describe_tiebreak, goal_value,
                                     load_hw_table, ties_at_best, warm_up)

_LAYER_FIELDS = set(LayerConfig.__dataclass_fields__)


def _layer_from_dict(d: dict) -> LayerConfig:
    return LayerConfig(**{k: v for k, v in d.items() if k in _LAYER_FIELDS})


def _layers_from_model_dir(p: Path) -> list[LayerConfig]:
    cfgs = sorted(p.glob("layer_*/config.json"))
    if not cfgs:
        raise SystemExit(f"no layer_*/config.json under {p}")
    return [_layer_from_dict(json.load(open(c))) for c in cfgs]


def load_mix(spec: str) -> tuple[str, list, dict]:
    """Return (mix_name, [(task_name, layers)], extra_attrs)."""
    extra: dict = {}

    m = re.fullmatch(r"mix(\d+)", spec.strip().lower())
    if m:
        from scripts.workloads import (SCHED_EVAL_MIXES, EDGE_WORKLOADS,
                                       CLOUD_WORKLOADS)
        n = int(m.group(1))
        if not 1 <= n <= len(SCHED_EVAL_MIXES):
            raise SystemExit(
                f"unknown mix {spec!r}; available: "
                + ", ".join(f"mix{i} ({mx['name']}, {len(mx['dnns'])} tasks)"
                            for i, mx in enumerate(SCHED_EVAL_MIXES, 1)))
        mix = SCHED_EVAL_MIXES[n - 1]
        by_name = {w["name"]: w for w in EDGE_WORKLOADS + CLOUD_WORKLOADS}
        tasks = []
        for dnn in mix["dnns"]:
            if dnn not in by_name:
                raise SystemExit(f"workload {dnn!r} not found")
            tasks.append((dnn, list(by_name[dnn]["layers"])))
        return mix["label"], tasks, extra

    p = Path(spec)
    if p.is_file() and p.suffix == ".json":
        data = json.load(open(p))
        name = data.get("name", p.stem)
        tasks, arrivals, prios, deads = [], [], [], []
        for t in data["tasks"]:
            if "layers" in t:
                layers = [_layer_from_dict(d) for d in t["layers"]]
            elif "model_dir" in t:
                layers = _layers_from_model_dir(Path(t["model_dir"]))
            else:
                raise SystemExit("each task needs 'layers' or 'model_dir'")
            tasks.append((t.get("name", f"task{len(tasks)}"), layers))
            arrivals.append(t.get("arrival", 0))
            prios.append(t.get("priority", len(prios)))
            deads.append(t.get("deadline", 1000 * (len(deads) + 1)))
        if any(a for a in arrivals):
            extra["arrivals"] = arrivals
        extra["priorities"] = prios
        extra["deadlines"] = deads
        return name, tasks, extra

    tasks = []
    for part in spec.split(","):
        d = Path(part.strip())
        if not d.is_dir():
            raise SystemExit(f"not a model directory: {d}")
        tasks.append((d.name, _layers_from_model_dir(d)))
    if not tasks:
        raise SystemExit("--mix produced no tasks")
    return "+".join(n for n, _ in tasks), tasks, extra


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
        if k.strip() not in ("makespan", "turnaround", "wait"):
            raise SystemExit(f"unknown weight key {k!r}")
        out[k.strip()] = float(v)
    return out


def _fmt(v, spec="", dash="--"):
    return dash if v is None else format(v, spec)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Analytical multi-DNN scheduler chooser: ranks all 14 "
                    "RTL schedulers (no RTL or synthesis run per query).")
    ap.add_argument("--mix", required=True,
                    help="mix1..mix6 | model dirs (comma-separated) | JSON")
    ap.add_argument("--array", default="8x8", help="array HxW (default 8x8)")
    ap.add_argument("--mem", default="256KB",
                    help="on-chip memory provision (default 256KB)")
    ap.add_argument("--dataflow", default="OS", choices=["OS", "IS", "WS"])
    ap.add_argument("--goal", default="makespan", choices=GOALS)
    ap.add_argument("--weights", default=None,
                    help="weighted-goal weights: makespan=1,turnaround=1,wait=1")
    ap.add_argument("--schedulers", default=None,
                    help="comma-separated subset (default: all 14)")
    ap.add_argument("--data-width", type=int, default=16)
    ap.add_argument("--csv", default=None,
                    help="output CSV path (default results/sched_chooser/)")
    args = ap.parse_args()

    name, mix, extra = load_mix(args.mix)
    ah, aw = parse_array(args.array)
    parse_mem(args.mem)          # validated; see note printed below
    weights = parse_weights(args.weights) if args.weights else None
    subset = ([s.strip().upper() for s in args.schedulers.split(",")]
              if args.schedulers else None)
    if subset:
        for s in subset:
            if s not in SCHEDULERS:
                raise SystemExit(f"unknown scheduler {s!r}")

    import_secs = warm_up()
    tasks = build_tasks(mix, args.dataflow, ah, aw, **extra)
    best, ranked, excluded, secs = choose(tasks, subset, args.goal, weights)

    hw = load_hw_table()
    n_measured = sum(1 for r in hw.values() if r.get("status") == "ok")

    print(f"\nScheduler chooser -- mix={name} ({len(tasks)} DNN tasks), "
          f"array={ah}x{aw}, dataflow={args.dataflow}, goal={args.goal}")
    print(f"Model libraries loaded in {import_secs*1e3:.0f} ms (one-time per "
          f"process); scored {len(ranked)+len(excluded)} schedulers "
          f"analytically in {secs*1e3:.1f} ms (no RTL, no synthesis).")
    print(f"Hardware columns: {n_measured}/{len(SCHEDULERS)} schedulers have "
          f"measured Vivado synthesis results.\n")

    if best is None:
        print(f"NO scheduler can be ranked on --goal {args.goal}: every "
              f"candidate lacks the measured value this goal needs.")
    else:
        print(f"RECOMMENDED: {best.scheduler}")
        print(f"  dispatch order    : {'->'.join('T%d' % t for t in best.order)}")
        print(f"  makespan          : {best.makespan:,} cycles  (model rank -- "
              f"not a cycle prediction)")
        print(f"  mean turnaround   : {best.mean_turnaround:,.0f} cycles  (model)")
        print(f"  mean wait         : {best.mean_wait:,.0f} cycles  (model)")
        if best.luts is not None:
            print(f"  area              : {best.luts:,} LUT / {best.ffs:,} FF  "
                  f"(measured, Vivado)")
        if best.power_dynamic_w is not None:
            print(f"  dynamic power     : {best.power_dynamic_w:.3f} W  "
                  f"(measured, Vivado vectorless)")
        if best.fmax_mhz is not None:
            print(f"  Fmax              : {best.fmax_mhz:,.1f} MHz  "
                  f"(measured, post-synthesis estimate)")
        if best.mean_turnaround_us is not None:
            print(f"  turnaround (real) : {best.mean_turnaround_us:,.1f} us  "
                  f"(derived: model cycles / measured Fmax)")
        if best.throughput_tasks_per_s is not None:
            print(f"  throughput        : {best.throughput_tasks_per_s:,.1f} "
                  f"tasks/s  (derived: model cycles / measured Fmax)")

        if best.hw_status == "unavailable":
            print(f"\n  *** WARNING: {best.scheduler} wins on --goal "
                  f"{args.goal}, but it DOES NOT SYNTHESISE and therefore "
                  f"cannot be built on this target. ***")
            print(f"      Reason: {best.hw_note}")
            buildable = next((s for s in ranked if s.hw_status == "ok"), None)
            if buildable:
                print(f"      Best synthesisable alternative: "
                      f"{buildable.scheduler} "
                      f"(mean turnaround {buildable.mean_turnaround:,.0f} "
                      f"cycles, {buildable.luts:,} LUT, "
                      f"{buildable.fmax_mhz:,.1f} MHz).")
        elif best.hw_status != "ok":
            print(f"\n  NOTE: no synthesis result exists for "
                  f"{best.scheduler}; its hardware columns are blank rather "
                  f"than estimated. Run scripts/synth_scheduler_hw.py.")

        if args.goal == "makespan":
            print("\n  WARNING: makespan cannot distinguish schedulers on "
                  "this accelerator.  A single machine that never idles "
                  "while work is queued finishes at the same time under "
                  "every order, so this goal is provably an all-way tie "
                  "(measured hardware agrees: 13,412 vs 13,413 cycles "
                  "across five schedulers).  Use --goal turnaround or wait "
                  "for scheduling quality, or --goal area / power for "
                  "measured hardware cost.")

        if args.goal == "throughput":
            print("\n  NOTE: throughput here is tasks / (makespan / Fmax). "
                  "Makespan is invariant across schedulers on this "
                  "accelerator (see --goal makespan), and the task count is "
                  "fixed, so this goal reduces exactly to ranking by "
                  "MEASURED Fmax -- it selects the scheduler with the "
                  "fastest clock, not the one with the best dispatch order. "
                  "Use --goal turnaround_us for latency the ordering "
                  "actually affects.")

        tied = ties_at_best(ranked, args.goal)
        if len(tied) > 1:
            print(f"\n  NOTE: {len(tied)} schedulers tie exactly at "
                  f"{goal_value(best, args.goal):,.0f} on --goal {args.goal}: "
                  + ", ".join(s.scheduler for s in tied))
            print(f"  Tie {describe_tiebreak(tied)}.")

    if excluded:
        print(f"\n  EXCLUDED from --goal {args.goal} "
              f"({len(excluded)} scheduler(s)) -- no measured value exists, "
              f"and none was substituted:")
        for s in excluded:
            print(f"    {s.scheduler}: {s.hw_note or s.hw_status}")
    print()

    hdr = (f"{'#':>3} {'scheduler':<12} {'order':<10} {'turnaround':>11} "
           f"{'wait':>10} {'real us':>10} {'tasks/s':>9} {'LUT':>7} "
           f"{'FF':>7} {'dyn W':>7} {'Fmax MHz':>9}")
    print(hdr)
    print("-" * len(hdr))
    for i, s in enumerate(ranked, 1):
        order = "->".join(str(t) for t in s.order)
        print(f"{i:>3} {s.scheduler:<12} {order[:10]:<10} "
              f"{s.mean_turnaround:>11,.0f} {s.mean_wait:>10,.0f} "
              f"{_fmt(s.mean_turnaround_us, ',.1f'):>10} "
              f"{_fmt(s.throughput_tasks_per_s, ',.0f'):>9} "
              f"{_fmt(s.luts, ',d'):>7} {_fmt(s.ffs, ',d'):>7} "
              f"{_fmt(s.power_dynamic_w, '.3f'):>7} "
              f"{_fmt(s.fmax_mhz, ',.1f'):>9}")
    print(f"\n(makespan is {ranked[0].makespan:,} cycles for every scheduler "
          f"-- provably invariant on a single work-conserving machine.)")

    csv_path = Path(args.csv).expanduser().resolve() if args.csv else (
        ROOT / "results/sched_chooser"
        / f"ranked_{re.sub(r'[^A-Za-z0-9]+', '_', name)}_{args.goal}.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["rank", "scheduler", "dispatch_order", "makespan_cycles",
                    "mean_turnaround_cycles", "mean_wait_cycles",
                    "max_turnaround_cycles", "max_wait_cycles",
                    "luts", "ffs", "power_dynamic_w", "fmax_mhz_post_synth",
                    "mean_turnaround_us", "throughput_tasks_per_s", "energy_uJ", "weighted",
                    "hw_status", "timing_source", "hw_source", "note"])
        for i, s in enumerate(ranked + excluded, 1):
            w.writerow([
                i if s in ranked else "excluded", s.scheduler,
                "->".join(str(t) for t in s.order), s.makespan,
                f"{s.mean_turnaround:.1f}", f"{s.mean_wait:.1f}",
                s.max_turnaround, s.max_wait,
                _fmt(s.luts, "d", ""), _fmt(s.ffs, "d", ""),
                _fmt(s.power_dynamic_w, ".3f", ""),
                _fmt(s.fmax_mhz, ".1f", ""),
                _fmt(s.mean_turnaround_us, ".2f", ""), _fmt(s.throughput_tasks_per_s, ".1f", ""),
                _fmt(s.energy_uJ, ".3f", ""),
                f"{s.weighted:.4f}", s.hw_status,
                "model", "measured (Vivado 2025.2 OOC)", s.hw_note,
            ])
    try:
        shown = csv_path.relative_to(ROOT)
    except ValueError:
        shown = csv_path
    print(f"\nRanked table exported: {shown}")
    print("Note: --mem is recorded for provenance; it does not change the "
          "ranking, because MT/CT overlap is deliberately not modelled "
          "(see the report's 'not modelled' section).")


if __name__ == "__main__":
    main()
