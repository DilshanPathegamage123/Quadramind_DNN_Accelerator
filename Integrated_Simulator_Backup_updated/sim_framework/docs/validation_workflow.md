# Validation Workflow — how this framework is verified, end to end

**What this document is.** The complete verification story for the simulator:
every layer of checking that exists, what each one *proves*, what each one
**cannot** prove, how to run it, and the defect log showing which layer caught
what. It is written so that a reader can tell the difference between "this
passed" and "this is verified" — those are not the same claim, and most of the
value here is in the gap between them.

Companion documents: [`verification_matrix.md`](verification_matrix.md)
(auto-generated config sweep), [`architecture.md`](architecture.md) (RTL
hierarchy), [`scheduler_chooser_contribution.md`](scheduler_chooser_contribution.md)
(the analytical selector's own validation), and
[`../results/aimt_exec/REPORT.md`](../results/aimt_exec/REPORT.md) (dual-issue
scheduling results).

---

## 1. The five layers, and the honest scope of each

Verification here is a stack. Each layer answers a different question, and a
pass at one layer says nothing about the layers above it.

| # | Layer | Question it answers | What it CANNOT catch |
|---|---|---|---|
| 1 | **Analytical / unit** (pytest, 73 tests) | Do the Python models, transcribed selectors and bit-level helpers agree with their specs? | Anything about the RTL. No hardware runs. |
| 2 | **Single-DNN TF golden** (cocotb + Verilator) | Does the datapath compute the right numbers? | Scheduling. One DNN, one config at a time. |
| 3 | **Multi-DNN TF golden, 14 schedulers** | Does a scheduler change *order* without corrupting *results*? Does every task get dispatched? | Whether the scheduler's MT/CT decisions are used at all (see §5.3 — this is the important one). |
| 4 | **Dual-issue scheduling evaluation** | Do AI-MT / BATCH-DNN / BATCH-DNN++ deliver their designed benefit on hardware that can express it? | Numerical correctness — `ct_engine` models occupancy, not arithmetic. |
| 5 | **Synthesis** (Vivado) | Area, power, F<sub>max</sub>, timing closure. | **Not available in this environment.** |

The governing rule, applied throughout:

> **A run that does not finish the workload is rejected, not credited.**
> Three of the defects in §7 first appeared as a *fast* result — a short cycle
> count for a run that had silently dropped half its work. Completion is
> therefore checked explicitly, never inferred from "it terminated".

---

## 2. Toolchain provisioning

Neither simulator ships with the environment; both are obtainable without root.

| Tool | Status | How |
|---|---|---|
| **Verilator 5.050** | built from source | `tb/exec/build_exec.sh` honours `$VERILATOR_INSTALL`; build needs only gcc/g++/make/autoconf/flex/bison (all present). ~4 min with `-j12`. `help2man` is absent and only generates man pages — stub it. |
| **cocotb 2.0.1** | `pip install cocotb` | Required for layers 2 and 3 (VPI driver). |
| **TensorFlow** | **not required to verify** | Only needed to *regenerate* golden vectors. `expected.npy` is already committed under `models/`, so the compare runs without it. |
| **Vivado** | unavailable | Layer 5 is not executed. Area/power/F<sub>max</sub> figures elsewhere come from an earlier synthesis run and are flagged stale where they matter. |

```bash
export VERILATOR_INSTALL=/path/to/verilator-install
export PATH=$VERILATOR_INSTALL/bin:$PATH
cd sim_framework && source .venv/bin/activate && pip install cocotb
```

---

## 3. The golden-reference chain

This is the spine of layers 2 and 3 — where "correct" comes from.

```
   TensorFlow model  (models/dump_tf_model.py, pysim/tf_dump.py)
            │  float32 forward pass, per layer
            ▼
   models/<net>/layer_NN/
       input.npy  weights.npy  expected.npy      ← float reference
       input.hex  weights.hex  expected.hex      ← Q-format for $readmemh
       config.json  quant.json                   ← shape + frac bits
            │
            │  quantise to Qm.n  (frac_x = frac_w = 14 by default)
            ▼
   RTL simulation under Verilator + cocotb
            │  capture fixed-point outputs, divide by 2^(fx+fw)
            ▼
   compare:  |actual − expected| ≤ tol × full_scale        (tol = 0.05)
```

**Tolerance.** 5% of full scale, where full scale is `max(|expected|)` for that
layer. This is deliberately loose — it accommodates Qm.n rounding — and the
measured margin is large: single-DNN verification runs come in at **≤ 0.0499%
max relative error**, multi-DNN at **0.017% of full scale**. A regression would
have to be gross to be missed; a *subtle* numerical drift would pass unnoticed.
The tolerance is a smoke detector, not a precision instrument, and no claim
about numerical accuracy finer than ~5% should be made from a pass.

**ReLU.** For `mnist_cnn` layers the comparison applies ReLU to the captured
values, matching the TF layer's activation.

---

## 4. Layer 1 — Analytical and unit tests

```bash
PYTHONPATH=. python -m pytest tb/unit tb/integration tb/timing -q     # 73 tests
```

| Directory | Tests | Covers |
|---|---|---|
| `tb/unit` | 63 | PE smoke, bank-conflict model (17), scheduler-chooser transcription, synthesis-fix equivalence, dual-issue scheduler regressions (10) |
| `tb/integration` | 4 | `single_dnn_top` / `multi_dnn_top` smoke via the software reference |
| `tb/timing` | 6 | Cycle-budget bounds per dataflow |

Runs in ~7 s with no simulator: every test either exercises pure Python or
falls back to `pysim/software_ref.py`. `tb/golden/` is **excluded** from this
invocation — those files `import cocotb` at module scope and fail collection
without it.

`tb/unit/test_dnn_scheduler_exec.py` is the regression guard for the §7
scheduler defects. It runs the real Verilator build and **skips cleanly** when
that build is absent, so the default environment stays green.

---

## 5. Layers 2 and 3 — RTL against the TensorFlow golden

### 5.1 Single-DNN — full-tensor verification

```bash
python tb/golden/run_golden.py --layer models/tiny_cnn/layer_00 \
    --dataflow OS --layout CHANNEL_MAJOR --memory STAMP --array 8x8 --num-banks 4
```

Builds `single_dnn_top` and compares **every output element**. A representative
verdict (`results/golden_check/raw/*_verdict.json`):

```json
{ "n_total": 5408, "n_within_tol": 5408,
  "max_abs_err": 0.000183, "max_rel_err_pct": 0.0089,
  "assembly": "hardware_full", "passed": true }
```

**This is where datapath correctness is actually established** — full tensors
(up to 5,408 elements per layer), across dataflow (OS/IS/WS) × layout
(ROW/COLUMN/CHANNEL_MAJOR) × memory backend (STAMP/PAGED) × casting
(UNICAST/MULTICAST/HYBRID) × array geometry.

Read the verdict directory carefully — it contains two different kinds of file:

| Kind | Count | Status |
|---|---|---|
| **Verification runs** | 23 | all pass; worst relative error **0.0499%** against a 5% tolerance |
| **Diagnostic probes** (`*probe*` in the filename) | 7 | **FAIL by design** — retained triage experiments, not verification results |

The probes carry `assembly` values like `tb_sum_over_tuples` and
`f4_load_probe`; they were instrumentation used while chasing the layout and
casting bugs, and their failures are expected. A naive `all(passed)` over the
directory therefore reports False and means nothing — filter out `*probe*`
first.

**One caveat inside the 23.** The `assembly` field records how the final result
was assembled:

- **20 runs are `hardware_full`** — the RTL produced the complete output.
- **3 runs are `tb_sum_over_channels`** — all three WS (weight-stationary)
  configs at 8x1, 8x2 and 8x8, where the *testbench* performs the
  cross-channel reduction.

So WS's golden pass is **partially testbench-assisted** and is a weaker claim
than the OS/IS results. That is a known structural property of the WS harness,
not a defect, but it should not be quoted as full end-to-end hardware
verification of WS.

### 5.2 Multi-DNN — order, completion, and non-corruption across all 14 schedulers

```bash
for S in FIFO LIFO SJF RR PRI EDF LRU SRTF HRRN MLQ MLFQ \
         AIMT BATCHDNN BATCHDNN_PP; do
    PYTHONPATH=. python tb/golden/run_golden_multi.py --sched $S
done
```

Builds `multi_dnn_top` once and runs a 3-task mix under each scheduler:

| Task | Layer | Pixel | Channels |
|---|---|---|---|
| 0 | `tiny_cnn/layer_00` | (0,0) | 0..7 |
| 1 | `mnist_cnn/layer_00` | (1,1) | 0..7 (ReLU) |
| 2 | `tiny_cnn/layer_01` | (0,0) | 0..3 |

Current result — `results/golden_check/multi_dnn_golden_all14.csv`:

| | Value |
|---|---|
| Golden pass | **14 / 14** |
| Dispatch-order match vs analytical model | **14 / 14** |
| Max error | 0.017% of full scale (tol 5%) |
| Makespan spread | **1 cycle** (13,412 basic/advanced, 13,413 DNN-aware) |

Pre-fix artefacts are preserved in `results/golden_check/raw_prefix_backup/`.

**This is a spot check, and that is a deliberate division of labour.** It
verifies 20 scalar values per scheduler (8+8+4 channels of one pixel each), not
full tensors. That is acceptable *only because* §5.1 already verifies the
datapath exhaustively. This layer's job is different: prove the scheduler
changes **order** without changing **results**, and prove every task actually
runs.

### 5.3 The critical limitation of layer 3 — read before quoting a pass

In `multi_dnn_top` the dispatch FSM starts `single_dnn_top` on **any**
`sched_out.valid`, and `single_dnn_top` then runs `S_MEM → S_COMPUTE`
internally **regardless of whether the scheduler flagged that dispatch as a
memory or a compute task**.

Numerical correctness therefore comes from the datapath, not from the
scheduler's MT/CT decisions.

> **A passing multi-DNN golden run proves the datapath is right. It does not
> prove the scheduler is right.**

This is not hypothetical. BATCH-DNN and BATCH-DNN++ passed this test for a long
time while carrying defects that stopped them issuing compute tasks *at all* —
the pre-fix artefacts record `is_ct: [0,0,0]`, i.e. every logged dispatch was a
memory task. The two failure classes this layer *can* catch are a wrong
dispatch **order** and a task **never dispatched**, and that is exactly how RR,
LRU and HRRN were caught (§7).

A second caveat on the order check: on this 3-task mix **11 of the 14 policies
emit the identical order**, so order agreement is a weak discriminator. It is
genuinely informative for LIFO and PRI (which invert) and for detecting gross
failure. A mix with real reordering pressure is the outstanding gap.

---

## 6. Layer 4 — dual-issue scheduling evaluation

The layer that demonstrates the AI-MT / BATCH-DNN / BATCH-DNN++ benefit, on
hardware built to express it (`rtl/exec/`).

```bash
./tb/exec/build_exec.sh [onchip_bytes] [compute_bal_thresh]
PYTHONPATH=. python scripts/run_aimt_eval.py --exp all
PYTHONPATH=. python scripts/gen_aimt_figs.py
```

Four experiments over the six `SCHED_EVAL_MIXES` (per-layer scheduling tables
generated by `scripts/aimt_workload_gen.py` from the MLPerf-derived shapes in
`scripts/workloads.py`):

| Exp | Sweeps | Establishes |
|---|---|---|
| A | 6 mixes × 6 schedulers | Speedup and array utilisation vs a serial baseline |
| C | DRAM bandwidth 8→512 B/cyc | Overlap gain is **non-monotone**, peaking where memory and compute balance — the falsifiable prediction |
| D | batch 1→16 | Weight-reload amortisation; inert at B=1 by construction |
| E | capacity 16→128 MB | Adaptive batching pays only when memory is tight |

### 6.1 Two disciplines that make the numbers trustworthy

**Completion accounting.** `multi_dnn_exec_top` counts *distinct layers
retired* (`stat_layers_completed`), not `ct_done` pulses — the latter
over-counts, because BATCH-DNN legitimately splits one layer into several
sub-batch CTs. A run that wedges is flagged `incomplete` and **dropped from the
comparison**; Exp E keeps and marks such runs, because "did not complete below
X MB" is the finding there.

**A fair baseline.** Basic schedulers run on the *same* machine, engines and
DRAM, through a serial MT→CT channel. That is not a handicap: FIFO emits one
undifferentiated task stream and has no notion of a memory task to overlap.
They are also not required to respect layer dependencies, which if anything
favours the baseline.

### 6.2 What layer 4 does **not** verify

`ct_engine` holds the array for the declared cycle count; it performs no MACs.
**The dual-issue top has no functional verification.** Its results are
scheduling results. Closing this would mean instantiating a real datapath in
`ct_engine`'s place and golden-checking it — substantial, and not done.

---

## 7. Defect log — which layer caught what

Ten RTL fixes and one parameter correction, all found by running layers 3 and
4. Every one produced a *plausible* result before being caught.

### 7.1 Batching / DNN-aware scheduler defects — found by layer 4

| # | Where | Defect | Symptom |
|---|---|---|---|
| 1 | BATCH-DNN, ++ | `prev_batch`/`prev_batch_reg` reset to 0, written only inside the dispatch path, while `max_batch_size()` clamps to them | feasible batch pinned at 0 → CT path stalled forever |
| 2 | all three | OFMAP reserved but never released; batching pair reserved it **twice** (MT `mem_req` *and* CT dispatch) | `avail_mem` drained until the balance check failed permanently |
| 3 | BATCH-DNN, ++ | `ct_cq_cnt`/`sct_cnt` used raw `+1`/`-1`; a same-edge enqueue+pop lost the enqueue | layers stranded — BATCH-DNN finished 8 of 12 |
| 4 | BATCH-DNN++ | `layer_distance()` compares **global** layer indices against a `ct_current_layer[]` that resets to 0 | any DNN whose first layer index > `MAX_LAYER_DISTANCE` throttled forever — a whole network never ran |
| 5 | BATCH-DNN++ | Bottleneck Expedition re-queued a layer already waiting in `sct_q` | 17 CTs for a 12-layer mix — real duplicated compute |
| — | testbench | `MAX_DNNS` defaults to 4; mix 6 co-schedules **six** networks | per-DNN state indexed out of range — elaborate with `MAX_DNNS = 8` |

Defect 3 is the "finding F7" pattern already applied to `mt_cq` but never
extended to the other two queues.

### 7.2 Stale-dispatch defects — found by layer 3, once it covered all 14

One mistake in five places: *something re-selects while a task is already in
flight*. Because `removing_id` tracks the live scheduler output and the queue
removal searches for it, the **wrong task is removed** — the running one
survives and is re-dispatched, while a task that never ran is deleted.

| # | Where | Fix | Symptom before |
|---|---|---|---|
| 6 | `task_scheduler.sv` | dispatch lock made unconditional (was gated on `is_non_preemptive`, excluding RR and LRU) | RR 0→2→0, LRU 0→0→1, both capped at 200,000 cycles; LRU's starved task read **100% FS error** |
| 7 | `advanced_task_scheduler.sv` | re-selection gated on `!task_running` | HRRN 0→0→2, capped |
| 8 | `task_scheduler.sv` | LRU access touch guarded with `!removing` — it sat after compaction in the same `always_ff` and stamped the entry that had just shifted down | LRU order 0→2→1 |
| 9 | `task_scheduler.sv` | RR quantum rotation gated on `!is_locked` — the quantum cannot preempt here, yet a ~4,400-cycle task expires a 10-cycle quantum hundreds of times | RR order 0→2→1, skipping a task |
| 10 | `multi_dnn_exec_top.sv` | `B_ACK` state waits for the scheduler to withdraw its offer after `task_complete` | FIFO ran 13 tasks for a 12-layer mix; HRRN starved a layer |

Only policies whose **selection key mutates during a run** were affected (RR's
pointer, LRU's access time, HRRN's ratio). Static-key policies — SJF, SRTF,
MLQ, MLFQ — re-selected the same task each cycle and were unaffected, which is
why the five-scheduler version of layer 3 passed for years while three of the
fourteen were broken.

Defect 10 was in code written for layer 4 itself, and it had inflated the
baseline: every reported speedup was recomputed against the corrected, faster
FIFO (mix 3: 1.45× → **1.41×**).

### 7.3 The lesson worth carrying forward

Every one of these produced a **fast, plausible, passing-looking** result. The
things that actually caught them were: extending coverage from 5 policies to
all 14, and refusing to credit a run that had not finished its workload. Neither
is clever; both are just discipline.

---

## 8. Coverage — what is verified and what is not

| Property | Status | Evidence |
|---|---|---|
| Datapath numerical correctness — **OS / IS** (× layout × STAMP/PAGED × casting) | **Verified**, full tensors, `hardware_full` | 20 of 23 verdicts |
| Datapath numerical correctness — **WS** | **Partially verified** — testbench performs the cross-channel reduction | 3 verdicts, `assembly = tb_sum_over_channels` |
| Scheduler does not corrupt results | **Verified**, spot check | 14/14, `multi_dnn_golden_all14.csv` |
| Every task dispatched exactly once | **Verified** | dispatch-order + completion counters |
| Analytical selector matches RTL order | **Verified on one mix**, 14/14 | §5.2 — but 11/14 policies coincide there |
| Makespan invariance on the single-issue machine | **Verified** | 1-cycle spread across 14 |
| Dual-issue scheduling benefit | **Measured** | `results/aimt_exec/` |
| Dual-issue numerical correctness | **NOT verified** | `ct_engine` is an occupancy model (§6.2) |
| Rank correlation model ↔ RTL across mixes | **NOT computed** | needs 14 × 6 runs; now executable |
| Area / power / F<sub>max</sub> | **Stale** | pre-dates §7 fixes; Vivado unavailable |
| Absolute cycle-count fidelity | **NOT claimed** | `estimate_cycles` is a rank score (`GOLDEN_CHECK_SUMMARY.md` §7) |

---

## 9. Full reproduction sequence

```bash
cd sim_framework && source .venv/bin/activate
export PATH=$VERILATOR_INSTALL/bin:$PATH
pip install cocotb                        # layers 2-3 only

# Layer 1 — no simulator needed (~7 s)
PYTHONPATH=. python -m pytest tb/unit tb/integration tb/timing -q

# Layer 2 — single-DNN, full-tensor golden
python tb/golden/run_golden.py --layer models/tiny_cnn/layer_00 --array 8x8

# Layer 3 — multi-DNN golden, all 14 schedulers
for S in FIFO LIFO SJF RR PRI EDF LRU SRTF HRRN MLQ MLFQ \
         AIMT BATCHDNN BATCHDNN_PP; do
    PYTHONPATH=. python tb/golden/run_golden_multi.py --sched $S
done

# Layer 4 — dual-issue scheduling evaluation
./tb/exec/build_exec.sh
PYTHONPATH=. python scripts/run_aimt_eval.py --exp all
PYTHONPATH=. python scripts/gen_aimt_figs.py

# Config sweep + report regeneration
PYTHONPATH=. python scripts/iterate_until_pass.py
python scripts/gen_report.py

# RTL lint
$VERILATOR_INSTALL/bin/verilator --lint-only -Wno-fatal \
    --top-module multi_dnn_top rtl/pkg/*.sv rtl/schedulers/*.sv rtl/tops/*.sv \
    rtl/array/*.sv rtl/pe/*.sv rtl/fetchers/*.sv rtl/memory/*.sv rtl/interfaces/*.sv
```

Regenerating golden vectors (only after a model change) additionally needs
TensorFlow:

```bash
python models/dump_tf_model.py --model tiny_cnn --out models/tiny_cnn
```

---

## 10. Open work, in priority order

1. **A reordering-heavy multi-DNN golden mix.** The current 3-task mix has 11
   of 14 policies producing the same order, so the 14/14 agreement mostly
   proves absence of gross failure. This is the single highest-value gap.
2. **14 policies × 6 mixes under Verilator** → decision accuracy and Spearman
   ρ for the analytical selector (`scheduler_chooser_contribution.md` §7.3).
   Now executable; falsifier stated in advance there.
3. **Functional verification for the dual-issue top** — instantiate a real
   datapath in place of `ct_engine` and golden-check it.
4. **Re-synthesise** the scheduler hardware table; every DNN-aware row
   pre-dates the §7 fixes.
5. **Widen the multi-DNN golden to full tensors** rather than one pixel per
   task.
6. **Activity-annotated power**, replacing Vivado's vectorless estimate.
