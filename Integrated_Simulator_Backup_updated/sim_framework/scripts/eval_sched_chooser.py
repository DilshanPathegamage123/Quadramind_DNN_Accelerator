#!/usr/bin/env python3
"""
eval_sched_chooser.py
=====================
Evaluation and verification for the multi-DNN scheduler chooser.

Five checks, every number either measured or model, none invented:

  (a) Decision accuracy vs exhaustive re-scoring.  The chooser IS
      exhaustive over 14 schedulers, so this verifies argmin/sort
      consistency and determinism -- not a heuristic's luck.  Stated
      plainly, as in the config-chooser's evaluation.
  (b) Anchor A -- dispatch order against the five MEASURED golden runs
      (results/golden_check/raw/multi_*.json).  Replays the exact synthetic
      task attributes the golden harness declares, because those (not the
      real cycle costs) are what the RTL schedulers decide on.
  (c) Anchor B -- makespan flatness.  The measured runs differ by ONE cycle
      across all five schedulers; the model must reproduce that invariance
      rather than predicting a speedup.  This is the check that would catch
      a fabricated performance claim.
  (d) Sensitivity -- does the recommendation actually depend on the
      workload and goal?  A chooser that always returns the same scheduler
      is the hardcoded-constant failure mode reappearing.
  (e) Speed -- warm scoring vs one-time imports vs cold end-to-end,
      measured separately (the config-chooser's Issue 3 discipline).

Usage (from sim_framework/):
    PYTHONPATH=. python scripts/eval_sched_chooser.py
"""
from __future__ import annotations

import csv
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pysim.scheduler_chooser import (GOALS, SCHEDULERS, Task, build_tasks,
                                     goal_value, load_hw_table,
                                     rank_schedulers, simulate, warm_up)

RAW = ROOT / "results/golden_check/raw"
OUT = ROOT / "results/sched_chooser"

# The golden multi-DNN harness (tb/golden/test_golden_multi.py) declares
# these synthetic attributes -- NOT the real cycle costs.  The RTL
# schedulers decide on them, so the anchor replay must use them verbatim.
GOLDEN_BURSTS = [10, 20, 30]        # 10 * (tid + 1)
GOLDEN_PRIOS = [0, 1, 2]            # tid
GOLDEN_DEADLINES = [1000, 2000, 3000]   # 1000 * (tid + 1)
GOLDEN_MEASURED = ["FIFO", "LIFO", "AIMT", "BATCHDNN", "BATCHDNN_PP"]

MIXES = ["mix1", "mix2", "mix3", "mix4"]
MODEL_GOALS = ["makespan", "turnaround", "wait", "weighted"]
# area/power/throughput need measured synthesis results; they are evaluated
# too, but only over the schedulers that actually have them.
HW_GOALS = ["area", "power", "throughput", "turnaround_us"]


def _load_mix(spec):
    from scripts.choose_scheduler import load_mix
    return load_mix(spec)


def _golden_tasks():
    """The golden 3-task mix with the harness's declared attributes."""
    from pysim.sim_config import LayerConfig
    names = ["models/tiny_cnn/layer_00", "models/mnist_cnn/layer_00",
             "models/tiny_cnn/layer_01"]
    mix = []
    for rel in names:
        cfg = json.loads((ROOT / rel / "config.json").read_text())
        fields = set(LayerConfig.__dataclass_fields__)
        mix.append((rel, [LayerConfig(**{k: v for k, v in cfg.items()
                                         if k in fields})]))
    return build_tasks(mix, "OS", 8, 8, priorities=GOLDEN_PRIOS,
                       deadlines=GOLDEN_DEADLINES, burst_times=GOLDEN_BURSTS)


# ---------------------------------------------------------------------------
# (a) decision accuracy + (d) sensitivity
# ---------------------------------------------------------------------------

def eval_accuracy_and_sensitivity():
    rows, sens = [], []
    hw = load_hw_table()
    has_hw = any(r.get("status") == "ok" for r in hw.values())
    goals = MODEL_GOALS + (HW_GOALS if has_hw else [])
    for mix_spec in MIXES:
        name, mix, extra = _load_mix(mix_spec)
        tasks = build_tasks(mix, "OS", 8, 8, **extra)
        for goal in goals:
            ranked, excluded = rank_schedulers(tasks, None, goal, hw=hw)
            if not ranked:
                rows.append({
                    "mix": name, "goal": goal, "pick": "NONE",
                    "pick_value": "", "true_best_value": "", "match": True,
                    "n_tied_at_best": 0, "n_ranked": 0,
                    "n_excluded": len(excluded),
                    "source": "model" if goal in MODEL_GOALS else "measured",
                })
                continue
            pick = ranked[0]
            # independent exhaustive re-scoring (throughput is maximised)
            vals = [goal_value(s, goal) for s in ranked]
            best_val = max(vals) if goal == "throughput" else min(vals)
            match = abs(goal_value(pick, goal) - best_val) < 1e-9
            n_tied = sum(1 for s in ranked
                         if abs(goal_value(s, goal) - best_val) < 1e-9)
            rows.append({
                "mix": name, "goal": goal, "pick": pick.scheduler,
                "pick_value": f"{goal_value(pick, goal):.2f}",
                "true_best_value": f"{best_val:.2f}",
                "match": match, "n_tied_at_best": n_tied,
                "n_ranked": len(ranked), "n_excluded": len(excluded),
                "source": ("model" if goal in MODEL_GOALS
                           else "measured (Vivado) / derived"),
            })
            sens.append({"mix": name, "goal": goal, "pick": pick.scheduler})
    return rows, sens


# ---------------------------------------------------------------------------
# (b) anchor A -- dispatch order vs measured RTL
# ---------------------------------------------------------------------------

def eval_anchor_order():
    tasks = _golden_tasks()
    rows = []
    for sched in GOLDEN_MEASURED:
        raw = RAW / f"multi_{sched}_8x8.json"
        if not raw.exists():
            rows.append({"scheduler": sched, "measured_order": "MISSING",
                         "model_order": "", "match": False,
                         "measured_cycles": "", "source": "measured (RTL)"})
            continue
        data = json.loads(raw.read_text())
        # measured order = first dispatch of each distinct task, in order
        seen, meas = set(), []
        for d in data["dispatch_order"]:
            if d["task"] not in seen:
                seen.add(d["task"])
                meas.append(d["task"])
        model = simulate(tasks, sched)["order"]
        rows.append({
            "scheduler": sched,
            "measured_order": "->".join(f"T{t}" for t in meas),
            "model_order": "->".join(f"T{t}" for t in model),
            "match": meas == model,
            "measured_cycles": data["total_cycles"],
            "source": "measured (RTL) vs model",
        })
    return rows


# ---------------------------------------------------------------------------
# (c) anchor B -- makespan flatness
# ---------------------------------------------------------------------------

def eval_anchor_flatness():
    tasks = _golden_tasks()
    measured = {}
    for sched in GOLDEN_MEASURED:
        raw = RAW / f"multi_{sched}_8x8.json"
        if raw.exists():
            measured[sched] = json.loads(raw.read_text())["total_cycles"]
    model = {s: simulate(tasks, s)["makespan"] for s in SCHEDULERS}

    def spread(d):
        v = list(d.values())
        return (max(v) - min(v)) / max(min(v), 1) * 100.0

    rows = [{
        "quantity": "measured total cycles (5 schedulers, RTL)",
        "min": min(measured.values()) if measured else "",
        "max": max(measured.values()) if measured else "",
        "spread_pct": f"{spread(measured):.4f}" if measured else "",
        "source": "measured (RTL)",
    }, {
        "quantity": "model makespan (14 schedulers)",
        "min": min(model.values()), "max": max(model.values()),
        "spread_pct": f"{spread(model):.4f}",
        "source": "model",
    }]
    # the check itself: the model must not invent a speedup the hardware
    # does not show
    meas_spread = spread(measured) if measured else 0.0
    model_spread = spread(model)
    verdict = "PASS" if model_spread <= max(meas_spread, 0.01) + 1e-9 else "FAIL"
    rows.append({"quantity": "flatness check (model spread <= measured)",
                 "min": "", "max": "", "spread_pct": verdict,
                 "source": "derived"})
    return rows, verdict


# ---------------------------------------------------------------------------
# (e) speed
# ---------------------------------------------------------------------------

def eval_speed():
    hw = load_hw_table()
    name, mix, extra = _load_mix("mix3")
    tasks = build_tasks(mix, "OS", 8, 8, **extra)

    reps = 5
    warm = []
    for _ in range(reps):
        t0 = time.perf_counter()
        rank_schedulers(tasks, None, "turnaround", hw=hw)
        warm.append(time.perf_counter() - t0)

    all_mixes = []
    t0 = time.perf_counter()
    for spec in MIXES:
        _, m, ex = _load_mix(spec)
        rank_schedulers(build_tasks(m, "OS", 8, 8, **ex), None, "turnaround",
                        hw=hw)
    all_mixes.append(time.perf_counter() - t0)

    cold = []
    for _ in range(3):
        t0 = time.perf_counter()
        subprocess.run(
            [sys.executable, "scripts/choose_scheduler.py", "--mix", "mix3",
             "--goal", "turnaround", "--csv",
             str(OUT / "_speed_probe.csv")],
            cwd=ROOT, capture_output=True,
            env={**__import__("os").environ, "PYTHONPATH": str(ROOT)})
        cold.append(time.perf_counter() - t0)
    probe = OUT / "_speed_probe.csv"
    if probe.exists():
        probe.unlink()

    return [
        {"what": "WARM scoring: 14 schedulers, one mix (median of 5; "
                 "EXCLUDES one-time imports)",
         "seconds": f"{statistics.median(warm):.4f}", "source": "measured"},
        {"what": "WARM: all 4 mixes x 14 schedulers",
         "seconds": f"{all_mixes[0]:.4f}", "source": "measured"},
        {"what": "COLD CLI end-to-end (interpreter + imports + scoring + "
                 "table + CSV; median of 3 subprocesses)",
         "seconds": f"{statistics.median(cold):.4f}", "source": "measured"},
        {"what": "Vivado synthesis per scheduler (cached, NOT per query)",
         "seconds": "~135", "source": "measured (synth_scheduler_hw.py)"},
    ]


def _save(rows, path, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields or list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {path.relative_to(ROOT)}")


def main() -> None:
    imports = warm_up()
    print(f"Model libraries loaded in {imports*1e3:.0f} ms\n")

    print("(a)+(d) decision accuracy and sensitivity")
    acc, sens = eval_accuracy_and_sensitivity()
    n_ok = sum(1 for r in acc if r["match"])
    print(f"  decision accuracy: {n_ok}/{len(acc)} "
          f"({100.0*n_ok/len(acc):.0f} %)")
    picks = {}
    for s in sens:
        picks.setdefault(s["pick"], 0)
        picks[s["pick"]] += 1
    print(f"  recommendation spread: "
          + ", ".join(f"{k} x{v}" for k, v in sorted(picks.items(),
                                                     key=lambda kv: -kv[1])))
    _save(acc, OUT / "eval_decision_accuracy.csv")
    _save(sens, OUT / "eval_sensitivity.csv")

    print("\n(b) anchor A -- dispatch order vs measured RTL")
    anch = eval_anchor_order()
    n_match = sum(1 for r in anch if r["match"])
    for r in anch:
        print(f"  {r['scheduler']:<12} measured {r['measured_order']:<12} "
              f"model {r['model_order']:<12} "
              f"{'MATCH' if r['match'] else 'MISMATCH'}")
    print(f"  => {n_match}/{len(anch)} exact")
    _save(anch, OUT / "eval_anchor_order.csv")

    print("\n(c) anchor B -- makespan flatness")
    flat, verdict = eval_anchor_flatness()
    for r in flat:
        print(f"  {r['quantity']:<48} {r['min']} .. {r['max']}  "
              f"{r['spread_pct']}")
    print(f"  => {verdict}")
    _save(flat, OUT / "eval_anchor_flatness.csv")

    print("\n(e) speed")
    sp = eval_speed()
    for r in sp:
        print(f"  {r['seconds']:>10} s  {r['what']}")
    _save(sp, OUT / "eval_speed.csv")

    print("\nEvaluation complete.")


if __name__ == "__main__":
    main()
