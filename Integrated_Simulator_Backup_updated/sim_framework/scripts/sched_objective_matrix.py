#!/usr/bin/env python3
"""
sched_objective_matrix.py
=========================
Sweep the analytical scheduler chooser over EVERY optimisation objective x
EVERY representative workload mix, and reduce the result to the deliverable
the framework exists to produce:

    "given this optimisation objective, use this scheduler"

Why a sweep and not a single query
----------------------------------
choose_scheduler.py answers one (mix, goal) question.  A recommendation
backed by one mix is not evidence: a scheduler can win on a 3-task cloud
queue and lose on a 6-task mixed queue.  This script runs all of them and
reports, per objective, whether the winner is STABLE across the mixes or
whether it depends on the workload -- which is itself a finding, not a
failure.

What is measured and what is modelled
-------------------------------------
Unchanged from pysim/scheduler_chooser.py: timing columns are MODEL rank
scores, LUT/FF/power/Fmax are MEASURED (Vivado OOC), throughput and
turnaround_us are DERIVED from the two.  Schedulers with no measured value
are EXCLUDED from hardware-based objectives, never given a substitute.

Default objective set
---------------------
turnaround, turnaround_us, wait, throughput, area, power.

`makespan` and `weighted` are excluded by default and must be asked for
with --goals: makespan is a provable all-way tie on a single
work-conserving machine (so its "winner" is decided by the tie-break, not
by scheduling), and `weighted` is a composite whose answer is a function of
--weights rather than of the hardware.

Usage (from sim_framework/):
  PYTHONPATH=. python scripts/sched_objective_matrix.py
  PYTHONPATH=. python scripts/sched_objective_matrix.py --array 16x16
  PYTHONPATH=. python scripts/sched_objective_matrix.py --goals all
  PYTHONPATH=. python scripts/sched_objective_matrix.py --mixes mix1,mix3,mix6

Outputs (results/sched_chooser/ by default):
  objective_matrix.csv          objective x mix -> winner, with metrics
  objective_recommendation.csv  objective -> recommended scheduler
  objective_matrix.md           both tables, for pasting into the report
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pysim.scheduler_chooser import (GOALS, SCHEDULERS, build_tasks,
                                     goal_value, rank_schedulers,
                                     ties_at_best, warm_up)
from scripts.choose_scheduler import load_mix, parse_array

# Objectives worth sweeping.  See the module docstring for why makespan and
# weighted are opt-in rather than default.
DEFAULT_GOALS = ["turnaround", "turnaround_us", "wait", "throughput",
                 "area", "power"]

# One line per objective explaining what winning it actually means, so the
# recommendation table cannot be read as "this scheduler is simply best".
GOAL_MEANING = {
    "turnaround": "mean cycles from submission to completion (model)",
    "turnaround_us": "mean wall-clock latency = model cycles / measured Fmax",
    "wait": "mean cycles queued before first dispatch (model)",
    "throughput": "tasks/s; reduces to measured Fmax (makespan is invariant)",
    "area": "measured LUT count",
    "power": "measured Vivado vectorless dynamic power",
    "makespan": "total completion time -- provably an all-way tie here",
    "weighted": "composite of makespan/turnaround/wait, set by --weights",
}


def parse_goals(spec: str | None) -> list[str]:
    if not spec:
        return list(DEFAULT_GOALS)
    if spec.strip().lower() == "all":
        return list(GOALS)
    out = []
    for part in spec.split(","):
        g = part.strip()
        if g not in GOALS:
            raise SystemExit(f"unknown goal {g!r}; choose from {GOALS}")
        out.append(g)
    return out


def parse_mixes(spec: str | None) -> list[str]:
    if not spec:
        from scripts.workloads import SCHED_EVAL_MIXES
        return [f"mix{i}" for i in range(1, len(SCHED_EVAL_MIXES) + 1)]
    return [s.strip() for s in spec.split(",") if s.strip()]


def _fmt_goal(goal: str, v: float) -> str:
    """Render a goal metric with units, so the CSV is readable standalone."""
    if v is None or v != v:                      # None / NaN
        return ""
    if goal in ("turnaround", "wait", "makespan"):
        return f"{v:,.0f} cyc"
    if goal == "turnaround_us":
        return f"{v:,.1f} us"
    if goal == "throughput":
        return f"{v:,.0f} tasks/s"
    if goal == "area":
        return f"{v:,.0f} LUT"
    if goal == "power":
        return f"{v:.3f} W"
    return f"{v:,.3f}"


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Sweep the analytical scheduler chooser over every "
                    "objective x every representative workload mix.")
    ap.add_argument("--mixes", default=None,
                    help="comma-separated mix specs (default: all 6 in "
                         "SCHED_EVAL_MIXES)")
    ap.add_argument("--goals", default=None,
                    help=f"comma-separated goals, or 'all'. "
                         f"default: {','.join(DEFAULT_GOALS)}")
    ap.add_argument("--array", default="8x8", help="array HxW (default 8x8)")
    ap.add_argument("--dataflow", default="OS", choices=["OS", "IS", "WS"])
    ap.add_argument("--weights", default=None,
                    help="weights for --goals weighted (see choose_scheduler)")
    ap.add_argument("--outdir", default=None,
                    help="output directory (default results/sched_chooser/)")
    args = ap.parse_args()

    goals = parse_goals(args.goals)
    mix_specs = parse_mixes(args.mixes)
    ah, aw = parse_array(args.array)
    weights = None
    if args.weights:
        from scripts.choose_scheduler import parse_weights
        weights = parse_weights(args.weights)

    import_secs = warm_up()

    # Build each mix's task list ONCE and reuse it across every objective:
    # the tasks do not depend on the goal, only the ranking does.  This is
    # also what makes the per-query cost honest to report.
    mixes = []
    for spec in mix_specs:
        name, mix, extra = load_mix(spec)
        tasks = build_tasks(mix, args.dataflow, ah, aw, **extra)
        mixes.append((spec, name, tasks))

    print(f"\nScheduler objective matrix -- {len(goals)} objectives x "
          f"{len(mixes)} mixes, array={ah}x{aw}, dataflow={args.dataflow}")
    print(f"Model libraries loaded in {import_secs*1e3:.0f} ms (one-time). "
          f"No RTL and no synthesis is run.\n")

    print("Workload mixes swept:")
    for spec, name, tasks in mixes:
        costs = "/".join(f"{t.service:,}" for t in tasks)
        print(f"  {spec:<6} {name:<22} {len(tasks)} tasks   "
              f"model cycles: {costs}")
    print()

    # ---- sweep --------------------------------------------------------
    import time
    rows = []                      # one per (goal, mix)
    tiedsets: dict[str, list[set]] = {g: [] for g in goals}
    luts: dict[str, int | None] = {}
    total_secs = 0.0
    for goal in goals:
        for spec, name, tasks in mixes:
            t0 = time.perf_counter()
            ranked, excluded = rank_schedulers(tasks, None, goal, weights)
            total_secs += time.perf_counter() - t0
            for s in ranked:
                luts.setdefault(s.scheduler, s.luts)
            if not ranked:
                rows.append({"goal": goal, "mix": spec, "mix_name": name,
                             "n_tasks": len(tasks), "winner": "",
                             "tied_with": "", "value": "", "runner_up": "",
                             "excluded": ";".join(s.scheduler
                                                  for s in excluded)})
                continue
            best = ranked[0]
            tied = [s.scheduler for s in ties_at_best(ranked, goal)]
            tiedsets[goal].append(set(tied))
            runner = next((s.scheduler for s in ranked[1:]
                           if s.scheduler not in tied), "")
            rows.append({
                "goal": goal, "mix": spec, "mix_name": name,
                "n_tasks": len(tasks),
                "winner": best.scheduler,
                "tied_with": ";".join(t for t in tied
                                      if t != best.scheduler),
                "value": _fmt_goal(goal, goal_value(best, goal)),
                "runner_up": runner,
                "excluded": ";".join(s.scheduler for s in excluded),
            })

    print(f"Scored {len(goals)*len(mixes)*len(SCHEDULERS):,} "
          f"(scheduler, mix, objective) combinations in "
          f"{total_secs*1e3:.1f} ms total.\n")

    # ---- matrix table --------------------------------------------------
    by = {(r["goal"], r["mix"]): r for r in rows}
    mix_cols = [spec for spec, _, _ in mixes]
    w_goal = max(len("objective"), max(len(g) for g in goals))
    hdr = f"{'objective':<{w_goal}} " + " ".join(f"{m:>10}" for m in mix_cols)
    print("WINNER PER (objective, mix)")
    print(hdr)
    print("-" * len(hdr))
    for goal in goals:
        cells = []
        for m in mix_cols:
            r = by[(goal, m)]
            mark = "*" if r["tied_with"] else ""
            cells.append(f"{(r['winner'] or '--') + mark:>10}")
        print(f"{goal:<{w_goal}} " + " ".join(cells))
    print("\n* = tied at the top on this objective; the printed name is the "
          "deterministic tie-break winner, not a strictly better scheduler.")

    # ---- recommendation per objective ----------------------------------
    #
    # The winner row above names ONE scheduler per cell, but most cells are
    # ties: several policies produce an identical dispatch order and are
    # therefore exactly equal on the objective.  Counting those single names
    # across mixes would manufacture a disagreement that does not exist --
    # mix1 reporting HRRN and mix3 reporting SJF can mean the very same set
    # of policies was optimal in both, with a different alphabetical
    # representative printed.
    #
    # So the recommendation is taken over TIED SETS, not over winner names:
    # a scheduler is recommended when it sits in the tied-at-best set for
    # EVERY mix swept.  Only when that intersection is empty is the answer
    # genuinely workload-dependent, and the script says so.
    #
    # Within the co-optimal set the objective itself cannot discriminate
    # (that is what co-optimal means), so the pick falls to MEASURED area --
    # of the policies that are all equally good at the goal, build the
    # cheapest.  Schedulers with no measured area sort last; name breaks
    # anything still level, mirroring rank_schedulers' final key.
    print("\n\nOBJECTIVE -> RECOMMENDED SCHEDULER")
    reco_rows = []
    w_sched = 12

    def _hw_key(s: str):
        return (luts.get(s) is None, luts.get(s) or 0, s)

    hdr2 = (f"{'objective':<{w_goal}} {'scheduler':<{w_sched}} "
            f"{'optimal on':>10}  {'stability':<20} "
            f"what the objective ranks on")
    print(hdr2)
    print("-" * len(hdr2))
    for goal in goals:
        tsets = tiedsets[goal]
        if not tsets:
            continue
        n_mix = len(tsets)
        always = set.intersection(*tsets)
        if always:
            pick = sorted(always, key=_hw_key)[0]
            stability = f"optimal on all {n_mix}"
            co_opt = sorted(always, key=_hw_key)
        else:
            # Genuinely workload-dependent: fall back to the scheduler that
            # is co-optimal on the most mixes.
            counts = Counter(s for ts in tsets for s in ts)
            top_n = max(counts.values())
            pick = sorted((s for s, c in counts.items() if c == top_n),
                          key=_hw_key)[0]
            stability = "workload-dependent"
            co_opt = sorted((s for s, c in counts.items() if c == top_n),
                            key=_hw_key)
        optimal_on = sum(1 for ts in tsets if pick in ts)
        reco_rows.append({
            "goal": goal, "recommended": pick,
            "optimal_on": f"{optimal_on}/{n_mix}",
            "stability": stability,
            "co_optimal_set": ";".join(co_opt),
            "picked_by": ("only candidate" if len(co_opt) == 1 else
                          f"lowest measured area among {len(co_opt)} "
                          f"co-optimal policies"),
            "meaning": GOAL_MEANING.get(goal, ""),
        })
        print(f"{goal:<{w_goal}} {pick:<{w_sched}} "
              f"{optimal_on}/{n_mix:<8}  {stability:<20} "
              f"{GOAL_MEANING.get(goal, '')}")

    print("\nHow to read this: a scheduler is recommended when it is in the "
          "tied-at-best set for every mix swept, not when its name won the "
          "most cells above.")

    multi = [r for r in reco_rows if ";" in r["co_optimal_set"]]
    if multi:
        print("\nCO-OPTIMAL SETS -- these policies are exactly equal on the "
              "objective; the pick is the cheapest to build, and any other "
              "member is an equally valid answer:")
        for r in multi:
            members = r["co_optimal_set"].split(";")
            shown = ", ".join(f"{s} ({luts[s]:,} LUT)" if luts.get(s)
                              else f"{s} (no measured area)"
                              for s in members)
            print(f"  {r['goal']:<{w_goal}} {shown}")

    dep = [r for r in reco_rows if r["stability"] == "workload-dependent"]
    if dep:
        print("\nWORKLOAD-DEPENDENT -- no single scheduler is optimal on "
              "every mix for these objectives, so the recommendation is a "
              "majority and the mix matters:")
        for r in dep:
            cells = ", ".join(f"{m}:{by[(r['goal'], m)]['winner']}"
                              for m in mix_cols)
            print(f"  {r['goal']:<{w_goal}} {cells}")

    # ---- exports -------------------------------------------------------
    outdir = (Path(args.outdir).expanduser().resolve() if args.outdir
              else ROOT / "results/sched_chooser")
    outdir.mkdir(parents=True, exist_ok=True)

    m_csv = outdir / "objective_matrix.csv"
    with open(m_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "goal", "mix", "mix_name", "n_tasks", "winner", "tied_with",
            "value", "runner_up", "excluded"])
        w.writeheader()
        w.writerows(rows)

    r_csv = outdir / "objective_recommendation.csv"
    with open(r_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "goal", "recommended", "optimal_on", "stability",
            "co_optimal_set", "picked_by", "meaning"])
        w.writeheader()
        w.writerows(reco_rows)

    md = outdir / "objective_matrix.md"
    with open(md, "w") as fh:
        fh.write(f"# Scheduler selection: objective x workload mix\n\n")
        fh.write(f"Array {ah}x{aw}, dataflow {args.dataflow}. "
                 f"{len(goals)} objectives x {len(mixes)} mixes, scored "
                 f"analytically in {total_secs*1e3:.1f} ms with no RTL "
                 f"simulation and no synthesis run.\n\n")
        fh.write("Timing columns are model rank scores; LUT/FF/power/Fmax "
                 "are measured (Vivado OOC); throughput and turnaround_us "
                 "are derived from both. Schedulers lacking a measured "
                 "value are excluded from hardware objectives, never "
                 "substituted.\n\n")
        fh.write("## Workload mixes\n\n")
        fh.write("| mix | name | tasks | per-task model cycles |\n")
        fh.write("|---|---|---|---|\n")
        for spec, name, tasks in mixes:
            fh.write(f"| {spec} | {name} | {len(tasks)} | "
                     f"{', '.join(f'{t.service:,}' for t in tasks)} |\n")
        fh.write("\n## Winner per (objective, mix)\n\n")
        fh.write("| objective | " + " | ".join(mix_cols) + " |\n")
        fh.write("|---" * (len(mix_cols) + 1) + "|\n")
        for goal in goals:
            cells = []
            for m in mix_cols:
                r = by[(goal, m)]
                cells.append((r["winner"] or "--")
                             + ("\\*" if r["tied_with"] else ""))
            fh.write(f"| {goal} | " + " | ".join(cells) + " |\n")
        fh.write("\n\\* tied at the top; name shown is the deterministic "
                 "tie-break winner.\n")
        fh.write("\n## Objective -> recommended scheduler\n\n")
        fh.write("A scheduler is recommended when it is in the tied-at-best "
                 "set for **every** mix swept. Where several policies are "
                 "co-optimal the objective cannot separate them, so the "
                 "pick is the one with the lowest measured area.\n\n")
        fh.write("The candidate-set column holds the co-optimal policies "
                 "when stability is *optimal on all N*; when stability is "
                 "*workload-dependent* no policy is optimal everywhere and "
                 "the column holds those optimal on the most mixes.\n\n")
        fh.write("| objective | recommended | optimal on | stability | "
                 "candidate set | what it ranks on |\n")
        fh.write("|---|---|---|---|---|---|\n")
        for r in reco_rows:
            fh.write(f"| {r['goal']} | **{r['recommended']}** | "
                     f"{r['optimal_on']} | {r['stability']} | "
                     f"{r['co_optimal_set'].replace(';', ', ')} | "
                     f"{r['meaning']} |\n")

    for p in (m_csv, r_csv, md):
        try:
            shown = p.relative_to(ROOT)
        except ValueError:
            shown = p
        print(f"\nExported: {shown}")


if __name__ == "__main__":
    main()
