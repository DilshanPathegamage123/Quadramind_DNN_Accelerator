# Scheduler-Chooser Report — analytical multi-DNN scheduler selection

**Date:** 2026-07-28 · **Branch:** `feature/scheduler-chooser` (branched off
the verified tip `1d160b6` on `fix/chooser-accuracy`) · **Module:**
`pysim/scheduler_chooser.py` · **CLI:** `scripts/choose_scheduler.py` ·
**Synthesis harness:** `scripts/synth_scheduler_hw.py` · **Evaluation:**
`scripts/eval_sched_chooser.py` · **Tests:**
`tb/unit/test_scheduler_chooser.py`

Given a multi-DNN workload mix, a fixed array size and a memory provision,
the chooser scores **all 14 schedulers the RTL implements**, ranks them by a
user-chosen goal, and returns the best scheduler plus the full ranked table.
No RTL and no synthesis is run per query. **No number is invented** — every
value is either computed by reused validated formulas (**model**), quoted
from real Vivado synthesis (**measured**), quoted from the recorded
Verilator golden runs (**measured (RTL)**), or arithmetic on those
(**derived**). Schedulers that do not synthesise carry **no** hardware
number; they are excluded from hardware goals rather than given a
substitute.

---

# FINDINGS — project-level, not chooser-specific

These four came out of building this framework but are **properties of the
project's RTL and assumptions**, not of the chooser. They are recorded here
so the team sees them; none of them is fixed on this branch (`feature/
scheduler-chooser`), per the agreed guardrail that RTL changes need their
own branch, Member 3's involvement, and a golden-check re-run.

> **STATUS UPDATE — Findings 1 and 2 are addressed on branch
> `fix/scheduler-synthesis`** (the separate branch the guardrail asked for).
> The unsynthesisable constructs have been rewritten; the rewrites are
> proven behaviour-preserving by `tb/unit/test_scheduler_synth_fix.py`
> (13 tests) and elaborate cleanly under `slang`.
>
> **Re-synthesised with the real tool** (Vivado 2025.2 had moved to
> `/vivado/2025.2`; the harness now discovers it instead of hardcoding a
> path). The table is now **13/14 measured**, up from 11/14:
>
> | Scheduler | Result | LUT | FF | DSP | Fmax |
> |---|---|---|---|---|---|
> | HRRN | now synthesises | 2,941 | 1,002 | 60 | 6.5 MHz |
> | BATCH-DNN | now synthesises | 4,657 | 6,529 | 10 | 10.7 MHz |
> | BATCH-DNN++ | still unmeasured | — | — | — | — |
>
> Three caveats, none of them cosmetic:
>
> 1. **HRRN is buildable but slow.** Exact integer ratio comparison infers
>    ~30 wide multipliers; it is the only scheduler consuming DSPs (60 of the
>    part's 240) and its Fmax collapses to 6.5 MHz, ranking it LAST on
>    `--goal turnaround_us`. This retires a real risk: HRRN wins 4 of 32
>    mix x goal cases on cycle-only timing, so a cycle-only analysis would
>    have recommended it.
> 2. **BATCH-DNN's 200 CRITICAL WARNINGs are NOT fixed.** They are on
>    `sched_table`'s `mem_access_done_flag` / `compute_done_flag`, driven by
>    both the table-load block and the main FSM — the *same* pathology as
>    Finding 3 (AI-MT, 164 warnings). Vivado keeps the constant driver and
>    ignores the real one, so 4,657 LUT is an honest measurement of a netlist
>    that does not faithfully implement the design. Fixing it needs an
>    ownership restructure of `sched_table`, which is its own piece of work.
> 3. **BATCH-DNN++ could not be measured on this machine.** Its RTL fixes are
>    in place and it elaborates cleanly, but Vivado needs ~12 GB to synthesise
>    it (measured by sampling: RAM peaked at 14.9/15 GB with swap fully
>    exhausted before the OOM kill). Four attempts, four OOM kills. Its CSV
>    row is marked `unavailable` with a STALE note rather than keeping the
>    last successful numbers, because that run predates the multi-driven-reset
>    fix and measured a netlist whose `current_batch` / `slice_remaining` were
>    tied to GND. Re-run on a machine with more swap.
>
> **No golden-check re-run has happened** — Verilator is still unavailable, so
> all three fixes rest on equivalence arguments plus Vivado DRC, not
> simulation. Findings 3 and 4 are untouched.

## Finding 1 — BATCH-DNN and BATCH-DNN++ are not synthesisable

Both modules fail Vivado synthesis outright:

```
ERROR: [Synth 8-3380] loop condition does not converge after 2000 iterations
    rtl/schedulers/batchdnn_scheduler.sv:370
    rtl/schedulers/batchdnn_pp_scheduler.sv:564
```

The cause is a loop whose **start bound is a runtime value**, so the tool
cannot unroll it — `batchdnn_scheduler.sv:370`:

```systemverilog
for (int l = resume_layer; l <= next_layer; l++) begin
```

`resume_layer` comes off the sub-batch stack and `next_layer` is a runtime
signal. BatchDNN++ carries a partial guard (`&& l < MAX_LAYERS`) and still
fails, because the *start* value is dynamic regardless.

**Two-tool corroboration.** Yosys 0.67 (via `yowasp-yosys`, used during
investigation before Vivado was located) also fails on both modules,
trapping the WASM runtime rather than completing. Two independent front
ends reject them.

**Impact.** These are two of Member 3's three flagship DNN-aware
schedulers. They simulate correctly — the golden runs at
`results/golden_check/raw/multi_BATCHDNN{,_PP}_8x8.json` pass with
`all_pass: true` — so this is **simulation-only RTL**, not broken
behaviour. But as written it cannot be built, and the chooser therefore
reports no area, power or Fmax for either.

**Suggested fix — APPLIED on `fix/scheduler-synthesis`:** bound the loop
statically and compare inside it, `for (int l = 0; l < MAX_LAYERS; l++) if
(l >= resume_layer && l <= next_layer) ...`, in both
`batchdnn_scheduler.sv` and `batchdnn_pp_scheduler.sv`. (BatchDNN++'s
pre-existing `l < MAX_LAYERS` guard was not sufficient — the *start* value
was the runtime `top.layer_idx`.) Iteration set and order are unchanged;
`tb/unit/test_scheduler_synth_fix.py` checks this exhaustively over all
32 x 32 in-range layer windows. The static bound additionally removes an
out-of-bounds `sched_table` read the old form allowed, since
`LAYER_ID_WIDTH = 8` expresses layer ids up to 255 while the table holds
`MAX_LAYERS = 32`. Still needs a golden-check re-run and re-synthesis.

## Finding 2 — HRRN is not synthesisable (floating-point in RTL)

```
ERROR: [Synth 8-27] real number expression not supported
    rtl/schedulers/advanced_task_scheduler.sv:180
```

`schedule_hrrn()` computes its response ratio in `real` (floating-point)
arithmetic:

```systemverilog
real max_ratio = 0.0;
current_ratio = real'(task_queue[i].wait_time + task_queue[i].burst_time)
              / real'(task_queue[i].burst_time);
```

`real` is simulation-only; it has no hardware mapping. **This one matters
for the chooser's own results**: HRRN wins 4 of the 32 evaluated
mix × goal cases on the timing metrics, so a cycle-only analysis would
recommend a scheduler that cannot be built. The CLI now prints an explicit
warning and names the best synthesisable alternative whenever this happens.

**Suggested fix — APPLIED on `fix/scheduler-synthesis`:** ratios are now
compared by cross-multiplication in integer arithmetic — `(wait_i +
burst_i) * burst_j > (wait_j + burst_j) * burst_i` — which is exact and
synthesisable. The running best is carried as a `(num, den)` pair, a
`found` flag reproduces the old `max_ratio = 0.0` seed, and strict `>`
preserves the original first-index-wins tie-break. Two `localparam`s size
the intermediates so neither the sum nor the products can wrap.

Worth flagging for whoever re-synthesises: exact ratio comparison needs
**two wide multipliers per queue slot** (~30 at `MAX_TASKS = 16`), of
33x16 bits. HRRN's measured area is therefore likely to come back
substantially above the other schedulers', and it may be the first to
consume DSP blocks (every scheduler currently reports `dsps = 0`). That is
a real cost of exact HRRN, not an artefact of the rewrite — the previous
`real` version simply never had a hardware cost to measure. If it proves
too expensive, the honest alternatives are a narrower saturating
`wait_time` or a multi-cycle comparison FSM, but both change behaviour and
so need Member 3 and a golden-check re-run.

## Finding 3 — AI-MT has multi-driven registers; the netlist ignores the real driver

AI-MT synthesises, but with **164 CRITICAL WARNINGs**, of this form:

```
CRITICAL WARNING: [Synth 8-6859] multi-driven net on pin Q with 1st driver
    pin 'sched_table_reg[31][mem_access_done_flag]__0/Q'
CRITICAL WARNING: [Synth 8-6859] multi-driven net on pin Q with 2nd driver pin 'GND'
CRITICAL WARNING: [Synth 8-6858] multi-driven net Q is connected to at least
    one constant driver which has been preserved, other driver is ignored
    rtl/schedulers/aimt_scheduler.sv:143
```

Vivado **kept the constant driver and discarded the real one**. AI-MT's
reported 3,417 LUT / 6,565 FF / 0.025 W are therefore real measurements of
a netlist that does **not** faithfully implement the simulated design. The
numbers are honest; what they are numbers *of* carries this caveat, and the
chooser's CSV records it in the `note` column.

This is the **same category** as the earlier F7 multi-driven-register
finding on this codebase. Two independent instances in the scheduler RTL
suggests a recurring pattern worth a dedicated cleanup pass rather than
another point fix.

## Finding 4 — the `CLOCK_GHZ = 1.0` assumption is ~9× optimistic (project-wide)

This affects **every throughput figure in the repository**, not just this
framework.

`scripts/run_full_eval.py:80` sets `CLOCK_GHZ = 1.0` ("assumed operating
frequency") and uses it for all throughput and GOPS numbers across
experiments 1–7. Real post-synthesis Fmax on the project's own target part
(`xc7a100tcsg324-1`, the part in `timing/vivado/synth_multi_dnn.tcl`):

| Scheduler | Fmax (MHz) | vs 1.0 GHz assumption |
|---|---|---|
| MLQ | 112.4 | 8.9× optimistic |
| LIFO | 111.1 | 9.0× |
| FIFO | 106.6 | 9.4× |
| RR | 93.4 | 10.7× |
| MLFQ | 90.9 | 11.0× |
| AI-MT | 86.7 | 11.5× |
| PRI | 41.7 | 24.0× |
| SRTF | 21.1 | 47.4× |
| SJF | 20.3 | 49.3× |
| LRU | 19.2 | 52.1× |
| EDF | 19.0 | 52.6× |

Even the fastest scheduler is **~9× below** the assumed clock, and these
are scheduler modules alone — the full `multi_dnn_top` including the
systolic array will not be faster than its slowest component. Published
throughput figures derived from `CLOCK_GHZ = 1.0` should be treated as
upper bounds that the hardware does not reach.

**Caveat, stated so the finding is not overclaimed:** these are
**post-synthesis** estimates from `opt_design`, with only the clock
constrained (so WNS reflects register-to-register paths inside the
scheduler). Placement and routing will reduce them further, not improve
them. Fmax is computed as `1000 / (constraint_ns − WNS)` at a 10 ns
constraint.

**A second-order consequence, which the chooser now surfaces:** the
comparator-tree policies (SJF, EDF, LRU, SRTF) buy fewer cycles at a ~5×
lower clock. On workload mix 3, SJF ranks **1st on cycle-turnaround and
9th on wall-clock turnaround** (4,457.8 µs vs MLQ's 985.6 µs). Any
scheduler comparison done in cycles alone inverts the real answer.

---

## 1. What exists, and where each number comes from

### 1.1 The 14 schedulers

| Select | Scheduler | RTL module |
|---|---|---|
| 0–6 | FIFO, LIFO, SJF, RR, PRI, EDF, LRU | `task_scheduler.sv` (`SCHEDULER_TYPE` 0–6) |
| 7–10 | SRTF, HRRN, MLQ, MLFQ | `advanced_task_scheduler.sv` |
| 11 | AI-MT | `aimt_scheduler.sv` |
| 12 | BATCH-DNN | `batchdnn_scheduler.sv` |
| 13 | BATCH-DNN++ | `batchdnn_pp_scheduler.sv` |

Muxed by `multi_scheduler_wrapper` (0–10) and `dnn_scheduler_wrapper`
(11–13) behind `unified_scheduler_wrapper`'s 5-bit select.

### 1.2 Reused cost logic (imported, not reinvented)

| Quantity | Source | Role |
|---|---|---|
| Per-task service cycles | `pysim.software_ref.estimate_cycles` | same estimator the config-chooser uses — **ranks**, does not predict absolute cycles |
| Memory-task cycles | `pysim.config_chooser.prefetch_traffic` | the structural prefetcher walk, RTL-exact on 10/10 recorded beat anchors |
| Area / power / Fmax | `scripts/synth_scheduler_hw.py` → Vivado 2025.2 | real out-of-context synthesis, cached |

The only genuinely new code is the **queueing discipline**, transcribed
from the RTL selectors — `task_scheduler.sv`'s combinational selector
(including the `is_non_preemptive` lock at line 91 and the first-index
tie-break), the four `advanced_task_scheduler.sv` policies, and the AI-MT
table walk. Zero fitted constants.

**`SCHEDULER_MODEL` is deliberately not used.** The hardcoded factor table
at `run_full_eval.py:295` (BATCHDNN_PP = 1.48× throughput, etc.) has no
derivation and no measurement behind it anywhere in the repo, and it is
workload-independent, so it would make `exp5_schedulers`-style rankings
identical for every mix by construction. The measured golden runs
contradict it directly (see §1.4). It is cited here once and never used to
compute a score.

### 1.3 Machine model — why run-to-completion

`multi_dnn_top`'s dispatch FSM holds a dispatched task until its
`task_complete` pulse, and the golden harness serves exactly one task at a
time. So although several RTL selectors are preemptive (RR, LRU, SRTF,
MLFQ re-decide every cycle), **preemption cannot manifest in this
integration**. The simulation applies each policy's selection rule at
dispatch points only. This is a property of the system, not a convenience
simplification, and it is why several policies produce identical orders.

### 1.4 Deliberately not modelled — and why

AI-MT's memory/compute overlap and BatchDNN's sub-batch pipelining are the
designed benefit of those schedulers. This integration serialises MT and
CT, and the measured golden runs show **all five schedulers within one
cycle** (13,412 vs 13,413). Modelling an overlap speedup would produce a
number no measurement in this project supports, so service time carries no
overlap term.

### 1.5 Makespan is provably not a discriminator here

On a **single machine that never idles while work is queued**, makespan is
identical for every scheduling order — including under staggered arrivals.
Reordering changes which task runs when, never total busy time nor the
forced idle waiting for an arrival.

An earlier draft of this plan claimed staggered arrivals would separate
schedulers on makespan. **That was wrong**, and it was caught by
`tb/unit/test_scheduler_chooser.py::test_makespan_invariant_under_staggered_arrivals_too`,
which now exists specifically to keep the claim from returning. `--goal
makespan` prints a warning saying so. The metrics scheduling actually moves
here are **turnaround** and **wait**, plus the scheduler's own measured
hardware cost.

---

## 2. Objective availability — stated explicitly

| Objective | Status | Label |
|---|---|---|
| Makespan | available but **provably an all-way tie** (§1.5) | model |
| Turnaround / wait (cycles) | available, discriminating | model |
| **Turnaround (µs, wall-clock)** | available, discriminating, **reverses the cycle ranking** | derived (model cycles ÷ measured Fmax) |
| Throughput | available; inverse of makespan × measured Fmax | derived |
| **Area (LUT/FF/DSP/BRAM)** | **available, real, 11/14** | measured (Vivado 2025.2 OOC) |
| **Power (W)** | **available, real, 11/14** | measured (Vivado vectorless, Medium confidence) |
| Fmax | available, real, 11/14 | measured (post-synthesis estimate) |
| Static power | reported **once**, not per scheduler | measured — device leakage (§2.1) |

### 2.1 Static power is not a per-scheduler number

Device static power is **0.084 W for every scheduler** — it is Artix-7
leakage, a property of the part, not of the design. Rolling it into a
per-scheduler total would make an 8× dynamic-power difference look like a
20% difference. The chooser ranks `--goal power` on **dynamic** power only
(0.008 W for MLQ up to 0.027 W for LRU) and reports static separately.

### 2.2 Power is vectorless, and what would improve it

Vivado reports `Confidence Level: Medium` and `Simulation Activity File:
---`, meaning toggle rates were estimated by vectorless propagation rather
than measured. This is a real Vivado estimate, it is cached, and it keeps
the CLI instant. **Available upgrade, not built:** dumping a SAIF from an
`xsim` run of the actual workload mix and feeding it to `report_power`
raises confidence to High and makes the number genuinely workload- and
activity-dependent. The plumbing is a per-(scheduler × mix) run; deferred
by agreement for v1.

---

## 3. The CLI

```
PYTHONPATH=. python scripts/choose_scheduler.py --mix mix3 --array 8x8 \
    --mem 256KB --goal turnaround_us
```

`--mix` accepts a named mix (`mix1`–`mix4` from `scripts/workloads.py`), a
comma-separated list of model directories, or a JSON file with per-task
`{name, layers|model_dir, arrival, priority, deadline}`. Other inputs:
`--array HxW`, `--mem`, `--dataflow OS|IS|WS`, `--goal`, `--weights`,
`--schedulers` (subset), `--csv`.

Example output (workload mix 3, 8×8, `--goal turnaround_us`):

```
RECOMMENDED: MLQ
  mean turnaround   : 110,781 cycles  (model)
  area              : 755 LUT / 490 FF  (measured, Vivado)
  dynamic power     : 0.008 W  (measured, Vivado vectorless)
  Fmax              : 112.4 MHz  (measured, post-synthesis estimate)
  turnaround (real) : 985.6 us  (derived: model cycles / measured Fmax)

  EXCLUDED from --goal turnaround_us (3 schedulers) -- no measured value
  exists, and none was substituted:
    HRRN: real number expression not supported [advanced_task_scheduler.sv:180]
    BATCHDNN: loop condition does not converge [batchdnn_scheduler.sv:370]
    BATCHDNN_PP: loop condition does not converge [batchdnn_pp_scheduler.sv:564]

  # scheduler    order       turnaround       wait    real us     LUT      FF   dyn W  Fmax MHz
  1 MLQ          0->1->2        110,781     44,244      985.6     755     490   0.008     112.4
  2 FIFO         0->1->2        110,781     44,244    1,039.2   1,501   1,050   0.011     106.6
  3 RR           0->1->2        110,781     44,244    1,186.1   1,594   1,070   0.013      93.4
  4 MLFQ         0->1->2        110,781     44,244    1,218.7   2,295   1,044   0.024      90.9
  5 AIMT         0->1->2        110,781     44,244    1,277.8   3,417   6,565   0.025      86.7
  6 LIFO         2->1->0        155,368     88,831    1,398.5   1,516   1,050   0.012     111.1
  7 PRI          2->1->0        155,368     88,831    3,725.9   1,663   1,050   0.020      41.7
  8 SRTF         1->0->2         90,493     23,956    4,288.8   1,854     490   0.018      21.1
  9 SJF          1->0->2         90,493     23,956    4,457.8   1,999   1,050   0.018      20.3
 10 LRU          0->1->2        110,781     44,244    5,769.9   3,035   1,594   0.027      19.2
 11 EDF          0->1->2        110,781     44,244    5,830.6   2,374   1,050   0.024      19.0
```

Note ranks 8–9: **SJF and SRTF have the best cycle-turnaround (90,493) and
the second-worst wall-clock turnaround.** That inversion is the single
most useful thing this framework produces, and it is only visible because
model timing and measured Fmax are combined.

**Tie reporting.** Exact ties are reported explicitly and broken by a
documented rule — mean turnaround, then mean wait, then makespan, then
scheduler name for determinism. When no timing metric separates a tied set
(schedulers producing an identical dispatch order are identical on all of
them), the CLI says exactly that and points the user at the measured
hardware columns, rather than implying a tie-break happened that did not.

---

## 4. Evaluation — five results

### (a) Decision accuracy — 32/32

For every mix × goal (4 mixes × 8 goals, minus goals with no rankable
candidate), the chooser's top pick equals the true best from an
independent exhaustive re-scoring pass: **32/32 (100%)**.

**Honesty note (same as the config-chooser's §4a):** the chooser *is*
exhaustive over 14 schedulers — exhaustive scoring is the correct
algorithm at this size. This check verifies argmin/sort consistency and
determinism, **not** a heuristic's luck. Data:
`eval_decision_accuracy.csv`.

### (b) Anchor A — dispatch order vs measured RTL: 5/5 exact

| Scheduler | Measured (RTL) | Model | Match |
|---|---|---|---|
| FIFO | T0→T1→T2 | T0→T1→T2 | exact |
| LIFO | T2→T1→T0 | T2→T1→T0 | exact |
| AI-MT | T0→T1→T2 | T0→T1→T2 | exact |
| BATCH-DNN | T0→T1→T2 | T0→T1→T2 | exact |
| BATCH-DNN++ | T0→T1→T2 | T0→T1→T2 | exact |

Source: `results/golden_check/raw/multi_*_8x8.json`. The replay uses the
**harness's declared synthetic attributes** (burst 10/20/30, priority
0/1/2, deadline 1000/2000/3000), because those — not the real cycle costs
— are what the RTL schedulers decide on. Data: `eval_anchor_order.csv`.

### (c) Anchor B — makespan flatness: PASS

| Quantity | Range | Spread |
|---|---|---|
| Measured total cycles (5 schedulers, RTL) | 13,412 – 13,413 | 0.0075% |
| Model makespan (14 schedulers) | 477 – 477 | 0.0000% |

The model reproduces the measured invariance instead of inventing a
speedup. **This is the check that would catch a fabricated performance
claim**, and it is the reason `SCHEDULER_MODEL`'s 1.26×/1.37×/1.48×
factors are not used. Data: `eval_anchor_flatness.csv`.

### (d) Sensitivity — 4 distinct schedulers recommended

Across 32 mix × goal cases the recommendation is **MLQ ×15, SJF ×12,
HRRN ×4, LIFO ×1** — it genuinely depends on workload and goal. (A chooser
that always returned BATCH-DNN++ would be the `SCHEDULER_MODEL`
constant-table failure mode reappearing.) MLQ wins the hardware goals
(smallest and fastest), SJF the cycle-timing goals, and the wall-clock goal
splits between them. Data: `eval_sensitivity.csv`.

### (e) Speed

| What | Time | Source |
|---|---|---|
| WARM scoring: 14 schedulers, one mix (median of 5; **excludes** one-time imports) | **0.2 ms** | measured |
| WARM: all 4 mixes × 14 schedulers | **1.9 ms** | measured |
| COLD CLI end-to-end (interpreter + imports + scoring + table + CSV; median of 3 subprocesses) | **1.07 s** | measured |
| Vivado synthesis per scheduler — **cached, not per query** | ~135 s | measured |

The synthesis cost is paid once by `scripts/synth_scheduler_hw.py`
(~25 min for all 14); queries read the cached CSV. Data: `eval_speed.csv`.

### (f) Unit tests — 21 passing

`tb/unit/test_scheduler_chooser.py` locks down each policy transcription,
the golden-order anchors, the makespan-invariance properties, and the
no-fabrication guarantee (missing hardware data must stay `None` and must
exclude rather than substitute). Runs without cocotb, Verilator or Vivado.

---

## 5. What cannot be anchored — stated plainly

1. **Absolute cycle counts.** `estimate_cycles` is a rank estimator. There
   is exactly one task in the golden mix where model and measurement are
   directly comparable — `tiny_cnn/layer_01` has a 1×1 output, so the
   harness's single-pixel invocation *is* the whole layer. There the model
   says **309 cycles** and the hardware measured **11,782** — a **38×**
   under-prediction, because the estimator models compute cycles while the
   measurement is dominated by the memory-delivery schedule. For the other
   two tasks the scopes differ (single pixel vs whole layer) and no
   comparison is possible. **There is no measured anchor for per-task
   service cost**, only for dispatch order and total cycles.
2. **The 9 unmeasured schedulers' behaviour.** Only FIFO, LIFO, AI-MT,
   BATCH-DNN and BATCH-DNN++ have recorded golden runs. SJF, RR, PRI, EDF,
   LRU, SRTF, HRRN, MLQ and MLFQ have **no measured dispatch behaviour** in
   this project; their orders are model predictions from the transcribed
   RTL selectors. (A standalone `unified_scheduler_wrapper` bench would
   close this; it was scoped out of v1.)
3. **MT/CT overlap.** Not observable in any recorded run, so not modelled
   (§1.4).
4. **Power in watts under real activity.** Vectorless only (§2.2).
5. **Post-route timing.** Fmax is post-synthesis (§ Finding 4).
6. **AI-MT's synthesised netlist fidelity.** See Finding 3.

---

## 6. Labels

- **measured (Vivado 2025.2 OOC):** LUT, FF, DSP, BRAM, power, WNS/Fmax —
  `results/sched_chooser/hw/scheduler_hw.csv`, raw reports under `hw/reports/`.
- **measured (RTL):** dispatch order and total cycles from
  `results/golden_check/`.
- **model:** makespan, turnaround, wait, dispatch orders for unmeasured
  schedulers. Never an absolute cycle prediction.
- **derived:** wall-clock turnaround, throughput, scheduler energy —
  arithmetic on model cycles and measured Fmax/power.
- **unavailable:** carries no number and states why.

## 7. Regression safety

Additions only. **No RTL, no golden harness, no `pysim/sim_config.py`, no
existing experiment result and no config-chooser file was modified.** The
golden regression outcome is unchanged by construction; it was **not**
re-run, because `run_golden.py` writes into `results/golden_check/raw/` and
re-running would overwrite recorded experiment results.

The synthesis harness distinguishes a **tool/environment failure** from a
genuine non-synthesising design and aborts loudly on the former — an early
version of this run recorded all 14 schedulers as "does not synthesise"
when the real cause was a space in the repository path, which would have
published a false finding about working RTL. Subset re-runs merge into the
cached table rather than truncating it.

## 8. Files

- `pysim/scheduler_chooser.py` — policy models + ranking
- `scripts/choose_scheduler.py` — CLI
- `scripts/synth_scheduler_hw.py` — Vivado synthesis harness (cached)
- `scripts/eval_sched_chooser.py` — the five evaluations
- `tb/unit/test_scheduler_chooser.py` — 21 regression tests
- `results/sched_chooser/hw/scheduler_hw.csv` — measured hardware table
- `results/sched_chooser/hw/reports/` — raw Vivado utilization/power/timing
- `results/sched_chooser/ranked_*.csv`, `eval_*.csv`
