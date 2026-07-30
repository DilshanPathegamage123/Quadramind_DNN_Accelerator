#!/usr/bin/env python3
"""
export_member3_dataset.py
=========================
Export the Member-3 (Multi-DNN scheduler module) dataset that
`member3_colab/member3_scheduler_analysis.py` consumes in Google Colab.

Every value written by this script is one of four kinds, and each CSV
carries the label in a `source` / `provenance` column:

  measured (Vivado)  LUT / FF / DSP / BRAM / power / WNS -> Fmax, read from
                     results/sched_chooser/hw/scheduler_hw.csv, produced by
                     scripts/synth_scheduler_hw.py from real out-of-context
                     synthesis on xc7a100tcsg324-1.
  measured (RTL)     dispatch order, per-task cycles and total cycles from
                     the recorded golden runs in
                     results/golden_check/raw/multi_*_8x8.json.
  model              queueing simulation in pysim/scheduler_chooser.py on
                     top of software_ref.estimate_cycles (a RANK score, not
                     an absolute cycle prediction).
  derived            arithmetic on the two above (wall-clock turnaround,
                     throughput, scheduler energy, Fmax-vs-assumption).

One extra file, 11_exp5_factor_model.csv, is copied from the older
experiment-5 output.  It is NOT measured -- it comes from the hardcoded
SCHEDULER_MODEL table in scripts/run_full_eval.py -- and is exported only
so the notebook can show, side by side, why the analytical chooser
replaced it.  Its provenance column says so on every row.

Nothing here is invented, interpolated or curve-fitted.

Usage (from sim_framework/):
    PYTHONPATH=. python scripts/export_member3_dataset.py
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # sim_framework/
sys.path.insert(0, str(ROOT))

REPO = ROOT.parent                                     # Integrated_Simulator_Backup_updated/
OUT = REPO / "member3_colab" / "data"

RESULTS = ROOT / "results"
SCHED = RESULTS / "sched_chooser"
GOLDEN_RAW = RESULTS / "golden_check" / "raw"

from pysim.scheduler_chooser import (GOALS, SCHEDULERS, build_tasks,   # noqa: E402
                                     goal_value, load_hw_table,
                                     rank_schedulers)
from pysim.software_ref import estimate_cycles                          # noqa: E402
from pysim.config_chooser import prefetch_traffic                       # noqa: E402
from scripts.choose_scheduler import load_mix                           # noqa: E402
from scripts.workloads import (WORKLOAD_MIXES, EDGE_WORKLOADS,          # noqa: E402
                               CLOUD_WORKLOADS)

MIX_SPECS = ["mix1", "mix2", "mix3", "mix4"]
ARRAY_H = ARRAY_W = 8
DATAFLOW = "OS"

# The five schedulers that have a recorded RTL golden run.
GOLDEN_MEASURED = ["FIFO", "LIFO", "AIMT", "BATCHDNN", "BATCHDNN_PP"]

# scripts/run_full_eval.py:80 -- the project-wide clock assumption that
# Finding 4 measured against.
ASSUMED_CLOCK_MHZ = 1000.0


def _write(rows: list[dict], name: str, fields: list[str] | None = None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    if not rows:
        print(f"  SKIP {name} (no rows)")
        return
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields or list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {path.relative_to(REPO)}  ({len(rows)} rows)")


def _copy(src: Path, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        print(f"  SKIP {name} (missing {src})")
        return
    shutil.copyfile(src, OUT / name)
    n = sum(1 for _ in open(OUT / name)) - 1
    print(f"  wrote {(OUT / name).relative_to(REPO)}  ({n} rows)")


# ---------------------------------------------------------------------------
# 01 -- scheduler inventory: what the RTL actually implements
# ---------------------------------------------------------------------------
# Family / module / select code come from rtl/schedulers/*.sv and
# pysim/sim_config.py:SCHEDULER_NAMES.  Preemptive flag is the complement of
# scheduler_chooser.NON_PREEMPTIVE (rtl/schedulers/task_scheduler.sv:91) for
# the basic family, and the RTL re-decide behaviour for the advanced family.
INVENTORY = [
    # select, name,          label,         family,     module,                        preemptive_rtl
    (0,  "FIFO",        "FIFO",        "Classical", "task_scheduler.sv",          False),
    (1,  "LIFO",        "LIFO",        "Classical", "task_scheduler.sv",          False),
    (2,  "SJF",         "SJF",         "Classical", "task_scheduler.sv",          False),
    (3,  "RR",          "Round-Robin", "Classical", "task_scheduler.sv",          True),
    (4,  "PRI",         "Priority",    "Classical", "task_scheduler.sv",          False),
    (5,  "EDF",         "EDF",         "Classical", "task_scheduler.sv",          False),
    (6,  "LRU",         "LRU",         "Classical", "task_scheduler.sv",          True),
    (7,  "SRTF",        "SRTF",        "Classical", "advanced_task_scheduler.sv", True),
    (8,  "HRRN",        "HRRN",        "Classical", "advanced_task_scheduler.sv", False),
    (9,  "MLQ",         "MLQ",         "Classical", "advanced_task_scheduler.sv", False),
    (10, "MLFQ",        "MLFQ",        "Classical", "advanced_task_scheduler.sv", True),
    (11, "AIMT",        "AI-MT",       "DNN-aware", "aimt_scheduler.sv",          False),
    (12, "BATCHDNN",    "BATCH-DNN",   "DNN-aware", "batchdnn_scheduler.sv",      False),
    (13, "BATCHDNN_PP", "BATCH-DNN++", "DNN-aware", "batchdnn_pp_scheduler.sv",   False),
]


def export_inventory() -> None:
    hw = load_hw_table()
    rows = []
    for sel, name, label, family, module, preempt in INVENTORY:
        src = ROOT / "rtl" / "schedulers" / module
        loc = sum(1 for _ in open(src)) if src.exists() else ""
        row = hw.get(name, {})
        rows.append({
            "select_code": sel,
            "scheduler": name,
            "label": label,
            "family": family,
            "rtl_module": f"rtl/schedulers/{module}",
            "rtl_lines": loc,
            "wrapper": ("multi_scheduler_wrapper.sv" if sel <= 10
                        else "dnn_scheduler_wrapper.sv"),
            "preemptive_in_rtl": preempt,
            "synthesis_status": row.get("status", "not attempted"),
            "has_golden_rtl_run": name in GOLDEN_MEASURED,
            "provenance": "RTL source + measured (Vivado) status",
        })
    _write(rows, "01_scheduler_inventory.csv")


# ---------------------------------------------------------------------------
# 02 -- measured Vivado synthesis table (verbatim copy)
# ---------------------------------------------------------------------------
def export_hw() -> None:
    _copy(SCHED / "hw" / "scheduler_hw.csv", "02_scheduler_hw_measured.csv")


# ---------------------------------------------------------------------------
# 03 -- full ranked tables: every mix x every goal x every scheduler
# ---------------------------------------------------------------------------
def export_ranked() -> None:
    hw = load_hw_table()
    rows = []
    for spec in MIX_SPECS:
        name, mix, extra = load_mix(spec)
        tasks = build_tasks(mix, DATAFLOW, ARRAY_H, ARRAY_W, **extra)
        for goal in GOALS:
            ranked, excluded = rank_schedulers(tasks, None, goal, hw=hw)
            for i, s in enumerate(ranked, 1):
                rows.append(_rank_row(spec, name, goal, i, s, len(tasks),
                                      excluded=False))
            for s in excluded:
                rows.append(_rank_row(spec, name, goal, "", s, len(tasks),
                                      excluded=True))
    _write(rows, "03_ranked_all_mixes_goals.csv")


def _rank_row(spec, mix_name, goal, rank, s, n_tasks, excluded) -> dict:
    gv = goal_value(s, goal)
    return {
        "mix_id": spec,
        "mix_label": mix_name,
        "n_tasks": n_tasks,
        "goal": goal,
        "rank": rank,
        "excluded": excluded,
        "scheduler": s.scheduler,
        "dispatch_order": "->".join(f"T{t}" for t in s.order),
        "goal_value": "" if gv in (float("inf"), float("-inf")) else f"{gv:.6f}",
        "makespan_cycles": s.makespan,
        "mean_turnaround_cycles": f"{s.mean_turnaround:.1f}",
        "mean_wait_cycles": f"{s.mean_wait:.1f}",
        "max_turnaround_cycles": s.max_turnaround,
        "max_wait_cycles": s.max_wait,
        "weighted_score": f"{s.weighted:.4f}",
        "luts": "" if s.luts is None else s.luts,
        "ffs": "" if s.ffs is None else s.ffs,
        "power_dynamic_w": "" if s.power_dynamic_w is None else f"{s.power_dynamic_w:.3f}",
        "fmax_mhz_post_synth": "" if s.fmax_mhz is None else f"{s.fmax_mhz:.1f}",
        "mean_turnaround_us": "" if s.mean_turnaround_us is None else f"{s.mean_turnaround_us:.2f}",
        "throughput_tasks_per_s": "" if s.throughput_tasks_per_s is None else f"{s.throughput_tasks_per_s:.1f}",
        "energy_uJ": "" if s.energy_uJ is None else f"{s.energy_uJ:.3f}",
        "hw_status": s.hw_status,
        "timing_source": "model",
        "hw_source": "measured (Vivado 2025.2 OOC)",
        "note": s.hw_note,
    }


# ---------------------------------------------------------------------------
# 04-08 -- the five evaluations (verbatim copies of eval_sched_chooser.py output)
# ---------------------------------------------------------------------------
def export_evals() -> None:
    _copy(SCHED / "eval_decision_accuracy.csv", "04_eval_decision_accuracy.csv")
    _copy(SCHED / "eval_sensitivity.csv",       "05_eval_sensitivity.csv")
    _copy(SCHED / "eval_anchor_order.csv",      "06_eval_anchor_order.csv")
    _copy(SCHED / "eval_anchor_flatness.csv",   "07_eval_anchor_flatness.csv")
    _copy(SCHED / "eval_speed.csv",             "08_eval_speed.csv")


# ---------------------------------------------------------------------------
# 09 -- measured RTL golden runs (per scheduler, per task)
# ---------------------------------------------------------------------------
def export_golden() -> None:
    rows = []
    for sched in GOLDEN_MEASURED:
        p = GOLDEN_RAW / f"multi_{sched}_8x8.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        seen, order = set(), []
        for disp in d["dispatch_order"]:
            if disp["task"] not in seen:
                seen.add(disp["task"])
                order.append(disp["task"])
        dispatch_cycle = {x["task"]: x["cycle"] for x in d["dispatch_order"]}
        for t in d["tasks"]:
            rows.append({
                "scheduler": sched,
                "task_id": t["task"],
                "layer": t["layer"],
                "task_cycles_measured": t["cycles"],
                "dispatch_cycle_measured": dispatch_cycle.get(t["task"], ""),
                "max_err_pct_full_scale": f"{t['max_err_pct_fs']:.4f}",
                "task_passed": t["passed"],
                "dispatch_order_measured": "->".join(f"T{x}" for x in order),
                "total_cycles_measured": d["total_cycles"],
                "all_pass": d["all_pass"],
                "array": "8x8",
                "source": "measured (RTL) -- results/golden_check/raw",
            })
    _write(rows, "09_golden_rtl_runs.csv")


# ---------------------------------------------------------------------------
# 10 -- workload mixes: what the schedulers are being asked to schedule
# ---------------------------------------------------------------------------
def export_workloads() -> None:
    by_name = {w["name"]: w for w in EDGE_WORKLOADS + CLOUD_WORKLOADS}
    edge_names = {w["name"] for w in EDGE_WORKLOADS}
    rows = []
    for spec, mix in zip(MIX_SPECS, WORKLOAD_MIXES):
        for tid, dnn in enumerate(mix["dnns"]):
            wl = by_name[dnn]
            macs = sum(l.weight_k * l.weight_c * l.weight_kh * l.weight_kw
                       * l.output_height * l.output_width
                       for l in wl["layers"])
            cyc = sum(estimate_cycles(l, DATAFLOW, ARRAY_H, ARRAY_W)
                      for l in wl["layers"])
            beats = sum(prefetch_traffic(l, ARRAY_H, ARRAY_W, "MULTICAST",
                                         DATAFLOW)["beats"]
                        for l in wl["layers"])
            rows.append({
                "mix_id": spec,
                "mix_label": mix["label"],
                "mix_name": mix["name"],
                "task_id": tid,
                "dnn": dnn,
                "domain": "Edge" if dnn in edge_names else "Cloud",
                "n_layers": len(wl["layers"]),
                "total_macs": macs,
                "total_macs_millions": round(macs / 1e6, 3),
                "model_compute_cycles": int(cyc),
                "model_prefetch_beats": int(beats),
                "declared_priority": tid,
                "declared_deadline": 1000 * (tid + 1),
                "source": ("workload definition (scripts/workloads.py) + "
                           "model (estimate_cycles / prefetch_traffic)"),
            })
    _write(rows, "10_workload_mixes.csv")


# ---------------------------------------------------------------------------
# 11-12 -- older experiment-5 output: the hardcoded factor model.
#          Exported ONLY as the contrast case.  Not measured.
# ---------------------------------------------------------------------------
def export_exp5() -> None:
    rows = []
    for domain, base in [("Edge", RESULTS / "edge"), ("Cloud", RESULTS / "cloud")]:
        p = base / "exp5_schedulers" / "scheduler_per_mix.csv"
        if not p.exists():
            continue
        for r in csv.DictReader(open(p)):
            r["domain"] = domain
            r["provenance"] = ("ASSUMED constant-factor table "
                               "(run_full_eval.py:295 SCHEDULER_MODEL) -- "
                               "no derivation and no measurement behind it; "
                               "workload-independent by construction")
            rows.append(r)
    _write(rows, "11_exp5_factor_model.csv")

    # The factor table itself, read live from the source it lives in.  The
    # committed exp5 CSVs above were produced by an EARLIER revision of
    # run_full_eval.py and their speedup column no longer equals these
    # constants -- which is itself part of the point about undocumented
    # factor tables, so both are exported rather than reconciled.
    from scripts.run_full_eval import SCHEDULER_MODEL
    ft = [{"scheduler": k,
           "label": next((lab for _, n, lab, _, _, _ in INVENTORY if n == k), k),
           "throughput_factor_vs_fifo": t,
           "offchip_factor_vs_fifo": o,
           "energy_factor_vs_fifo": e,
           "provenance": ("ASSUMED constant, read from "
                          "scripts/run_full_eval.py SCHEDULER_MODEL. "
                          "No derivation and no measurement behind it "
                          "anywhere in the repository; workload-independent "
                          "by construction. NOT used by the chooser.")}
          for k, (t, o, e) in SCHEDULER_MODEL.items()]
    _write(ft, "11b_scheduler_factor_table.csv")

    sd = []
    for domain, base in [("Edge", RESULTS / "edge"), ("Cloud", RESULTS / "cloud")]:
        p = base / "exp5_schedulers" / "static_vs_dynamic.csv"
        if not p.exists():
            continue
        for r in csv.DictReader(open(p)):
            r["domain"] = domain
            r["provenance"] = ("Static row = analytical sim_layer model; "
                               "Dynamic row = Static x the ASSUMED "
                               "SCHEDULER_MODEL BATCHDNN_PP factors")
            sd.append(r)
    _write(sd, "12_static_vs_dynamic.csv")


# ---------------------------------------------------------------------------
# 13 -- findings register
# ---------------------------------------------------------------------------
FINDINGS = [
    {
        "id": "F1",
        "title": "BATCH-DNN / BATCH-DNN++ did not synthesise (runtime loop bound)",
        "evidence": ("Vivado [Synth 8-3380] loop condition does not converge "
                     "after 2000 iterations -- batchdnn_scheduler.sv:370, "
                     "batchdnn_pp_scheduler.sv:564; corroborated by Yosys 0.67"),
        "impact": ("2 of the 3 flagship DNN-aware schedulers were "
                   "simulation-only RTL: correct in simulation "
                   "(golden all_pass) but not buildable"),
        "action": ("FIXED on branch fix/scheduler-synthesis: loop bounded "
                   "statically, compare inside. BATCH-DNN now measured "
                   "(4,657 LUT). Equivalence proven by "
                   "tb/unit/test_scheduler_synth_fix.py"),
        "status": "Fixed (BATCH-DNN measured; BATCH-DNN++ still unmeasured)",
        "source": "measured (Vivado tool output)",
    },
    {
        "id": "F2",
        "title": "HRRN did not synthesise (floating-point in RTL)",
        "evidence": ("Vivado [Synth 8-27] real number expression not "
                     "supported -- advanced_task_scheduler.sv:180; "
                     "schedule_hrrn() computed its response ratio in `real`"),
        "impact": ("HRRN wins 4 of 32 mix x goal cases on cycle-only "
                   "timing, so a cycle-only analysis would have recommended "
                   "a scheduler that could not be built"),
        "action": ("FIXED: exact integer cross-multiplication instead of "
                   "real division. Now measured: 2,941 LUT, 60 DSP, "
                   "6.5 MHz -- buildable but the slowest of all 13"),
        "status": "Fixed and measured",
        "source": "measured (Vivado tool output)",
    },
    {
        "id": "F3",
        "title": "AI-MT and BATCH-DNN have multi-driven registers",
        "evidence": ("164 CRITICAL WARNINGs (AI-MT) and 200 (BATCH-DNN) of "
                     "form [Synth 8-6859] multi-driven net on pin Q; Vivado "
                     "keeps the constant driver and discards the real one"),
        "impact": ("The reported area/power are honest measurements of a "
                   "netlist that does not faithfully implement the "
                   "simulated design"),
        "action": ("NOT fixed -- needs an ownership restructure of "
                   "sched_table. Recorded in the note column of every "
                   "affected CSV row so no consumer silently trusts it"),
        "status": "Open, disclosed",
        "source": "measured (Vivado tool output)",
    },
    {
        "id": "F4",
        "title": "The project-wide CLOCK_GHZ = 1.0 assumption is ~9x optimistic",
        "evidence": ("run_full_eval.py:80 assumes 1.0 GHz for every "
                     "throughput and GOPS figure in experiments 1-7. "
                     "Measured post-synthesis Fmax on the project's own "
                     "target part tops out at 112.4 MHz (MLQ)"),
        "impact": ("Every published throughput figure in the repository is "
                   "an upper bound the hardware does not reach; and the "
                   "cycle ranking of schedulers inverts once the measured "
                   "clock is applied"),
        "action": ("Chooser reports wall-clock turnaround (model cycles / "
                   "measured Fmax) as a first-class goal so the inversion "
                   "is visible"),
        "status": "Open (project-wide), surfaced by the chooser",
        "source": "measured (Vivado) vs source constant",
    },
]


def export_findings() -> None:
    _write(FINDINGS, "13_findings.csv")


# ---------------------------------------------------------------------------
# 14 -- measured Fmax vs the assumed clock (Finding 4, quantified)
# ---------------------------------------------------------------------------
def export_fmax_gap() -> None:
    hw = load_hw_table()
    rows = []
    label = {n: lab for _, n, lab, _, _, _ in INVENTORY}
    for name in SCHEDULERS:
        row = hw.get(name, {})
        f = row.get("fmax_mhz_post_synth", "")
        if not f:
            continue
        f = float(f)
        rows.append({
            "scheduler": name,
            "label": label[name],
            "fmax_mhz_measured": f,
            "assumed_clock_mhz": ASSUMED_CLOCK_MHZ,
            "optimism_factor": round(ASSUMED_CLOCK_MHZ / f, 1),
            "wns_ns": row.get("wns_ns", ""),
            "constraint_ns": row.get("constraint_ns", ""),
            "source": ("measured (Vivado post-synthesis estimate: "
                       "1000 / (constraint_ns - WNS)) vs "
                       "run_full_eval.py:80 CLOCK_GHZ = 1.0"),
        })
    rows.sort(key=lambda r: -r["fmax_mhz_measured"])
    _write(rows, "14_fmax_vs_clock_assumption.csv")


# ---------------------------------------------------------------------------
# 15 -- provenance manifest, so the notebook can print where things came from
# ---------------------------------------------------------------------------
MANIFEST = [
    ("01_scheduler_inventory.csv", "RTL source + Vivado status",
     "The 14 schedulers the RTL implements, their select code, family and wrapper."),
    ("02_scheduler_hw_measured.csv", "measured (Vivado 2025.2 OOC)",
     "LUT / FF / DSP / BRAM / power / WNS / Fmax on xc7a100tcsg324-1."),
    ("03_ranked_all_mixes_goals.csv", "model + measured + derived",
     "Chooser ranking of all 14 schedulers for 4 workload mixes x 8 goals."),
    ("04_eval_decision_accuracy.csv", "model / measured",
     "Chooser pick vs independent exhaustive re-scoring, per mix x goal."),
    ("05_eval_sensitivity.csv", "model / measured",
     "Which scheduler is recommended for each mix x goal."),
    ("06_eval_anchor_order.csv", "measured (RTL) vs model",
     "Model dispatch order vs the recorded RTL golden runs."),
    ("07_eval_anchor_flatness.csv", "measured (RTL) vs model",
     "Makespan spread in hardware vs in the model."),
    ("08_eval_speed.csv", "measured",
     "Chooser query latency, warm and cold, vs Vivado synthesis cost."),
    ("09_golden_rtl_runs.csv", "measured (RTL)",
     "Per-task cycles, dispatch cycles and accuracy from the golden runs."),
    ("10_workload_mixes.csv", "workload definition + model",
     "The 4 multi-DNN workload mixes and their per-task cost."),
    ("11_exp5_factor_model.csv", "ASSUMED constant-factor table (not measured)",
     "Older experiment-5 output, exported only as the contrast case."),
    ("11b_scheduler_factor_table.csv", "ASSUMED constants read from source",
     "The SCHEDULER_MODEL factor table itself, which the chooser does not use."),
    ("12_static_vs_dynamic.csv", "analytical model x assumed factors",
     "Older static-vs-dynamic scheduling comparison."),
    ("13_findings.csv", "measured (Vivado tool output)",
     "The four findings the framework produced, with status."),
    ("14_fmax_vs_clock_assumption.csv", "measured vs source constant",
     "Finding 4 quantified: measured Fmax against the assumed 1.0 GHz."),
]


def export_manifest() -> None:
    rows = [{"file": f, "provenance": p, "description": d}
            for f, p, d in MANIFEST]
    _write(rows, "00_manifest.csv")


def main() -> None:
    print(f"Exporting Member-3 dataset to {OUT.relative_to(REPO)}\n")
    export_manifest()
    export_inventory()
    export_hw()
    export_ranked()
    export_evals()
    export_golden()
    export_workloads()
    export_exp5()
    export_findings()
    export_fmax_gap()
    print("\nDone.  Zip member3_colab/data and upload it to Colab, or upload "
          "the individual CSVs.")


if __name__ == "__main__":
    main()
