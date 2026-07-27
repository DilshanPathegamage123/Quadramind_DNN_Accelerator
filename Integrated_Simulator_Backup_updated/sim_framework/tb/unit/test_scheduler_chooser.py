"""Unit tests for the multi-DNN scheduler chooser policy models.

These lock down the transcription of each RTL selector
(rtl/schedulers/task_scheduler.sv, advanced_task_scheduler.sv,
aimt_scheduler.sv) into pysim/scheduler_chooser.py, plus the two
properties the framework must never violate:

  * it must reproduce the MEASURED golden dispatch orders, and
  * it must NOT invent a makespan speedup the hardware does not show.

Runs without cocotb, Verilator or Vivado (the repo's standard pattern for
tb/unit).  Hardware columns are absent unless the Vivado table has been
generated, and their absence must never turn into a fabricated number.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from pysim.scheduler_chooser import (SCHEDULERS, Task, load_hw_table,
                                     rank_schedulers, simulate)


def _tasks(specs):
    """specs: list of (compute, burst, priority, deadline, arrival)."""
    return [Task(tid=i, name=f"T{i}", compute_cycles=c, burst_time=b,
                 priority=p, deadline=d, arrival=a)
            for i, (c, b, p, d, a) in enumerate(specs)]


# Three tasks, distinct on every attribute so each policy is separable.
# Service costs differ too, otherwise turnaround/wait collapse to the same
# value for every order and the discrimination tests prove nothing.
BASE = _tasks([
    (300, 30, 0, 3000, 0),   # T0: longest, lowest prio, latest deadline
    (100, 10, 2, 1000, 0),   # T1: shortest, highest prio, earliest deadline
    (200, 20, 1, 2000, 0),   # T2: middle on everything
])


def test_fifo_takes_head():
    assert simulate(BASE, "FIFO")["order"] == [0, 1, 2]


def test_lifo_takes_newest():
    assert simulate(BASE, "LIFO")["order"] == [2, 1, 0]


def test_sjf_takes_shortest_burst():
    assert simulate(BASE, "SJF")["order"] == [1, 2, 0]


def test_pri_takes_highest_priority():
    assert simulate(BASE, "PRI")["order"] == [1, 2, 0]


def test_edf_takes_earliest_deadline():
    assert simulate(BASE, "EDF")["order"] == [1, 2, 0]


def test_srtf_takes_least_remaining():
    # remaining_time is initialised to burst_time (advanced_task_scheduler.sv)
    assert simulate(BASE, "SRTF")["order"] == [1, 2, 0]


def test_mlq_degenerates_to_fifo():
    """Faithful transcription, not a bug fix.

    Every task enters at queue_level 0 (advanced_task_scheduler.sv:100) and
    MLQ scans levels from NUM_QUEUES-1 DOWN to 0, so it always lands on the
    first level-0 task.  If this test starts failing, the RTL changed.
    """
    assert simulate(BASE, "MLQ")["order"] == simulate(BASE, "FIFO")["order"]


def test_dnn_aware_family_follows_table_order():
    for s in ("AIMT", "BATCHDNN", "BATCHDNN_PP"):
        assert simulate(BASE, s)["order"] == [0, 1, 2]


def test_every_scheduler_runs_every_task_once():
    for s in SCHEDULERS:
        order = simulate(BASE, s)["order"]
        assert sorted(order) == [0, 1, 2], f"{s} lost or duplicated a task"


def test_makespan_invariant_when_all_arrive_together():
    """The measured hardware shows all five schedulers within ONE cycle.

    With a single accelerator and every task ready at t=0, total work is
    order-independent, so makespan must be identical across schedulers.  A
    model that predicted a speedup here would be inventing one.
    """
    spans = {s: simulate(BASE, s)["makespan"] for s in SCHEDULERS}
    assert len(set(spans.values())) == 1, spans
    assert spans["FIFO"] == 600


def test_makespan_invariant_under_staggered_arrivals_too():
    """Makespan is invariant for ANY work-conserving order, not just at t=0.

    A single machine that never idles while work is queued finishes at the
    same time whatever order it picks -- reordering changes which task runs
    when, not the total busy time nor the forced wait for a late arrival.
    So `--goal makespan` is provably an all-way tie on this accelerator.
    An earlier draft of this framework claimed staggered arrivals would
    separate schedulers on makespan; this test exists because that claim
    was wrong.
    """
    staggered = _tasks([(300, 30, 0, 3000, 0),
                        (100, 10, 2, 1000, 250),
                        (200, 20, 1, 2000, 900)])
    spans = {s: simulate(staggered, s)["makespan"] for s in SCHEDULERS}
    assert len(set(spans.values())) == 1, spans


def test_turnaround_and_wait_discriminate():
    """The metrics scheduling actually moves must not be flat."""
    tas = {s: simulate(BASE, s)["mean_turnaround"] for s in SCHEDULERS}
    assert len(set(tas.values())) > 1


def test_wait_is_never_negative():
    for s in SCHEDULERS:
        assert simulate(BASE, s)["mean_wait"] >= 0


# ---------------------------------------------------------------------------
# Anchors against the MEASURED golden runs
# ---------------------------------------------------------------------------

RAW = ROOT / "results/golden_check/raw"
GOLDEN = {"FIFO": [0, 1, 2], "LIFO": [2, 1, 0], "AIMT": [0, 1, 2],
          "BATCHDNN": [0, 1, 2], "BATCHDNN_PP": [0, 1, 2]}


@pytest.mark.parametrize("sched", sorted(GOLDEN))
def test_matches_measured_golden_dispatch_order(sched):
    raw = RAW / f"multi_{sched}_8x8.json"
    if not raw.exists():
        pytest.skip(f"measured golden run missing: {raw.name}")
    data = json.loads(raw.read_text())
    seen, measured = set(), []
    for d in data["dispatch_order"]:
        if d["task"] not in seen:
            seen.add(d["task"])
            measured.append(d["task"])
    assert measured == GOLDEN[sched], "recorded golden run changed"

    # golden harness declares synthetic attributes; replay them verbatim
    tasks = _tasks([(971, 10, 0, 1000, 0),
                    (355, 20, 1, 2000, 0),
                    (11782, 30, 2, 3000, 0)])
    assert simulate(tasks, sched)["order"] == measured


# ---------------------------------------------------------------------------
# The no-fabrication guarantee
# ---------------------------------------------------------------------------

def test_missing_hardware_data_is_never_substituted():
    """Schedulers without synthesis results get None, not a stand-in."""
    ranked, excluded = rank_schedulers(BASE, None, "makespan", hw={})
    for s in ranked + excluded:
        assert s.luts is None and s.ffs is None
        assert s.power_dynamic_w is None and s.fmax_mhz is None
        assert s.throughput_tasks_per_s is None and s.energy_uJ is None


def test_hardware_goals_exclude_rather_than_guess():
    """A goal needing measured data must drop candidates that lack it."""
    ranked, excluded = rank_schedulers(BASE, None, "area", hw={})
    assert ranked == [] and len(excluded) == len(SCHEDULERS)


def test_hw_table_rows_are_consistent_when_present():
    hw = load_hw_table()
    if not hw:
        pytest.skip("no Vivado table yet (run scripts/synth_scheduler_hw.py)")
    for name, row in hw.items():
        assert name in SCHEDULERS, f"unknown scheduler in hw table: {name}"
        if row["status"] == "ok":
            assert row["luts"] and int(row["luts"]) > 0
            assert row["ffs"] and int(row["ffs"]) > 0
        else:
            # a scheduler that did not synthesise must carry NO numbers
            assert row["luts"] == "" and row["ffs"] == ""
            assert row["power_total_w"] == ""
            assert row["note"], "unavailable rows must state why"
