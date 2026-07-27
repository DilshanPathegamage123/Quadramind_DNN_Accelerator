"""Analytical multi-DNN scheduler chooser.

Scores every scheduler the RTL implements (14 of them) against a workload
mix on a fixed array + memory provision, ranks them by a user goal, and
returns the best scheduler plus the full ranked table.  Pure analytical --
no RTL and no synthesis is run per query.

WHAT IS MEASURED AND WHAT IS MODELLED
-------------------------------------
measured (Vivado):  LUT / FF / DSP / BRAM, power, and post-synthesis Fmax,
    read from results/sched_chooser/hw/scheduler_hw.csv, produced by
    scripts/synth_scheduler_hw.py from real out-of-context synthesis.
    Schedulers that do not synthesise carry NO number -- never interpolated.
measured (RTL):     dispatch order and total cycles for FIFO / LIFO / AIMT /
    BATCHDNN / BATCHDNN_PP on the golden 3-task mix, in
    results/golden_check/raw/multi_*.json.  Used by the evaluation as an
    anchor; not used to compute chooser scores.
model:              per-task service cycles (software_ref.estimate_cycles --
    a RANK score, not a cycle prediction, per GOLDEN_CHECK_SUMMARY.md sec.7),
    the queueing simulation, and every timing metric derived from them.
derived:            throughput and scheduler energy (model cycles combined
    with measured Fmax / measured power).

MACHINE MODEL -- why it is run-to-completion
--------------------------------------------
multi_dnn_top's dispatch FSM holds a dispatched task until its
task_complete pulse, and the golden harness serves exactly one task at a
time.  So although several RTL selectors are preemptive (RR, LRU, SRTF,
MLFQ re-decide every cycle), preemption cannot manifest in this
integration: whatever is dispatched runs to completion.  The simulation
therefore applies each policy's selection rule at dispatch points only.
This is a property of the system, not a simplification chosen for
convenience -- and it is why several policies produce identical orders.

WHAT IS DELIBERATELY NOT MODELLED
----------------------------------
AI-MT's memory/compute overlap and BatchDNN's sub-batch pipelining are the
designed benefit of those schedulers, but this integration serialises MT
and CT, and the measured golden runs show all five schedulers within ONE
cycle (13,412 vs 13,413).  Modelling an overlap speedup would produce a
number no measurement in this project supports, so service time carries no
overlap term.

WHY MAKESPAN CANNOT DISCRIMINATE HERE
--------------------------------------
This follows from the machine, not from the model: on a SINGLE machine
that never idles while work is queued (work-conserving), makespan is
identical for every scheduling order -- including under staggered
arrivals.  Reordering moves which task runs when, never the total busy
time nor the forced idle waiting for an arrival.  So `--goal makespan`
provably returns an all-way tie on this accelerator, and the measured
hardware agrees (13,412 vs 13,413 cycles across five schedulers, a 1-cycle
spread attributable to dispatch handshake, not to policy).

The metrics scheduling genuinely moves on this hardware are per-task
TURNAROUND and WAIT, plus the scheduler's own measured hardware cost
(area, power, Fmax).  Those are the goals worth choosing on.
"""
from __future__ import annotations

import csv
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from pysim.sim_config import LayerConfig
from pysim.software_ref import estimate_cycles

ROOT = Path(__file__).resolve().parent.parent

# Select codes 0..13, mirroring SimConfig.SCHEDULER_NAMES and the decode in
# rtl/schedulers/unified_scheduler_wrapper.sv.
SCHEDULERS = ["FIFO", "LIFO", "SJF", "RR", "PRI", "EDF", "LRU",
              "SRTF", "HRRN", "MLQ", "MLFQ",
              "AIMT", "BATCHDNN", "BATCHDNN_PP"]

DNN_AWARE = {"AIMT", "BATCHDNN", "BATCHDNN_PP"}

GOALS = ["makespan", "turnaround", "turnaround_us", "wait", "throughput",
         "area", "power", "weighted"]

# Goals where a LOWER value is better.  throughput is the only maximised one.
_MAXIMISE = {"throughput"}

# rtl/schedulers/task_scheduler.sv:91
NON_PREEMPTIVE = {"FIFO", "LIFO", "SJF", "PRI", "EDF"}
# rtl/schedulers/advanced_task_scheduler.sv -- NUM_QUEUES default
NUM_QUEUES = 4
# rtl/schedulers/aimt_scheduler.sv -- COMPUTE_BAL_THRESH default
COMPUTE_BAL_THRESH = 1000


@dataclass
class Task:
    """One DNN inference submitted to the scheduler.

    compute_cycles / mem_cycles are MODEL values.  burst_time, priority and
    deadline are the attributes the system *declares* to the scheduler --
    the RTL decides on these, not on the true cost, so they are separate
    fields (the golden harness declares synthetic values, which is what the
    anchor replay reproduces).
    """
    tid: int
    name: str
    compute_cycles: int
    mem_cycles: int = 0
    burst_time: int = 0
    priority: int = 0
    deadline: int = 0
    arrival: int = 0

    @property
    def service(self) -> int:
        """Cycles the machine is occupied by this task (no overlap term --
        see the module docstring)."""
        return self.compute_cycles


@dataclass
class SchedResult:
    scheduler: str
    order: List[int]
    makespan: int
    mean_turnaround: float
    max_turnaround: int
    mean_wait: float
    max_wait: int
    # measured hardware columns (empty when the scheduler does not synthesise)
    luts: Optional[int] = None
    ffs: Optional[int] = None
    fmax_mhz: Optional[float] = None
    power_dynamic_w: Optional[float] = None
    hw_status: str = "unknown"
    hw_note: str = ""
    # derived
    throughput_tasks_per_s: Optional[float] = None
    mean_turnaround_us: Optional[float] = None
    energy_uJ: Optional[float] = None
    weighted: float = float("nan")

    @property
    def area_luts(self) -> Optional[int]:
        return self.luts


# ---------------------------------------------------------------------------
# Policy selectors -- transcribed from the RTL, one function per algorithm.
# Each takes the ready queue (list of Task, in RTL array order after
# compaction) plus simulation state, and returns the index to dispatch.
# ---------------------------------------------------------------------------

def _sel_fifo(q, st):          # task_scheduler.sv case 0
    return 0


def _sel_lifo(q, st):          # case 1: newest = highest index
    return len(q) - 1


def _sel_sjf(q, st):           # case 2: min burst_time, first index wins
    best = 0
    for i in range(1, len(q)):
        if q[i].burst_time < q[best].burst_time:
            best = i
    return best


def _sel_rr(q, st):            # case 3: rr_ptr, wraps when past the end
    ptr = st.get("rr_ptr", 0)
    return ptr if ptr < len(q) else 0


def _sel_pri(q, st):           # case 4: max priority, first index wins
    best = 0
    for i in range(1, len(q)):
        if q[i].priority > q[best].priority:
            best = i
    return best


def _sel_edf(q, st):           # case 5: min deadline, first index wins
    best = 0
    for i in range(1, len(q)):
        if q[i].deadline < q[best].deadline:
            best = i
    return best


def _sel_lru(q, st):           # case 6: min last_access_time
    acc = st["last_access"]
    best = 0
    for i in range(1, len(q)):
        if acc.get(q[i].tid, 0) < acc.get(q[best].tid, 0):
            best = i
    return best


def _sel_srtf(q, st):          # advanced: min remaining_time
    rem = st["remaining"]
    best = 0
    for i in range(1, len(q)):
        if rem[q[i].tid] < rem[q[best].tid]:
            best = i
    return best


def _sel_hrrn(q, st):          # advanced: max (wait + burst) / burst
    wait = st["wait_time"]
    best, best_r = 0, -1.0
    for i, t in enumerate(q):
        b = max(t.burst_time, 1)
        r = (wait.get(t.tid, 0) + b) / b
        if r > best_r:
            best, best_r = i, r
    return best


def _sel_mlq(q, st):
    """advanced: schedule_mlq scans queue levels from NUM_QUEUES-1 DOWN to 0.

    Every task is inserted at queue_level 0 (advanced_task_scheduler.sv:100)
    and MLQ never changes a level, so the high-to-low scan finds nothing
    above level 0 and always selects the first task at level 0.  Transcribed
    as written: this makes MLQ behave as FIFO in this RTL.  Recorded as a
    faithful transcription, not a bug fix.
    """
    lvl = st["queue_level"]
    for level in range(NUM_QUEUES - 1, -1, -1):
        for i, t in enumerate(q):
            if lvl.get(t.tid, 0) == level:
                return i
    return 0


def _sel_mlfq(q, st):          # advanced: scans levels 0 UP to NUM_QUEUES-1
    lvl = st["queue_level"]
    for level in range(NUM_QUEUES):
        for i, t in enumerate(q):
            if lvl.get(t.tid, 0) == level:
                return i
    return 0


def _sel_dnn_aware(q, st):
    """AI-MT / BatchDNN / BatchDNN++ table scan.

    aimt_scheduler.sv walks the scheduling table in index order and
    dispatches the first candidate whose memory task fits the balance
    checks (mem_cycles <= cycles_to_fill_remaining, or available compute
    beyond COMPUTE_BAL_THRESH).  With a run-to-completion machine the
    balance checks never defer a candidate, so the walk selects in table
    order -- which is what the measured runs show (T0->T1->T2 for all three
    DNN-aware schedulers).  BatchDNN and BatchDNN++ reuse this MT path and
    modify only CT sub-batching, which is inert at unit batch.
    """
    return 0


_SELECTORS = {
    "FIFO": _sel_fifo, "LIFO": _sel_lifo, "SJF": _sel_sjf, "RR": _sel_rr,
    "PRI": _sel_pri, "EDF": _sel_edf, "LRU": _sel_lru,
    "SRTF": _sel_srtf, "HRRN": _sel_hrrn, "MLQ": _sel_mlq, "MLFQ": _sel_mlfq,
    "AIMT": _sel_dnn_aware, "BATCHDNN": _sel_dnn_aware,
    "BATCHDNN_PP": _sel_dnn_aware,
}


def simulate(tasks: List[Task], scheduler: str) -> dict:
    """Run the queueing simulation for one scheduler.

    Returns dispatch order, makespan and per-task start/finish, from which
    turnaround and wait follow.  Model values throughout.
    """
    if scheduler not in _SELECTORS:
        raise ValueError(f"unknown scheduler {scheduler!r}")
    select = _SELECTORS[scheduler]

    pending = sorted(tasks, key=lambda t: (t.arrival, t.tid))
    queue: List[Task] = []
    st = {
        "rr_ptr": 0,
        "last_access": {t.tid: 0 for t in tasks},
        "remaining": {t.tid: t.burst_time for t in tasks},
        "wait_time": {t.tid: 0 for t in tasks},
        "queue_level": {t.tid: 0 for t in tasks},
    }
    now = 0
    order: List[int] = []
    starts: Dict[int, int] = {}
    finishes: Dict[int, int] = {}

    while pending or queue:
        # admit everything that has arrived (RTL: insertion at the tail)
        newly = [t for t in pending if t.arrival <= now]
        if not newly and not queue:
            now = pending[0].arrival          # machine idles to next arrival
            continue
        for t in newly:
            queue.append(t)
            pending.remove(t)

        idx = select(queue, st)
        idx = max(0, min(idx, len(queue) - 1))
        task = queue.pop(idx)                  # RTL: removal + compaction

        start = max(now, task.arrival)
        finish = start + task.service
        order.append(task.tid)
        starts[task.tid] = start
        finishes[task.tid] = finish

        # per-policy state updates, mirroring the RTL always_ff blocks
        st["last_access"][task.tid] = start                     # LRU
        st["remaining"][task.tid] = 0                           # SRTF
        for other in queue:                                     # wait_time
            st["wait_time"][other.tid] += task.service
        if scheduler == "RR":                                   # rr_ptr
            st["rr_ptr"] = 0 if idx >= max(len(queue), 1) else idx
        if scheduler == "MLFQ":
            lvl = st["queue_level"]
            if lvl[task.tid] < NUM_QUEUES - 1:
                lvl[task.tid] += 1
            for other in queue:                 # aging promotion, wait > 100
                if st["wait_time"][other.tid] > 100 and lvl[other.tid] > 0:
                    lvl[other.tid] -= 1
        now = finish

    makespan = max(finishes.values()) if finishes else 0
    turnarounds = [finishes[t.tid] - t.arrival for t in tasks]
    waits = [starts[t.tid] - t.arrival for t in tasks]
    return {
        "order": order,
        "makespan": makespan,
        "starts": starts,
        "finishes": finishes,
        "mean_turnaround": sum(turnarounds) / len(turnarounds),
        "max_turnaround": max(turnarounds),
        "mean_wait": sum(waits) / len(waits),
        "max_wait": max(waits),
    }


# ---------------------------------------------------------------------------
# Measured hardware table
# ---------------------------------------------------------------------------

def load_hw_table(path: Optional[Path] = None) -> Dict[str, dict]:
    """Load the measured Vivado synthesis results.

    Missing file or missing scheduler -> no hardware numbers for it.  This
    function never invents or interpolates a value.
    """
    p = path or (ROOT / "results/sched_chooser/hw/scheduler_hw.csv")
    if not p.exists():
        return {}
    out = {}
    with open(p, newline="") as fh:
        for row in csv.DictReader(fh):
            out[row["scheduler"]] = row
    return out


def _num(row: dict, key: str, cast=float):
    v = (row or {}).get(key, "")
    if v in ("", None):
        return None
    try:
        return cast(v)
    except (TypeError, ValueError):
        return None


def build_tasks(mix: List[tuple[str, List[LayerConfig]]], dataflow: str,
                array_h: int, array_w: int,
                arrivals: Optional[List[int]] = None,
                priorities: Optional[List[int]] = None,
                deadlines: Optional[List[int]] = None,
                burst_times: Optional[List[int]] = None) -> List[Task]:
    """Turn (name, layers) pairs into Tasks with model cycle costs.

    Declared burst_time defaults to the modelled compute cycles (what a real
    system would declare); priority/deadline default to submission order,
    matching the golden harness convention.  All are overridable so the
    evaluation can replay the harness's exact synthetic attributes.
    """
    from pysim.config_chooser import prefetch_traffic
    tasks = []
    for i, (name, layers) in enumerate(mix):
        cyc = sum(estimate_cycles(l, dataflow, array_h, array_w)
                  for l in layers)
        beats = sum(prefetch_traffic(l, array_h, array_w, "MULTICAST",
                                     dataflow)["beats"] for l in layers)
        tasks.append(Task(
            tid=i, name=name,
            compute_cycles=int(cyc), mem_cycles=int(beats),
            burst_time=int(burst_times[i]) if burst_times else int(cyc),
            priority=int(priorities[i]) if priorities else i,
            deadline=int(deadlines[i]) if deadlines else 1000 * (i + 1),
            arrival=int(arrivals[i]) if arrivals else 0,
        ))
    return tasks


def score_scheduler(tasks: List[Task], scheduler: str,
                    hw: Dict[str, dict]) -> SchedResult:
    sim = simulate(tasks, scheduler)
    row = hw.get(scheduler, {})
    status = row.get("status", "unknown")
    fmax = _num(row, "fmax_mhz_post_synth")
    pdyn = _num(row, "power_dynamic_w")

    res = SchedResult(
        scheduler=scheduler,
        order=sim["order"],
        makespan=sim["makespan"],
        mean_turnaround=sim["mean_turnaround"],
        max_turnaround=sim["max_turnaround"],
        mean_wait=sim["mean_wait"],
        max_wait=sim["max_wait"],
        luts=_num(row, "luts", int),
        ffs=_num(row, "ffs", int),
        fmax_mhz=fmax,
        power_dynamic_w=pdyn,
        hw_status=status,
        hw_note=row.get("note", ""),
    )
    # derived: real wall-clock throughput needs the MEASURED clock, so it
    # only exists where synthesis succeeded.
    if fmax and res.makespan > 0:
        wall_s = res.makespan / (fmax * 1e6)
        res.throughput_tasks_per_s = len(tasks) / wall_s
        # Wall-clock turnaround: the metric that actually matters to a user.
        # Cycle counts alone are misleading here because the comparator-tree
        # policies (SJF/EDF/LRU/SRTF) buy fewer cycles at a much lower clock.
        res.mean_turnaround_us = res.mean_turnaround / fmax
        if pdyn is not None:
            res.energy_uJ = pdyn * wall_s * 1e6
    return res


def goal_value(s: SchedResult, goal: str) -> float:
    """The metric a goal ranks on.  Missing measured values sort last."""
    if goal == "makespan":
        return float(s.makespan)
    if goal == "turnaround":
        return s.mean_turnaround
    if goal == "turnaround_us":
        return (s.mean_turnaround_us if s.mean_turnaround_us is not None
                else float("inf"))
    if goal == "wait":
        return s.mean_wait
    if goal == "throughput":
        return (s.throughput_tasks_per_s
                if s.throughput_tasks_per_s is not None else float("-inf"))
    if goal == "area":
        return float(s.luts) if s.luts is not None else float("inf")
    if goal == "power":
        return (s.power_dynamic_w if s.power_dynamic_w is not None
                else float("inf"))
    if goal == "weighted":
        return s.weighted
    raise ValueError(goal)


def rankable(s: SchedResult, goal: str) -> bool:
    """False when the goal needs a measured value this scheduler lacks."""
    if goal in ("area", "power", "throughput", "turnaround_us"):
        v = goal_value(s, goal)
        return math.isfinite(v)
    return True


def ties_at_best(ranked: List[SchedResult], goal: str) -> List[SchedResult]:
    """All schedulers exactly tied with the winner on the goal metric."""
    if not ranked:
        return []
    best = goal_value(ranked[0], goal)
    return [s for s in ranked if goal_value(s, goal) == best]


def rank_schedulers(tasks: List[Task], schedulers: Optional[List[str]] = None,
                    goal: str = "makespan",
                    weights: Optional[Dict[str, float]] = None,
                    hw: Optional[Dict[str, dict]] = None
                    ) -> tuple[List[SchedResult], List[SchedResult]]:
    """Score every scheduler and return (ranked, excluded).

    `excluded` holds schedulers that cannot be ranked on this goal because
    the measured value they would need does not exist (they do not
    synthesise).  They are never given a substitute number.

    Tie-break rule (deliberate, documented, mirrors the config-chooser):
    exact ties on the goal metric are ordered by mean turnaround, then mean
    wait, then makespan, and finally by scheduler NAME -- never by
    enumeration order.  The name key matters: schedulers that produce an
    identical dispatch order are identical on every timing metric, so
    without it the winner would be decided by list position.
    """
    if goal not in GOALS:
        raise ValueError(f"goal must be one of {GOALS}, got {goal!r}")
    names = schedulers or list(SCHEDULERS)
    hw = load_hw_table() if hw is None else hw
    scores = [score_scheduler(tasks, n, hw) for n in names]

    # weighted: normalise each metric by its best so best == 1.0.
    w = {"makespan": 1.0, "turnaround": 1.0, "wait": 1.0}
    if weights:
        w.update(weights)
    mins = {}
    for key, attr in [("makespan", "makespan"),
                      ("turnaround", "mean_turnaround"),
                      ("wait", "mean_wait")]:
        vals = [float(getattr(s, attr)) for s in scores]
        mins[key] = min(v for v in vals if v > 0) if any(v > 0 for v in vals) else 1.0
    for s in scores:
        s.weighted = (w["makespan"] * s.makespan / mins["makespan"]
                      + w["turnaround"] * s.mean_turnaround / mins["turnaround"]
                      + w["wait"] * max(s.mean_wait, 0.0) / mins["wait"])

    ok = [s for s in scores if rankable(s, goal)]
    excluded = [s for s in scores if not rankable(s, goal)]
    reverse = goal in _MAXIMISE
    ok.sort(key=lambda s: ((-goal_value(s, goal)) if reverse
                           else goal_value(s, goal),
                           s.mean_turnaround, s.mean_wait, s.makespan,
                           s.scheduler))
    return ok, excluded


# Numeric tie-break keys, in the order rank_schedulers applies them.  The
# final key (scheduler name) is not listed: it only guarantees determinism
# and never counts as having "broken" a tie.
TIEBREAK_KEYS = [("mean turnaround", lambda s: s.mean_turnaround),
                 ("mean wait", lambda s: s.mean_wait),
                 ("makespan", lambda s: float(s.makespan))]


def describe_tiebreak(tied: List[SchedResult]) -> str:
    """Explain which key actually separated a tied set.

    Reporting 'broken by turnaround' when every tied entry has the SAME
    turnaround would be circular and misleading, so this names the first
    key whose values genuinely differ.  When none of them do, it says so --
    schedulers with an identical dispatch order are identical on every
    timing metric, and the name key only makes the order deterministic.
    """
    for label, fn in TIEBREAK_KEYS:
        vals = [fn(s) for s in tied]
        if len(set(vals)) > 1:
            shown = ", ".join(f"{s.scheduler} {fn(s):,.0f}" for s in tied)
            return f"broken by {label} ({shown})"
    return ("NOT broken by any timing metric -- these schedulers produce an "
            "identical dispatch order and are equal on makespan, turnaround "
            "and wait; ordered deterministically by name. Distinguish them "
            "by the measured hardware columns (--goal area / power)")


def warm_up() -> float:
    """Load the heavy model dependencies so the first scoring call does not
    silently include the one-time import cost (the config-chooser's Issue 3
    discipline)."""
    t0 = time.perf_counter()
    import scripts.run_full_eval  # noqa: F401
    from pysim.config_chooser import prefetch_traffic  # noqa: F401
    return time.perf_counter() - t0


def choose(tasks: List[Task], schedulers: Optional[List[str]] = None,
           goal: str = "makespan",
           weights: Optional[Dict[str, float]] = None
           ) -> tuple[SchedResult, List[SchedResult], List[SchedResult], float]:
    """Return (best, ranked, excluded, elapsed_seconds)."""
    t0 = time.perf_counter()
    ranked, excluded = rank_schedulers(tasks, schedulers, goal, weights)
    return (ranked[0] if ranked else None), ranked, excluded, \
        time.perf_counter() - t0
