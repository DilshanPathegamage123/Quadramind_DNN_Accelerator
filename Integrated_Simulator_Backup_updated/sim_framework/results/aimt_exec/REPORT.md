# AI-MT / BATCH-DNN / BATCH-DNN++ on real hardware — measured results

Every number in this report comes from **Verilator simulation of the RTL**
(`rtl/exec/` + `rtl/schedulers/`). No scheduler carries a hand-written speedup
factor. Reproduce with:

```bash
cd sim_framework && source .venv/bin/activate
./tb/exec/build_exec.sh                      # build the simulator
PYTHONPATH=. python scripts/run_aimt_eval.py --exp all
PYTHONPATH=. python scripts/gen_aimt_figs.py
```

---

## 1. Why the old framework showed no benefit

The three DNN-aware schedulers were **already implemented correctly** — each
drives an independent `mt_valid` and `ct_valid`, as the papers require. Three
things downstream destroyed that parallelism before it could pay:

| # | Where | What it did |
|---|---|---|
| 1 | `unified_scheduler_wrapper.sv` | Collapsed the concurrent `{mt_valid, ct_valid}` pair into a single tagged union that gives the CT priority — only one could be seen per cycle |
| 2 | `multi_dnn_top.sv:298-338` | Single-issue run-to-completion dispatch FSM (`D_IDLE → D_RUN → D_WAIT_DONE`), one task held until it retired |
| 3 | `single_dnn_top.sv:409-413` | `S_MEM → S_COMPUTE` strictly in sequence, so even within one layer the array idled through the entire memory phase |

Memory and compute could therefore never be in flight together — the one thing
AI-MT exists to do. A fourth issue made the benefit unmeasurable even in
principle: `software_ref.estimate_cycles` is a pure compute formula and
`bytes_loaded` was never converted into cycles, so **memory cost zero time**.
Hiding a zero-cost operation saves nothing.

The measured consequence was all five schedulers landing within one cycle of
each other (13,412 vs 13,413), while `run_full_eval.py`'s Exp 5 charts asserted
a 26–48% speedup from a hardcoded `SCHEDULER_MODEL` lookup table.

## 2. What was built

New RTL in `rtl/exec/`, all synthesisable:

| Module | Role |
|---|---|
| `dram_model.sv` | Bandwidth- and latency-limited off-chip responder. Gives memory a real time cost: `latency + bytes/bandwidth`. Both knobs are runtime inputs. |
| `mt_engine.sv` | Memory Task engine — owns the off-chip port. `bytes = weight + batch × ifmap` (weights fetched once per batch). |
| `ct_engine.sv` | Compute Task engine — owns the systolic array. `cycles = compute × batch + fill_drain`. |
| `multi_dnn_exec_top.sv` | **Dual-issue** top: two independent dispatch channels that can both launch in the same cycle, plus per-layer completion accounting. |

`unified_scheduler_wrapper.sv` gained concurrent `mt_*_o` / `ct_*_o`
passthroughs (the legacy tagged union is untouched, so `multi_dnn_top` still
works), and the on-chip capacity/balance parameters are now plumbed through so
they can be swept.

**The baseline is fair.** Basic schedulers (FIFO/SJF) run on the *same*
machine, same engines, same DRAM — through a serial MT→CT channel. That is not
a handicap: a FIFO scheduler emits one undifferentiated task stream and has no
notion of a memory task to overlap. They are also *not* required to respect
layer dependencies, which if anything favours the baseline.

**Runs that do not finish are rejected, not credited.** `stat_layers_completed`
counts distinct layers retired; any run that wedges is flagged `incomplete` and
dropped from the comparison (Exp E keeps and marks them, because "did not
complete" is the finding there).

## 3. RTL defects found and fixed

Building the machine exposed four real bugs in the schedulers. Each produced a
*fast but wrong* result — a short cycle count for a run that had silently
dropped part of the workload — which is why they had gone unnoticed.

| # | Scheduler | Defect | Symptom |
|---|---|---|---|
| 1 | BATCH-DNN, ++ | `prev_batch` / `prev_batch_reg` reset to 0 and written only inside the dispatch path, but `max_batch_size()` clamps to it | `feasible_b` pinned at 0 → CT path stalled forever; every MT ran, then deadlock |
| 2 | all three | OFMAP reserved but never released; the batching pair reserved it *twice* (MT `mem_req` **and** CT dispatch) | `avail_mem` drained monotonically until the balance check failed permanently |
| 3 | BATCH-DNN, ++ | `ct_cq_cnt` / `sct_cnt` used a raw `+1`/`-1` pair; a same-edge enqueue+pop lost the enqueue to last-assignment-wins | Layers stranded in the queue — BATCH-DNN finished 8 of 12 |
| 4 | BATCH-DNN++ | `layer_distance()` compares **global** layer indices, but `ct_current_layer[]` reset to 0 | Any DNN whose first layer index > `MAX_LAYER_DISTANCE` (5) was throttled forever — an entire network never ran |

Fix 3 is the "finding F7" pattern that had already been applied to `mt_cq` but
never extended to the other two queues. A fifth issue was a *parameter*, not a
bug: `MAX_DNNS` defaults to 4 while Workload mix 6 co-schedules six networks,
so per-DNN state was indexed out of range; the testbench now elaborates with
`MAX_DNNS = 8`.

### A second class: stale dispatch selection

Running the multi-DNN TF-golden test across **all 14** schedulers (not the 5 it
previously covered) exposed a second, independent defect class. Every instance
is the same mistake: *something re-selects while a task is already in flight*.
Because `removing_id` tracks the live scheduler output and the queue removal
searches for it, the wrong task gets removed — the running one survives and is
re-dispatched, while a task that never ran is deleted and starves.

| # | Where | Defect | Symptom |
|---|---|---|---|
| 5 | `task_scheduler.sv` | Dispatch lock gated on `is_non_preemptive`, so RR and LRU were never locked | RR dispatched 0→2→0, LRU 0→0→1, both hitting the 200,000-cycle cap; starved task's output garbage (LRU 100% FS error) |
| 6 | `advanced_task_scheduler.sv` | Re-ran `schedule_*()` every cycle without checking its own `task_running` flag | HRRN (ratio changes every cycle as `wait_time` increments) dispatched 0→0→2 and hit the cap |
| 7 | `task_scheduler.sv` | LRU access touch sits after compaction in the same `always_ff`; on a removal edge it stamped the entry that had just shifted down | LRU order 0→2→1 instead of 0→1→2 — an innocent neighbour marked most-recently-used |
| 8 | `task_scheduler.sv` | RR quantum rotation ran mid-task, but the quantum cannot preempt here; a ~4,400-cycle task expires a 10-cycle quantum hundreds of times | `rr_ptr` left at an arbitrary offset — RR came out 0→2→1, skipping a task |
| 9 | `multi_dnn_exec_top.sv` | Basic FSM returned `B_RETIRE → B_IDLE` on the same cycle `task_complete` was presented, re-latching the stale offer | FIFO ran 13 tasks for a 12-layer mix; HRRN additionally starved a layer |

Policies whose selection key is *static* (SJF, SRTF, MLQ, MLFQ) re-selected the
same task each cycle and so were unaffected — which is why only three of the
fourteen failed and why the defects survived the five-scheduler test.

Result: **14/14 pass the TF-golden test, and 14/14 match the analytical model's
predicted dispatch order** (`results/golden_check/multi_dnn_golden_all14.csv`).
Measured makespan spread across all 14 is 1 cycle (13,412–13,413).

Guarded by `tb/unit/test_dnn_scheduler_exec.py` (10 tests, skips cleanly when
the simulator is not built).

## 4. Results

### A — Scheduler comparison (batch 1, 64 B/cycle DRAM)

![A](figures/A_speedup_and_utilisation.png)

| Mix | mem/compute | FIFO | AI-MT | Speedup | Array util FIFO → AI-MT |
|---|---|---|---|---|---|
| 1 | 1.19 | 129,104 | 77,496 | **1.67×** | 46% → 76% |
| 2 | 0.85 | 156,188 | 96,531 | **1.62×** | 54% → 87% |
| 3 | 0.61 | 322,042 | 229,100 | **1.41×** | 62% → 87% |
| 4 | 2.29 | 217,949 | 152,393 | **1.43×** | 30% → 44% |
| 5 | 0.33 | 176,686 | 147,306 | **1.20×** | 75% → 90% |
| 6 | 0.62 | 347,913 | 264,389 | **1.32×** | 62% → 81% |

All six mixes complete on **all 14 schedulers**, no rejections. FIFO, SJF and
RR are bit-identical per mix, as they must be: on the serial channel the order
cannot change the total, which is the single-issue makespan invariance showing
through.

> **These numbers superseded an earlier, slightly higher set** (1.45× on mix 3,
> 1.66× on mix 4). The baseline was inflated: the basic dispatch FSM re-latched
> a stale offer after `task_complete` and re-ran one task per mix, so FIFO paid
> for 13 tasks on a 12-layer workload. Fixed (`B_ACK` state); every speedup here
> is against the corrected, faster baseline.

### B — The mechanism

![B](figures/B_timeline_mechanism.png)

FIFO strictly alternates DMA and array (0% overlap, visible bubbles). AI-MT
runs both engines together — 41% of cycles have a memory task and a compute
task in flight simultaneously, and the array stops idling through prefetch.

### C — Speedup vs arithmetic intensity (the falsifiable test)

![C](figures/C_arithmetic_intensity.png)

Sweeping DRAM bandwidth 8→512 B/cycle moves the mix from memory-bound to
compute-bound. Speedup **peaks where the two resources are balanced** and
decays in both directions:

| mem/compute | 4.88 | 2.44 | 1.22 | 0.61 | 0.31 | 0.15 | 0.08 |
|---|---|---|---|---|---|---|---|
| AI-MT speedup | 1.12 | 1.22 | 1.38 | **1.41** | 1.28 | 1.15 | 1.07 |
| overlap % | 12.0 | 22.4 | 37.6 | **40.5** | 28.2 | 14.4 | 7.3 |

This is the result that proves the numbers are not a lookup table: a hardcoded
1.26 cannot bend. Both limits behave correctly — nothing to hide when
compute-bound, nothing to hide *behind* when memory-bound.

### D — Batch sweep

![D](figures/D_batch_sweep.png)

Batching is **inert at B=1** (all three identical, reproducing the original
golden observation) and grows with B. At B=16 BATCH-DNN moves 66.8 MB against
AI-MT's 124.8 MB — **1.87× less off-chip traffic for identical compute**.
BATCH-DNN++ separates from BATCH-DNN at B=16 (1.62× vs 1.54×) where batch
slicing engages.

### E — On-chip capacity

![E](figures/E_capacity_sweep.png)

At 24 MB, BATCH-DNN++ needs 541,614 cycles against AI-MT's 1,001,330 — **1.85×**
— because adaptive batching adapts and AI-MT cannot. Past ~32 MB capacity stops
binding and the three converge. Below 24 MB the batching schedulers deadlock
(see limitations).

## 5. Limitations — read before quoting these numbers

- **Compute is modelled as occupancy, not arithmetic.** `ct_engine` holds the
  array for the cycle count the scheduling table declares; it does not perform
  MACs. Functional correctness of the datapath is covered by the existing
  golden tests, not by this harness. These are *scheduling* results.
- **`compute_cycles` comes from `software_ref.estimate_cycles`**, the
  framework's existing analytical array model — a rank score, per
  `GOLDEN_CHECK_SUMMARY.md` §7, not a validated cycle prediction. Speedup
  *ratios* are far more trustworthy than absolute cycle counts.
- **BATCH-DNN / ++ deadlock below ~24 MB at batch 4.** Sub-batch splitting acts
  on the CT dispatch path only; the MT path still requires the *full* batch
  footprint to fit before it will start, so it cannot split its way out of a
  buffer smaller than one full-batch layer. AI-MT degrades gracefully there.
  This is a real limitation of the implementations, left unfixed and reported
  rather than hidden.
- ~~RR is excluded~~ and ~~FIFO dispatches 13 tasks for 12 layers~~ — **both
  fixed.** They were two faces of one defect class: a scheduler or dispatcher
  re-selecting while a task was already in flight. Four fixes now cover it —
  an unconditional dispatch lock in `task_scheduler.sv`, a `!task_running`
  gate in `advanced_task_scheduler.sv`, an `!removing` guard on the LRU access
  touch, and a `B_ACK` handshake state in this top. All 14 schedulers retire
  every layer and dispatch exactly one task per layer.
- **No Vivado.** Area/power/Fmax for the new engines are not measured; only
  cycles are.
- `run_full_eval.py`'s Exp 5 still uses the hardcoded `SCHEDULER_MODEL`. It was
  left untouched so the existing report keeps building; these results supersede
  it and live in a separate tree.
