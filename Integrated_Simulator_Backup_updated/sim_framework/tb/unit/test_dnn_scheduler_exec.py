"""Regression guards for the DNN-aware schedulers on the dual-issue machine.

These run the real Verilator build (rtl/exec + rtl/schedulers) rather than a
model, so they lock in behaviour that four separate RTL defects used to break.
Each defect below silently produced a WRONG-BUT-PLAUSIBLE result -- a fast
cycle count for a run that had quietly dropped half the workload -- which is
exactly the failure mode worth a permanent test.

  1. prev_batch / prev_batch_reg were never seeded, so max_batch_size() clamped
     the feasible batch to 0 and the CT path stalled forever.
  2. OFMAP was reserved but never released (twice over in the batching
     schedulers), draining avail_mem until the balance check failed for good.
  3. ct_cq_cnt / sct_cnt took a raw +1 / -1 pair, so a same-edge enqueue and
     pop lost the enqueue and stranded layers in the queue.
  4. BATCH-DNN++ measured layer distance on GLOBAL indices against a
     ct_current_layer that reset to 0, throttling any DNN whose first layer sat
     beyond MAX_LAYER_DISTANCE -- a whole network never ran.

The suite skips (does not fail) when the simulator has not been built, so the
default no-Verilator environment stays green.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

FW = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(FW))

CAPACITY = 46137344
BAL = 1000
BINARY = FW / "build" / f"exec_sim_{CAPACITY}_{BAL}" / "exec_sim"

FIFO, AIMT, BATCHDNN, BATCHDNN_PP = 0, 11, 12, 13

pytestmark = pytest.mark.skipif(
    not BINARY.exists(),
    reason=f"exec simulator not built ({BINARY.relative_to(FW)}); "
           f"run tb/exec/build_exec.sh",
)


def _workload(tmpdir: Path, mix_label: str = "Workload mix 3",
              batch: int = 1, dram_bw: int = 64) -> Path:
    from scripts.aimt_workload_gen import build_table, mix_by_label, write_table
    rows = build_table(mix_by_label(mix_label), dram_bw=dram_bw, batch=batch)
    return write_table(rows, tmpdir / "wl.txt")


def _run(wl: Path, sched: int, tmpdir: Path, dram_bw: int = 64) -> dict:
    out = tmpdir / f"run_{sched}.json"
    subprocess.run(
        [str(BINARY), f"+sched={sched}", f"+workload={wl}", f"+json={out}",
         f"+dram_bw={dram_bw}", "+timeout=40000000"],
        capture_output=True, text=True, timeout=1800, check=False)
    assert out.exists(), f"simulator produced no JSON for sched={sched}"
    return json.loads(out.read_text())["stats"]


@pytest.fixture(scope="module")
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture(scope="module")
def runs(tmpdir):
    wl = _workload(tmpdir)
    return {s: _run(wl, s, tmpdir)
            for s in (FIFO, AIMT, BATCHDNN, BATCHDNN_PP)}


@pytest.mark.parametrize("sched,name", [
    (FIFO, "FIFO"), (AIMT, "AI-MT"),
    (BATCHDNN, "BATCH-DNN"), (BATCHDNN_PP, "BATCH-DNN++"),
])
def test_every_scheduler_retires_the_whole_workload(runs, sched, name):
    """Defects 1-4 all manifested as layers silently never being computed."""
    st = runs[sched]
    assert not st["incomplete"], f"{name} wedged with layers outstanding"
    assert not st["timed_out"], f"{name} hit the cycle cap"
    assert st["layers_completed"] == st["layers_expected"], (
        f"{name} retired {st['layers_completed']}/{st['layers_expected']} layers")


def test_dnn_aware_schedulers_overlap_memory_and_compute(runs):
    """The whole point: MT and CT in flight simultaneously."""
    for sched, name in ((AIMT, "AI-MT"), (BATCHDNN, "BATCH-DNN"),
                        (BATCHDNN_PP, "BATCH-DNN++")):
        assert runs[sched]["overlap_cycles"] > 0, f"{name} never overlapped"


def test_basic_scheduler_cannot_overlap(runs):
    """FIFO runs the serial MT->CT channel, so overlap must be exactly zero.

    If this ever becomes non-zero the baseline has silently gained the very
    capability it is supposed to lack, and every speedup number is understated.
    """
    assert runs[FIFO]["overlap_cycles"] == 0


def test_dnn_aware_beats_the_serial_baseline(runs):
    fifo = runs[FIFO]["total_cycles"]
    for sched, name in ((AIMT, "AI-MT"), (BATCHDNN, "BATCH-DNN"),
                        (BATCHDNN_PP, "BATCH-DNN++")):
        assert runs[sched]["total_cycles"] < fifo, f"{name} did not beat FIFO"


def test_array_utilisation_improves(runs):
    """Overlap should show up as the array idling less, not just fewer cycles."""
    assert runs[AIMT]["array_utilization_pct"] > \
           runs[FIFO]["array_utilization_pct"] + 10.0


def test_batching_reduces_to_aimt_at_unit_batch(runs):
    """At batch 1 sub-batching and slicing are inert, so all three coincide.

    This is the property the pre-existing golden runs already showed, and it is
    the cheapest way to catch a batching scheduler that has started doing
    something at B=1 that it should not.
    """
    assert runs[BATCHDNN]["total_cycles"] == runs[AIMT]["total_cycles"]
    assert runs[BATCHDNN_PP]["total_cycles"] == runs[AIMT]["total_cycles"]


def test_batching_amortises_weight_traffic(tmpdir):
    """At B=4 the batching schedulers must move strictly less data than AI-MT.

    AI-MT has no batching mechanism, so it reloads weights per inference: its
    table scales the footprints by B at batch 1.  BATCH-DNN loads them once.
    """
    from scripts.aimt_workload_gen import build_table, mix_by_label, write_table
    B = 4
    mix = mix_by_label("Workload mix 3")

    serial = build_table(mix, dram_bw=64, batch=1, ai_scale=float(B))
    for r in serial:
        r["compute_cycles"] *= B
    wl_serial = write_table(serial, tmpdir / "wl_serial.txt")
    wl_batched = write_table(build_table(mix, dram_bw=64, batch=B),
                             tmpdir / "wl_batched.txt")

    aimt = _run(wl_serial, AIMT, tmpdir)
    bdnn = _run(wl_batched, BATCHDNN, tmpdir)

    assert not aimt["incomplete"] and not bdnn["incomplete"]

    # Strictly less weight traffic -- the batching benefit.
    assert bdnn["bytes_moved"] < aimt["bytes_moved"]

    # ...for the SAME compute.  Note `inferences` is NOT the comparable field
    # here: it counts dispatched batch slots, so the batched encoding reports
    # 48 while the serial encoding folds B into each layer's cost and reports
    # 12.  Array-busy cycles is the invariant that actually says "same work".
    assert abs(bdnn["ct_busy_cycles"] - aimt["ct_busy_cycles"]) \
        <= 0.01 * aimt["ct_busy_cycles"]
