"""Equivalence tests for the three synthesisability fixes in the scheduler RTL.

Three schedulers did not synthesise (recorded as Findings 1 and 2 in
results/sched_chooser/SCHEDULER_CHOOSER_REPORT.md):

  * HRRN        -- rtl/schedulers/advanced_task_scheduler.sv used `real`
                   (floating-point) division, which has no hardware mapping
                   [Synth 8-27].
  * BATCHDNN    -- rtl/schedulers/batchdnn_scheduler.sv:370 and
  * BATCHDNN_PP -- rtl/schedulers/batchdnn_pp_scheduler.sv:564 looped from a
                   RUNTIME start bound, so the tool had no static trip count
                   [Synth 8-3380].

The fixes must be behaviour-preserving.  These tests execute the OLD and NEW
formulations side by side in Python and assert they select/iterate
identically, which is the part that can be checked without Vivado.  They do
NOT prove synthesisability -- only Vivado can, via
scripts/synth_scheduler_hw.py.

Runs without cocotb, Verilator or Vivado (the repo's standard tb/unit
pattern).
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Widths as parameterised in advanced_task_scheduler.sv
BURST_TIME_WIDTH = 16
DEADLINE_WIDTH = 32
MAX_TASKS = 16
# Widths as parameterised in batchdnn_scheduler.sv / batchdnn_pp_scheduler.sv
MAX_LAYERS = 32
LAYER_ID_WIDTH = 8


# ---------------------------------------------------------------------------
# HRRN: real division (old) vs integer cross-multiplication (new)
# ---------------------------------------------------------------------------

def _hrrn_old(queue, num_tasks):
    """Verbatim model of the pre-fix `real` implementation."""
    highest_idx, max_ratio = 0, 0.0
    for i in range(MAX_TASKS):
        if i < num_tasks and queue[i][1] > 0:
            wait, burst = queue[i]
            current_ratio = float(wait + burst) / float(burst)
            if current_ratio > max_ratio:
                max_ratio, highest_idx = current_ratio, i
    return highest_idx


def _hrrn_new(queue, num_tasks):
    """Verbatim model of the post-fix integer implementation."""
    highest_idx, found = 0, False
    best_num, best_den = 0, 0
    for i in range(MAX_TASKS):
        if i < num_tasks and queue[i][1] > 0:
            wait, burst = queue[i]
            cand_num, cand_den = wait + burst, burst
            lhs, rhs = cand_num * best_den, best_num * cand_den
            if (not found) or lhs > rhs:
                found, highest_idx = True, i
                best_num, best_den = cand_num, cand_den
    return highest_idx


def _rand_queue(rng, num_tasks, wait_hi, burst_hi):
    q = []
    for _ in range(MAX_TASKS):
        q.append((rng.randrange(0, wait_hi), rng.randrange(0, burst_hi)))
    return q, num_tasks


def test_hrrn_matches_old_on_random_queues():
    """New integer HRRN picks the same task as the old real HRRN."""
    rng = random.Random(20260728)
    for _ in range(20000):
        n = rng.randrange(0, MAX_TASKS + 1)
        q, n = _rand_queue(rng, n, 1 << 12, 1 << 10)
        assert _hrrn_new(q, n) == _hrrn_old(q, n), q


def test_hrrn_matches_old_at_full_width():
    """Equivalence holds at the declared field widths, not just small values."""
    rng = random.Random(4242)
    for _ in range(20000):
        n = rng.randrange(0, MAX_TASKS + 1)
        q, n = _rand_queue(rng, n, 1 << DEADLINE_WIDTH, 1 << BURST_TIME_WIDTH)
        assert _hrrn_new(q, n) == _hrrn_old(q, n), q


def test_hrrn_products_fit_declared_width():
    """HRRN_PROD_W must hold the widest possible cross-product.

    Guards the localparams added to advanced_task_scheduler.sv: if either
    product could wrap, the comparison would silently invert.
    """
    hrrn_num_w = max(DEADLINE_WIDTH, BURST_TIME_WIDTH) + 1
    hrrn_prod_w = hrrn_num_w + BURST_TIME_WIDTH
    max_wait = (1 << DEADLINE_WIDTH) - 1
    max_burst = (1 << BURST_TIME_WIDTH) - 1
    assert max_wait + max_burst < (1 << hrrn_num_w)
    assert (max_wait + max_burst) * max_burst < (1 << hrrn_prod_w)


def test_hrrn_ties_keep_first_index():
    """Strict `>` in both forms means the lowest index wins a tie."""
    q = [(10, 5)] * MAX_TASKS
    assert _hrrn_new(q, 8) == 0 == _hrrn_old(q, 8)


def test_hrrn_zero_burst_tasks_are_skipped():
    """burst_time == 0 is ineligible in both forms (it is also the div-by-0)."""
    q = [(99, 0), (99, 0), (1, 7)] + [(0, 0)] * (MAX_TASKS - 3)
    assert _hrrn_new(q, 3) == 2 == _hrrn_old(q, 3)


def test_hrrn_all_ineligible_returns_zero():
    """No eligible task -> index 0, matching the old max_ratio = 0.0 seed."""
    q = [(5, 0)] * MAX_TASKS
    assert _hrrn_new(q, 4) == 0 == _hrrn_old(q, 4)
    assert _hrrn_new(q, 0) == 0 == _hrrn_old(q, 0)


def test_hrrn_float_and_integer_forms_cannot_diverge_at_declared_widths():
    """The rewrite is exactly equivalent, not merely equivalent in practice.

    Two DISTINCT response ratios are rationals over burst_time denominators,
    so they differ by at least 1 / (b_i * b_j).  float64 compares them equal
    only if that gap falls under about one ulp of their magnitude R.  Taking
    b_i <= b_j, the larger ratio is bounded by R <= 1 + W / b_i where
    W = 2**DEADLINE_WIDTH, so divergence would require

        1 / (b_i * b_j)  <  (W / b_i) * 2**-52
                    <=>   b_j  >  2**52 / W  =  2**(52 - DEADLINE_WIDTH)

    i.e. a burst_time denominator wider than the field can hold, since
    b_j < 2**BURST_TIME_WIDTH.  The condition is therefore just

        BURST_TIME_WIDTH + DEADLINE_WIDTH < 52      (here 16 + 32 = 48)

    This test asserts that bound, so it FAILS if someone widens the fields
    far enough to make float division genuinely lossy -- at which point the
    integer form is strictly more correct, and the old `real` code would
    have been wrong as well as unsynthesisable.  A 4-bit margin remains.
    """
    assert BURST_TIME_WIDTH + DEADLINE_WIDTH < 52, (
        "float64 can no longer separate adjacent HRRN ratios at these widths; "
        "the integer cross-multiplication is now strictly more correct")


# ---------------------------------------------------------------------------
# BatchDNN / BatchDNN++: dynamic-start loop vs static loop + inner window
# ---------------------------------------------------------------------------

def _window_old(start, stop):
    """`for (int l = start; l <= stop; l++)` -- runtime start bound."""
    return [l for l in range(start, stop + 1)]


def _window_old_pp(start, stop):
    """BatchDNN++ variant: `l <= stop && l < MAX_LAYERS`, dynamic start."""
    out, l = [], start
    while l <= stop and l < MAX_LAYERS:
        out.append(l)
        l += 1
    return out


def _window_new(start, stop):
    """`for (int l = 0; l < MAX_LAYERS; l++) if (l >= start && l <= stop)`."""
    return [l for l in range(MAX_LAYERS) if start <= l <= stop]


def test_batchdnn_window_equivalent_in_range():
    """Identical iteration set and order for every in-range (start, stop)."""
    for start in range(MAX_LAYERS):
        for stop in range(MAX_LAYERS):
            assert _window_new(start, stop) == _window_old(start, stop), (start, stop)


def test_batchdnn_pp_window_equivalent_in_range():
    for start in range(MAX_LAYERS):
        for stop in range(MAX_LAYERS):
            assert _window_new(start, stop) == _window_old_pp(start, stop), (start, stop)


def test_batchdnn_window_empty_when_start_exceeds_stop():
    """A popped sub-batch ahead of the current layer iterates zero times."""
    assert _window_new(9, 4) == [] == _window_old(9, 4)


def test_batchdnn_new_window_never_indexes_past_the_table():
    """The static bound also removes an out-of-bounds read the old form had.

    LAYER_ID_WIDTH = 8 can express layer ids up to 255 while sched_table
    holds only MAX_LAYERS = 32, so the old loop could read past the end.
    """
    max_layer_id = (1 << LAYER_ID_WIDTH) - 1
    idxs = _window_new(0, max_layer_id)
    assert idxs and max(idxs) == MAX_LAYERS - 1
    assert max(_window_old(0, max_layer_id)) == max_layer_id      # old: OOB
    assert all(0 <= l < MAX_LAYERS for l in _window_new(30, max_layer_id))


# ---------------------------------------------------------------------------
# The RTL text itself must stay free of the two constructs Vivado rejected
# ---------------------------------------------------------------------------

RTL = ROOT / "rtl" / "schedulers"


def _code_lines(path):
    """Source lines with `//` comments stripped, so prose is not matched."""
    out = []
    for line in path.read_text().splitlines():
        out.append(line.split("//", 1)[0])
    return out


def test_no_real_arithmetic_in_advanced_scheduler():
    """Finding 2 must not regress: `real` is simulation-only."""
    import re
    src = _code_lines(RTL / "advanced_task_scheduler.sv")
    hits = [(i + 1, l) for i, l in enumerate(src)
            if re.search(r"\breal\b|\bshortreal\b", l)]
    assert not hits, f"`real` reintroduced: {hits}"


def test_batchdnn_loops_have_static_bounds():
    """Finding 1 must not regress: every for-loop needs a static trip count."""
    import re
    for name in ("batchdnn_scheduler.sv", "batchdnn_pp_scheduler.sv"):
        for i, line in enumerate(_code_lines(RTL / name)):
            m = re.search(r"for\s*\(\s*(?:int|genvar)?\s*\w+\s*=\s*([^;]+);", line)
            if not m:
                continue
            init = m.group(1).strip()
            assert re.fullmatch(r"\d+|[A-Z_][A-Z0-9_]*(\s*-\s*\d+)?", init), (
                f"{name}:{i + 1} loop starts at runtime value {init!r} -- "
                f"Vivado cannot unroll this [Synth 8-3380]")
