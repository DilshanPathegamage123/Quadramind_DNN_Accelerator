# Analytical Scheduler Selection for a Multi-DNN Accelerator

**Status of this document.** It states the scientific claim of the scheduler
section, gives the algorithm formally, and reports exactly how much of the
claim is currently backed by measurement. The validation section
distinguishes what has been verified from what has not; the unverified parts
are named as such rather than left implied.

Implementation: [`pysim/scheduler_chooser.py`](../pysim/scheduler_chooser.py),
[`scripts/choose_scheduler.py`](../scripts/choose_scheduler.py),
[`scripts/sched_objective_matrix.py`](../scripts/sched_objective_matrix.py).

> **Revision note — the accelerator this document models is now one of two.**
> Every claim below is scoped to the **single-issue** integration
> (`rtl/tops/multi_dnn_top.sv`), which dispatches one task at a time and holds
> it to completion. A second execution top,
> **`rtl/exec/multi_dnn_exec_top.sv`**, now exists: it is *dual-issue*, with
> independent memory and compute engines that can both be busy in the same
> cycle. On that machine several conclusions here **invert** — most
> importantly §9.2, the limitation that this framework cannot demonstrate the
> AI-MT / BATCH-DNN benefit. It can now, and does; see
> [`results/aimt_exec/REPORT.md`](../results/aimt_exec/REPORT.md).
> The chooser itself is unchanged and still models the single-issue machine.
> Findings F1 and F3 are therefore properties of *that* machine, not of
> scheduling in general, and are labelled accordingly.

---

## 1. The claim

> Given a multi-DNN workload and an optimisation objective, the scheduling
> policy that best serves that objective on a fixed accelerator can be
> selected at design time by an analytical model, in milliseconds, without
> RTL simulation and without invoking synthesis per query — and the
> selection agrees with the behaviour the synthesised RTL actually exhibits.

Two halves. The first (cost) is measured and settled. The second
(agreement) is partially measured; §7 states how far.

### 1.1 Wording that must not be overclaimed

The chooser **does** run a simulation: a discrete-event queue model over the
task set (`simulate()`). What it does *not* run, per query, is **RTL
simulation** or **logic synthesis**. The defensible phrasing is:

- ✅ "no RTL simulation and no synthesis per query"
- ✅ "analytical cost model, no cycle-accurate simulation"
- ❌ "without running simulations" — false as written, and the first thing
  a reviewer would check.

Similarly, the timing metrics are **rank scores, not cycle predictions**.
`estimate_cycles` is documented as such (`GOLDEN_CHECK_SUMMARY.md` §7). The
claim is about *which policy wins*, never about how many cycles it takes.

**And one more scoping clause, now load-bearing:** the claim is about the
policy that wins **on the accelerator being modelled**. The dual-issue
results show the winner can change when the machine changes, so "best
scheduler" is never a property of the policy alone.

---

## 2. Scope — what is and is not claimed as novel

| Component | Novel? | Why |
|---|---|---|
| The 14 scheduling policies (FIFO, LIFO, SJF, RR, PRI, EDF, LRU, SRTF, HRRN, MLQ, MLFQ, AI-MT, BatchDNN, BatchDNN++) | **No** | Standard operating-systems policies; AI-MT and BatchDNN are from the literature. |
| Their RTL implementations | **No** | Engineering work, not a research result. |
| The systolic-array simulator | **No** | Infrastructure. |
| The dual-issue execution top (`rtl/exec/`) | **No** | Engineering work; it is what makes the literature's policies behave as published. |
| **The selection algorithm** — workload + objective → policy, at design time, from a closed-form cost model plus a policy-replay model, joined to a measured hardware table | **Yes** | This is the contribution. |
| The measured hardware table itself (13/14 policies synthesised) | Supporting | Evidence, not the claim. |

The contribution is a **design-space pruning method**. It does not claim to
predict cycle counts, and it does not claim a scheduler is fast — it claims
to identify, cheaply, which scheduler to build.

---

## 3. Problem statement

Let

- $S$ = the set of implemented scheduling policies, $|S| = 14$.
- $W = \langle w_1, \dots, w_n \rangle$ = a workload mix of $n$ DNN inference
  tasks, each $w_i$ a sequence of layers $\ell_{i,1..L_i}$.
- $H$ = a fixed hardware configuration: array geometry $(H_a, W_a)$,
  dataflow $d \in \{\mathrm{OS}, \mathrm{IS}, \mathrm{WS}\}$, data width,
  **and the dispatch discipline** (single-issue run-to-completion here).
- $g$ = an optimisation objective drawn from
  $G = \{$turnaround, turnaround_us, wait, throughput, area, power,
  makespan, weighted$\}$.

**Problem.** Compute $\sigma^\star(W, H, g) \in S$, the policy minimising
(or, for throughput, maximising) $g$, **without** simulating the RTL for any
$(\sigma, W)$ pair and without invoking synthesis at query time.

**Baseline cost.** The direct method evaluates all $|S| \times |W|$
combinations by RTL simulation, and requires the hardware to have been
synthesised first. The measured synthesis cost alone is ~135 s per policy
(`scripts/synth_scheduler_hw.py`), i.e. ~31 min for the 14-policy table.

---

## 4. The algorithm

Four stages. Stages 1–2 are the model; stage 3 is a join against measured
data; stage 4 is the decision rule.

### Stage 1 — Workload abstraction (closed form, no simulation)

Each layer's service cost is a closed-form function of its shape and the
array geometry. From `software_ref.estimate_cycles`:

$$
\tau_{\mathrm{OS}}(\ell) = 5 + H_a + W_a + \left\lceil \frac{o_h o_w}{H_a W_a} \right\rceil \cdot C \, k_H k_W
$$

$$
\tau_{\mathrm{IS}}(\ell) = 5 + o_h o_w + C \, k_H k_W \left\lceil \frac{K}{H_a} \right\rceil
$$

$$
\tau_{\mathrm{WS}}(\ell) = 5 + \left\lceil \frac{K}{H_a} \right\rceil \left\lceil \frac{C k_H k_W}{W_a} \right\rceil + o_h o_w C
$$

where $K$ = output channels, $C$ = input channels, $k_H \times k_W$ = kernel,
$o_h \times o_w$ = output spatial dims. The constant 5 is the pipeline
fill/drain allowance; $H_a + W_a$ in OS is the systolic skew.

Task service time is the sum over the task's layers:

$$
\tau_i = \sum_{j=1}^{L_i} \tau_d(\ell_{i,j})
$$

Each task additionally carries the attributes the RTL schedulers decide on —
declared burst time $b_i$, priority $p_i$, deadline $D_i$, arrival $a_i$.
These are **declared** values, deliberately separate from $\tau_i$: the RTL
decides on what the system tells it, not on the true cost. By default
$b_i = \tau_i$, $p_i = i$, $D_i = 1000(i{+}1)$, $a_i = 0$.

> **Correction to an earlier description of this work.** The estimator is a
> function of layer shape, dataflow and array geometry **only**. It takes no
> memory-capacity argument. The CLI's `--mem` flag is recorded for
> provenance and provably does not change the ranking, because MT/CT overlap
> is not modelled on the single-issue machine (§9.2). Any write-up claiming
> memory provision feeds *this* cost model is wrong. (On the dual-issue top
> memory provision does change the outcome — measurably, see §8.1 — which is
> a reason to extend the model, not a reason to reinterpret it.)

### Stage 2 — Policy replay

Each policy $\sigma \in S$ is a **selection predicate** $\Phi_\sigma$ over
the ready queue $Q$ and scheduler state $\Theta$, returning the index to
dispatch. Each is transcribed from the corresponding RTL case arm, and each
`_sel_*` function in the source carries the file and case number it mirrors.

| Policy | $\Phi_\sigma(Q,\Theta)$ | RTL source |
|---|---|---|
| FIFO | $0$ | `task_scheduler.sv` case 0 |
| LIFO | $\lvert Q\rvert - 1$ | case 1 |
| SJF | $\arg\min_i b_i$, lowest index wins | case 2 |
| RR | $\theta_{rr}$ if $\theta_{rr} < \lvert Q\rvert$ else 0 | case 3 |
| PRI | $\arg\max_i p_i$, lowest index wins | case 4 |
| EDF | $\arg\min_i D_i$, lowest index wins | case 5 |
| LRU | $\arg\min_i \theta_{acc}[i]$ | case 6 |
| SRTF | $\arg\min_i \theta_{rem}[i]$ | advanced |
| HRRN | $\arg\max_i (\theta_{wait}[i] + b_i)/b_i$ | advanced |
| MLQ | first task at the highest non-empty level, scanning $N_q{-}1 \to 0$ | advanced |
| MLFQ | first task at the lowest non-empty level, scanning $0 \to N_q{-}1$ | advanced |
| AI-MT / BatchDNN / BatchDNN++ | first table entry passing the memory-balance check | `aimt_scheduler.sv` |

The dispatch loop is work-conserving and **run-to-completion**: this is a
property of the single-issue integration, not a modelling shortcut.
`multi_dnn_top`'s dispatch FSM holds a dispatched task until its
`task_complete` pulse, so although RR, LRU, SRTF and MLFQ are preemptive
selectors, preemption cannot manifest. $\Phi_\sigma$ is therefore applied at
dispatch points only.

> **This is where the two machines diverge.** `multi_dnn_exec_top` runs two
> independent dispatch channels, so for AI-MT / BatchDNN / BatchDNN++ a
> memory task and a compute task can be in flight at once. The single-index
> $\Phi_\sigma$ above cannot express that — a faithful model of the
> dual-issue machine needs a *pair* of predicates over two resources plus a
> buffer-occupancy constraint. Extending the chooser that way is open work
> (§9.10).

Given a dispatch order, per-task start $s_i$ and finish $f_i$ follow, and:

$$
\mathrm{makespan} = \max_i f_i, \qquad
\overline{T} = \frac{1}{n}\sum_i (f_i - a_i), \qquad
\overline{W} = \frac{1}{n}\sum_i (s_i - a_i)
$$

### Stage 3 — Join with measured hardware

Area (LUT/FF), vectorless dynamic power, and post-synthesis $F_{max}$ come
from `results/sched_chooser/hw/scheduler_hw.csv`, produced by real Vivado
out-of-context synthesis. Two derived quantities bridge model and
measurement:

$$
\overline{T}_{\mu s} = \frac{\overline{T}}{F_{max}}, \qquad
\mathrm{Throughput} = \frac{n \cdot F_{max}}{\mathrm{makespan}}
$$

**Invariant preserved:** a policy with no measured value is **excluded**
from hardware-dependent objectives. No value is ever interpolated,
substituted, or estimated. This is why `BATCHDNN_PP` currently drops out of
`--goal area/power/throughput/turnaround_us` (its last synthesis predates
the multi-driven-reset fix and re-synthesis exceeds this machine's RAM).

> The measured hardware table also **predates the four scheduler RTL fixes of
> §7.4**. Those fixes add a small amount of logic (a seeded register, a guard
> flag, restructured queue-counter updates), so the LUT/FF/power/$F_{max}$
> rows for AI-MT, BatchDNN and BatchDNN++ should be re-synthesised before
> being quoted again. Objectives that depend only on the model (turnaround,
> wait, makespan) are unaffected.

### Stage 4 — Ranking and tie-break

$$
\sigma^\star = \arg\!\min_{\sigma \in S_g} \; \big\langle\, v_g(\sigma),\; \overline{T}(\sigma),\; \overline{W}(\sigma),\; \mathrm{makespan}(\sigma),\; \mathrm{name}(\sigma) \,\big\rangle
$$

lexicographically, where $S_g \subseteq S$ is the rankable subset for
objective $g$ and $v_g$ is negated for throughput. The trailing name key is
**required, not cosmetic**: policies producing an identical dispatch order
are identical on every timing metric, so without it the winner would be
decided by enumeration order — an artefact masquerading as a result.
`describe_tiebreak()` reports which key genuinely separated a tied set, and
says so explicitly when none did.

### Stage 5 (sweep) — Robust recommendation across mixes

A single mix cannot support a recommendation. `sched_objective_matrix.py`
sweeps $G \times \mathcal{M}$ over a representative mix set $\mathcal{M}$
and recommends per objective by **intersection of tied-best sets**:

$$
A_g = \bigcap_{m \in \mathcal{M}} \mathrm{TiedBest}_g(m)
$$

If $A_g \neq \emptyset$ the objective has a workload-independent answer, and
the pick within $A_g$ falls to lowest measured area — of policies that are
provably co-optimal on the objective, build the cheapest. If
$A_g = \emptyset$ the answer is genuinely workload-dependent and is reported
as such.

> This step exists because the naive summary — counting winner *names* per
> mix — manufactures disagreement. Most cells are ties, so different mixes
> print different alphabetical representatives of the *same* optimal set.
> Aggregating over sets rather than names removes that artefact.

### Pseudocode

```
CHOOSE(W, H, g, M):
  # Stage 1 — O(L), closed form
  for each task i in W:
      tau_i = sum over layers of tau_d(layer)          # no simulation
      declare (b_i, p_i, D_i, a_i)

  # Stage 2 — O(|S| n^2)
  for each policy s in S:
      Q, t, order = [], 0, []
      while tasks remain:
          admit all arrivals with a_i <= t
          k = Phi_s(Q, Theta)                          # RTL-transcribed rule
          dispatch Q[k]; t += tau_k; record s_i, f_i
          update Theta                                 # LRU/SRTF/RR/MLFQ state
      derive makespan, mean turnaround, mean wait

  # Stage 3 — table lookup, no synthesis
  join measured (LUT, FF, power, Fmax); derive us and tasks/s
  drop policies lacking a measured value required by g

  # Stage 4 — O(|S| log |S|)
  return lexicographic argmin over (v_g, T, W, makespan, name)
```

---

## 5. Complexity

| Stage | Cost |
|---|---|
| 1 — cost model | $O(L)$, $L$ = total layers. Closed form, no iteration over data. |
| 2 — policy replay | $O(\lvert S\rvert \, n^2)$ — $n$ dispatch events, each an $O(n)$ queue scan plus an $O(n)$ wait-time update. |
| 3 — hardware join | $O(\lvert S\rvert)$ table lookup. Synthesis is **amortised**, not per query. |
| 4 — ranking | $O(\lvert S\rvert \log \lvert S\rvert)$ |

Crucially the complexity is independent of cycle count. RTL simulation cost
scales with the *makespan* (~10⁴–10⁵ cycles here); the model's cost scales
with the *number of tasks* ($n \le 6$).

### Measured cost

| Quantity | Measured |
|---|---|
| Warm scoring, 14 policies × 1 mix | **0.1 ms** |
| Warm, 14 policies × 4 mixes | **1.0 ms** |
| Full sweep: 6 objectives × 6 mixes × 14 policies = 504 combinations | **8.2 ms** |
| Cold CLI end-to-end (interpreter + imports + scoring + table + CSV) | **0.54 s** |
| Vivado synthesis, per policy (amortised, cached) | **~135 s** |

Source: `results/sched_chooser/eval_speed.csv`, measured with warm scoring
separated from one-time import cost.

**Honest comparator.** Synthesis is per-policy, not per-workload, so it is
paid once (~31 min for all 14) and reused. What the method eliminates per
query is the **RTL simulation** of $\lvert S\rvert \times \lvert
\mathcal{M}\rvert$ combinations.

> **Updated:** Verilator is no longer unavailable — it is built from source
> into the scratchpad (v5.050, ~4 min with `-j12`, no sudo; see
> `tb/exec/build_exec.sh`). An RTL-simulation comparator is therefore now
> *measurable*, and the earlier refusal to quote a speedup ratio no longer
> needs to be permanent. It is still not quoted here, because the runs that
> exist are on the **dual-issue** top, not the single-issue machine this
> chooser models; a like-for-like comparator requires the §7.3 experiment.
> Until it is run, the defensible statement remains the absolute figure:
> full 504-combination sweep in 8.2 ms, versus a hardware table that costs
> ~31 min to build once.

---

## 6. Representative workload set

Six mixes (`SCHED_EVAL_MIXES` in `scripts/workloads.py`), spanning the two
axes that change a scheduling decision — queue depth and task-size skew:

| Mix | Tasks | Per-task model cycles |
|---|---|---|
| 1 — Edge Classification | 3 | 4,484 / 42,708 / 11,404 |
| 2 — Edge Heterogeneous | 4 | 10,569 / 1,876 / 65,172 / 6,420 |
| 3 — Cloud NLP + Vision | 3 | 64,532 / 3,668 / 131,412 |
| 4 — Cloud Heterogeneous | 4 | 57,108 / 1,620 / 1,876 / 5,460 |
| 5 — Skewed Pair | 2 | 1,620 / 131,412 (81× skew, shallowest reorderable queue) |
| 6 — Deep Mixed Queue | 6 | 1,620 … 131,412 (deepest queue, full cost range) |

Workloads are drawn from MLPerf Inference v3.0, MLPerf Tiny v1.0 and
DeepBench. Each network contributes 4 representative layers, so a "task"
here is a 4-layer stage sequence, not a full network.

The dual-issue evaluation uses **these same six mixes**, expanded to
per-layer scheduling tables (12–24 layers) rather than collapsed to one
service time per task — which is what lets memory and compute be scheduled
separately. Generator: `scripts/aimt_workload_gen.py`.

---

## 7. Validation — what is established and what is not

This section is deliberately conservative. **The claim is not yet fully
validated**, and the gap is specific.

### 7.1 Established

**Anchor A — policy transcription and TF-golden output, all 14 policies.**
Re-run under Verilator 5.050 + cocotb 2.0.1 against `multi_dnn_top` with the
§7.4 scheduler fixes in place. Each policy runs the 3-task golden mix and each
task's RTL output is compared to its TensorFlow-dumped `expected.npy`. Raw
data: `results/golden_check/raw/multi_*.json`; summary:
`results/golden_check/multi_dnn_golden_all14.csv`. The pre-fix artefacts are
preserved in `results/golden_check/raw_prefix_backup/`.

| Policy | Sel | RTL order | Model order | Cycles | max err %FS | Verdict |
|---|---|---|---|---|---|---|
| FIFO | 0 | 0→1→2 | 0→1→2 | 13,412 | 0.017 | ✅ |
| LIFO | 1 | 2→1→0 | 2→1→0 | 13,412 | 0.017 | ✅ |
| SJF | 2 | 0→1→2 | 0→1→2 | 13,412 | 0.017 | ✅ |
| RR | 3 | 0→1→2 | 0→1→2 | 13,412 | 0.017 | ✅ |
| PRI | 4 | 2→1→0 | 2→1→0 | 13,412 | 0.017 | ✅ |
| EDF | 5 | 0→1→2 | 0→1→2 | 13,412 | 0.017 | ✅ |
| LRU | 6 | 0→1→2 | 0→1→2 | 13,412 | 0.017 | ✅ |
| SRTF | 7 | 0→1→2 | 0→1→2 | 13,412 | 0.017 | ✅ |
| HRRN | 8 | 0→1→2 | 0→1→2 | 13,412 | 0.017 | ✅ |
| MLQ | 9 | 0→1→2 | 0→1→2 | 13,412 | 0.017 | ✅ |
| MLFQ | 10 | 0→1→2 | 0→1→2 | 13,412 | 0.017 | ✅ |
| AI-MT | 11 | 0→1→2 | 0→1→2 | 13,413 | 0.017 | ✅ |
| BatchDNN | 12 | 0→1→2 | 0→1→2 | 13,413 | 0.017 | ✅ |
| BatchDNN++ | 13 | 0→1→2 | 0→1→2 | 13,413 | 0.017 | ✅ |

**14/14 golden pass, and 14/14 exact dispatch-order match against the
transcribed $\Phi_\sigma$.** Every task reproduces its TensorFlow golden to
≤ 0.017% of full scale, and the measured makespan spread across all fourteen
policies is **1 cycle** (13,412 vs 13,413). The replay uses the golden
harness's *declared* synthetic attributes ($b = 10/20/30$) verbatim, because
those — not the real costs — are what the RTL decides on.

> **This required fixing the hardware, not the model.** The first all-14 run
> had RR, LRU and HRRN failing outright — each dispatching one task twice,
> starving another, and hitting the 200,000-cycle cap with the starved task's
> output meaningless (LRU: 100% of full scale). Root cause and the four fixes
> are in §8.2. The model needed no change: it had transcribed the selection
> rules correctly all along, and once the RTL stopped re-deciding mid-flight
> the two agreed exactly.

> **On the pre-fix artefacts.** They recorded `is_ct: [0, 0, 0]` for the three
> DNN-aware policies — every logged dispatch a *memory* task — which is
> consistent with two of the §7.4 defects stopping the compute path
> dispatching. That they nonetheless passed golden is explained in §7.5:
> `single_dnn_top` computes on any dispatch regardless of the MT/CT flag, so
> this test cannot detect a broken CT path.

**Anchor B — makespan invariance (single-issue machine).** The theory says
makespan is identical under every order on a single work-conserving machine.
Measured RTL spread across five policies: 13,412–13,413 cycles (0.0075%, one
cycle, attributable to dispatch handshake). Model spread: 0.0000%. The model
reproduces the invariance instead of predicting a speedup — this is the check
that would catch a fabricated performance claim.

> **Scope.** This invariance is a property of the *single-issue* machine, and
> the identical measured numbers are its signature. On the dual-issue top the
> same five policies span 331,621 → 229,100 cycles on mix 3 (a 1.45× spread),
> because there the scheduler controls how much memory time hides behind
> compute, not merely the order of a fixed amount of work. Anchor B is
> therefore evidence that the model is faithful *to the machine it models* —
> not evidence that scheduling cannot matter.

**Determinism / argmin consistency.** Every $(\text{mix}, \text{goal})$
pick re-verified against independent exhaustive re-scoring: all match. Note
this is a **self-consistency check, not external validation** — the chooser
is exhaustive over 14 policies, so it verifies the sort and tie-break, not
the model's fidelity. The evaluation script states this plainly and this
document repeats it.

### 7.2 Not established — the actual gap

Two distinct halves of the algorithm have very different validation status,
and conflating them would be the central weakness of any write-up:

| Component | Validated against RTL? |
|---|---|
| $\Phi_\sigma$ — selection rules | **14 of 14 policies**, on 1 mix: exact dispatch-order match plus TF-golden output. |
| $\tau_d(\ell)$ — cost estimator | **No.** Never compared to RTL cycle counts in the multi-DNN setting. Documented as a rank score. |

Specifically missing:

1. ~~9 of 14 policies have no RTL ground truth~~ — **closed.** All 14 have it,
   and after the §8.2 hardware fixes all 14 pass and match the model exactly.
2. **Only one mix has ground truth** — the golden 3-task mix, not the six
   representative mixes. Still open, and now **the** binding limitation.
3. **No rank correlation has been computed** — the claim "the model's
   ranking matches the RTL's ranking" is currently untested. There is no
   Spearman $\rho$ to quote. Still open.
4. **Absolute timing is unvalidated by construction** and must never be
   presented as a cycle prediction.

A caution that the exercise earned: on the 3-task mix eleven of the fourteen
policies produce the *same* dispatch order, so order agreement is a weak
discriminator. It is strong evidence for LIFO and PRI (which invert) and for
catching gross failure, but a mix with real reordering pressure is what would
make Anchor A load-bearing. That is item 2.

**What the dual-issue work does and does not contribute here.** It supplies
RTL measurements for 5 policies × 6 mixes — but on a *different machine*, so
it does **not** close items 1–3. Its contribution to this gap is that the
blocker was tooling, and the tooling now exists.

### 7.3 The experiment that closes the gap

**Now executable** — Verilator is available (§5). This is the single highest-value
piece of outstanding work in the scheduler section.

- **Design:** for each mix $m \in \mathcal{M}$ (6) and each policy
  $\sigma \in S$ (14), run `multi_dnn_top` under Verilator and record
  dispatch order and per-task completion cycles. 84 RTL runs.
- **Metric 1 — decision accuracy.** Fraction of $(m, g)$ pairs where the
  model's $\sigma^\star$ equals the RTL's, counting a tied-set hit as a hit
  (a tie the model correctly identifies as a tie is a correct decision).
  Target: report as $X/(6 \times \lvert G\rvert)$.
- **Metric 2 — rank correlation.** Spearman $\rho$ between model and RTL
  rankings of the 14 policies, per $(m, g)$; report mean and worst case.
  This is the number the claim actually rests on.
- **Metric 3 — order fidelity.** Exact dispatch-order match rate across all
  84 runs, extending Anchor A from 5/14 to 14/14 and from MT-only to MT+CT.
- **Falsifier, stated in advance:** if mean $\rho < 0.8$, or if decision
  accuracy is below the rate obtainable by always answering with the
  co-optimal set from §5, the method does not support the claim and the
  cost model needs revision rather than reinterpretation.

**Practical note:** budget for RR being excluded or fixed first — on the
dual-issue harness it retires only 10–11 of 12 layers, because the legacy
round-robin pointer can re-select an already-dispatched slot. Any policy that
fails to retire the whole workload must be **rejected, not credited with a
fast time**; the dual-issue harness enforces this with an explicit
completion counter, and the §7.3 experiment should do the same.

### 7.4 Scheduler RTL defects found and fixed

Building the dual-issue machine exposed four genuine bugs in the DNN-aware
schedulers. Each produced a *fast but wrong* run — a short cycle count for a
workload that had been silently half-dropped — which is precisely why they
survived the existing checks.

| # | Scheduler | Defect | Symptom |
|---|---|---|---|
| 1 | BatchDNN, ++ | `prev_batch` / `prev_batch_reg` reset to 0 and written only inside the dispatch path, while `max_batch_size()` clamps to them | feasible batch pinned at 0 → CT path stalled forever |
| 2 | all three | OFMAP reserved but never released; the batching pair reserved it twice (MT `mem_req` *and* CT dispatch) | `avail_mem` drained until the balance check failed permanently |
| 3 | BatchDNN, ++ | `ct_cq_cnt` / `sct_cnt` used a raw `+1`/`-1`; a same-edge enqueue+pop lost the enqueue | layers stranded in the queue — BatchDNN finished 8 of 12 |
| 4 | BatchDNN++ | `layer_distance()` compares *global* layer indices against a `ct_current_layer[]` that resets to 0 | any DNN whose first layer index > `MAX_LAYER_DISTANCE` throttled forever — a whole network never ran |

Defect 3 is the "finding F7" pattern already applied to `mt_cq` but never
extended to the other two queues. Separately, `MAX_DNNS` defaults to 4 while
mix 6 co-schedules six networks, so per-DNN state was indexed out of range;
the dual-issue testbench elaborates with `MAX_DNNS = 8`.

**Consequence for this document:** the transcribed $\Phi_\sigma$ for the
DNN-aware family mirrors the *table-scan* logic, which was never the broken
part, so Stage 2 is unaffected. The measured hardware rows are affected (§4,
Stage 3) and should be re-synthesised.

Regression-guarded by `tb/unit/test_dnn_scheduler_exec.py` (10 tests; skips
cleanly when the simulator is not built).

### 7.5 Why the golden test did not catch any of this

Worth stating plainly, because it bounds what a passing golden run means here.
In `multi_dnn_top` the dispatch FSM starts `single_dnn_top` on **any**
`sched_out.valid`, and `single_dnn_top` then runs `S_MEM → S_COMPUTE`
internally *regardless of whether the scheduler flagged that dispatch as a
memory or a compute task*. Numerical correctness therefore comes from the
datapath, not from the scheduler's CT decisions.

That is exactly why all five instrumented policies passed golden while
BatchDNN and BatchDNN++ were carrying defects 1–3, which stopped them issuing
compute tasks at all.

> **A passing multi-DNN golden run is evidence the datapath is right. It is
> not evidence the scheduler is right.** The two failure classes this test
> *can* catch are a wrong dispatch *order* and a task that never gets
> dispatched — which is how RR, LRU and HRRN were caught.

---

## 8. Findings that follow from the model

These are results, not caveats — each is a statement about the hardware that
the model makes explicit and the measurements corroborate. **F1–F4 are
properties of the single-issue machine**; §8.1 records what changes when the
machine does.

**F1 — Makespan cannot discriminate policies on the single-issue
accelerator.** On a single work-conserving machine, reordering moves *which*
task runs when, never total busy time nor forced idle. `--goal makespan` is
therefore provably an all-way 14-way tie. Measured RTL agrees (1-cycle
spread). Any paper claiming a makespan speedup from scheduling **on this
integration** would be wrong — but see §8.1 before generalising the
statement, because on a dual-resource machine it is false.

**F2 — `--goal throughput` reduces exactly to ranking by measured
$F_{max}$.** Since throughput $= n F_{max} / \mathrm{makespan}$, makespan is
invariant (F1) and $n$ is fixed, the objective selects the policy with the
fastest clock, not the best dispatch order. The CLI now states this. This
reduction is inherited from F1 and so is likewise single-issue-only.

**F3 — The 14 policies collapse to 4 behavioural classes.** Across all six
mixes, only four distinct dispatch-order signatures exist:

| Class | Policies |
|---|---|
| Arrival-order | FIFO, MLQ, RR, EDF, LRU, MLFQ, HRRN, AI-MT, BatchDNN, BatchDNN++ |
| Reverse-order | LIFO, PRI |
| Shortest-first | SJF, SRTF |

> **Now confirmed on hardware for all 14** (§7.1), but only after the §8.2
> fixes: before them RR, LRU and HRRN produced no valid schedule at all, so
> their class membership was a property of the model rather than the RTL. The
> collapse is real, and on this mix it is severe — eleven of fourteen policies
> emit the identical order, which is why hardware cost is usually the only
> discriminator.

This collapse is a direct consequence of run-to-completion dispatch plus
default task attributes, and it means the effective design space is far
smaller than the policy count suggests. It also explains why hardware cost (area, power,
$F_{max}$) is usually the *only* discriminator between co-optimal policies.
Note the collapse is about **dispatch order**: on a dual-issue machine the
three DNN-aware policies still scan the table in order yet no longer perform
identically to FIFO, because order is not the only thing that varies.

**F4 — MLQ is behaviourally FIFO in this RTL.** Every task is inserted at
queue level 0 and MLQ never changes a level, so its high-to-low scan always
selects the first level-0 task. This is transcribed faithfully rather than
"fixed", and recorded as a property of the implementation. MLQ wins area,
power and throughput because it is the smallest and fastest netlist, not
because of scheduling behaviour.

**F5 — Objective → policy, over the six representative mixes:**

| Objective | Recommended | Optimal on | Stability | Co-optimal set |
|---|---|---|---|---|
| turnaround | **SRTF** | 6/6 | workload-independent | SRTF, SJF |
| wait | **SRTF** | 6/6 | workload-independent | SRTF, SJF |
| turnaround_us | **MLQ** | 5/6 | **workload-dependent** (LIFO wins mix 4) | — |
| throughput | **MLQ** | 6/6 | workload-independent | — |
| area | **MLQ** | 6/6 | workload-independent | — |
| power | **MLQ** | 6/6 | workload-independent | — |

SRTF/SJF being co-optimal for mean turnaround and wait is the
textbook-correct result for a single machine with simultaneous arrivals —
an independent sanity signal that Stage 2 behaves correctly. SRTF is picked
over SJF on measured area (1,854 vs 1,999 LUT).

Note the tension F5 exposes and does not hide: shortest-first wins in
*cycles*, but MLQ wins in *wall-clock microseconds*, because the
comparator-tree policies buy fewer cycles at a much lower $F_{max}$
(SJF 20.3 MHz vs MLQ 112.4 MHz). Reporting cycle-domain results alone would
invert the engineering conclusion.

### 8.1 F6 — The machine, not the policy, decides whether scheduling matters

Measured on `multi_dnn_exec_top` under Verilator 5.050, same six mixes, same
array geometry and dataflow; full detail in
[`results/aimt_exec/REPORT.md`](../results/aimt_exec/REPORT.md).

| Mix | mem/compute | FIFO cycles | AI-MT cycles | Speedup | Array util |
|---|---|---|---|---|---|
| 1 | 1.19 | 129,702 | 77,496 | **1.67×** | 46% → 76% |
| 2 | 0.85 | 156,383 | 96,531 | **1.62×** | 54% → 87% |
| 3 | 0.61 | 331,621 | 229,100 | **1.45×** | 61% → 87% |
| 4 | 2.29 | 253,632 | 152,393 | **1.66×** | 37% → 44% |
| 5 | 0.33 | 182,369 | 147,306 | **1.24×** | 73% → 90% |
| 6 | 0.62 | 353,564 | 264,389 | **1.34×** | 61% → 81% |

Three consequences for this document:

1. **F1 is machine-specific, not general.** Makespan discriminates strongly
   once there are two resources to keep busy.
2. **The single-issue result was never evidence against AI-MT.** It was
   evidence that the machine could not express what AI-MT does — which §9.2
   previously said, and which is now demonstrated rather than argued.
3. **The chooser's objective set is incomplete for the new machine.**
   Utilisation and overlap are first-class outcomes there and have no
   corresponding goal in $G$.

Two further measured results bear on the model's design:

- **Overlap gain is non-monotone in arithmetic intensity.** Sweeping DRAM
  bandwidth (mem/compute 4.88 → 0.08), AI-MT's speedup peaks at **1.45× at a
  ratio of 0.61** and decays to 1.17× and 1.09× at the two extremes. Any
  future overlap term must be non-monotone; a constant factor is falsified by
  this curve.
- **Memory provision changes the ranking.** At 24 MB on-chip, BatchDNN++
  needs 541,614 cycles against AI-MT's 1,001,330 (**1.85×**); past ~32 MB the
  three converge. So the `--mem` flag, provenance-only today (§4 Stage 1),
  corresponds to a real effect on the dual-issue machine and would need to
  become a live model input there.

---

### 8.2 F7 — Dispatch must be locked: a scheduler that re-decides mid-flight removes the wrong task

Found by the all-14 golden run (§7.1), fixed, and re-verified. This is a
hardware finding, not a modelling one.

**Mechanism.** `removing_id` tracks the *live* scheduler output, and the queue
removal on `task_complete` searches for that id. So if a selector is free to
re-decide while a dispatched task is still executing, the registered output
drifts off the running task and the **wrong entry is removed**: the dispatched
task survives and is re-dispatched, while a task that never ran is deleted and
starves. The run then hits the cycle cap, and the starved task's captured
output is meaningless.

**Why only three policies failed.** The defect only bites when the selection
key *changes* during a run:

| Policy | Selection key | Mutates mid-run? | Before fix |
|---|---|---|---|
| SJF, SRTF | `burst_time` / `remaining_time` (not decremented here) | no | ✅ |
| MLQ, MLFQ | `queue_level` (always 0, cf. F4) | no | ✅ |
| **RR** | `rr_ptr` | **yes** | ❌ 0→2→0, capped |
| **LRU** | `last_access_time` | **yes** | ❌ 0→0→1, capped |
| **HRRN** | $(\theta_{wait}+b)/b$ | **yes** | ❌ 0→0→2, capped |

FIFO/LIFO/SJF/PRI/EDF were already locked (`is_non_preemptive`); the other nine
were not.

**Four fixes, one idea — nothing may re-select while a task is outstanding:**

1. `task_scheduler.sv` — dispatch lock made **unconditional** (was gated on
   `is_non_preemptive`, which excluded RR and LRU).
2. `advanced_task_scheduler.sv` — re-selection gated on `!task_running` (it
   re-ran `schedule_*()` every cycle).
3. `task_scheduler.sv` — LRU access touch guarded with `!removing`. It sat
   after compaction in the same `always_ff`, so on a removal edge it stamped
   the entry that had just shifted down, marking an innocent neighbour
   most-recently-used (LRU order 0→2→1 instead of 0→1→2).
4. `task_scheduler.sv` — RR quantum rotation gated on `!is_locked`. The quantum
   cannot preempt on a run-to-completion machine, yet a ~4,400-cycle task
   expires a 10-cycle quantum hundreds of times, leaving `rr_ptr` at an
   arbitrary offset (RR order 0→2→1, skipping a task).

A fifth instance lived in the dual-issue top: its basic FSM returned
`B_RETIRE → B_IDLE` on the same cycle `task_complete` was presented, re-latching
the stale offer. Fixed with a `B_ACK` state that waits for the scheduler to
withdraw. That one had been inflating the FIFO baseline of §8.1 by a full
redundant task per mix.

**Result:** 14/14 golden pass, 14/14 model-order match, makespan spread 1 cycle.
RR is now genuine round-robin and LRU genuine least-recently-used.

> **If real preemption is ever implemented, all four gates must be revisited
> together** — there, quantum expiry *is* the preemption trigger, and
> `removing_id` must latch the dispatched id at an accept handshake rather than
> tracking the live output. The lock is correct for a run-to-completion
> machine, not in general.

## 9. Limitations and threats to validity

1. **Cost model is a rank score.** $\tau_d$ has no validated absolute
   accuracy. All conclusions are ordinal.
2. **MT/CT overlap is not modelled — and this now bounds the chooser's
   applicability, not the hardware's capability.** The single-issue
   integration serialises MT and CT, so the chooser correctly carries no
   overlap term for it. **This is no longer a statement about the framework
   as a whole:** on `multi_dnn_exec_top` the overlap is real and measured
   (1.24–1.67×, up to 40.5% of cycles with both engines busy). The former
   wording — "this framework cannot demonstrate the advantage AI-MT and
   BatchDNN were designed for" — is **superseded**; it can, and does. What
   remains true is that *this chooser* cannot predict that advantage, because
   its machine model has one resource.
3. **Memory provision does not enter the model.** Consequence of (2) for the
   single-issue machine. `--mem` is provenance only *here*; on the dual-issue
   machine capacity demonstrably changes the winner (§8.1).
4. **Run-to-completion erases preemption, and the RTL now enforces that.**
   RR, LRU, SRTF, HRRN and MLFQ are preemptive selectors that cannot preempt
   here; §8.2 added the dispatch locks that make the hardware consistent with
   that fact (before them, three of the five actively broke). Results do not
   generalise to a preemptive dispatch FSM, and those locks are the first
   thing to remove if one is built.
5. **Arrivals are simultaneous by default** ($a_i = 0$). Staggered arrivals
   are supported via JSON mixes but are not part of the representative set,
   so the reported stability is conditioned on batch arrival.
6. **Single machine.** Every conclusion, especially F1, depends on there
   being exactly one compute engine — an assumption a second top now
   violates by design.
7. **13/14 hardware coverage, and the table is stale.** BatchDNN++ lacks a
   current measured row; additionally all three DNN-aware rows predate the
   §7.4 fixes and should be re-synthesised.
8. **Vectorless power.** Dynamic power is Vivado's vectorless estimate, not
   activity-annotated from real switching.
9. **Anchor A is narrower than it reads.** MT ordering only, on artefacts
   predating the scheduler fixes (§7.1 caveat).
10. **Open work — a dual-resource chooser.** Predicting the §8.1 results
    analytically needs a pair of selection predicates over two resources, a
    bandwidth-derived memory service time, and a buffer-occupancy constraint.
    Until that exists, the chooser must not be applied to
    `multi_dnn_exec_top`; doing so would return an answer for the wrong
    machine.
11. **Order agreement is a weak discriminator on the golden mix.** Eleven of
    the fourteen policies emit the same dispatch order there (F3), so Anchor A
    mostly demonstrates absence of gross failure. It is genuinely
    discriminating only for LIFO/PRI, which invert. A mix with real reordering
    pressure is needed before "the model matches the RTL" carries much weight
    — the same gap as §7.2 item 2.
12. **The §8.2 fixes changed measured timings slightly.** Locking the
    advanced family cost SRTF/MLQ/MLFQ two cycles (13,410 → 13,412), and the
    dual-issue `B_ACK` fix removed a redundant task from every basic-scheduler
    baseline, lowering the §8.1 speedups (mix 3: 1.45× → 1.41×). Any figure or
    table quoting the earlier numbers is stale.

---

## 10. Reproduction

```bash
cd sim_framework && source .venv/bin/activate

# --- the chooser (single-issue machine; this document's subject) ---

# single query
PYTHONPATH=. python scripts/choose_scheduler.py --mix mix3 --array 8x8 \
    --mem 256KB --goal turnaround_us

# full objective x mix sweep (the §8 F5 table)
PYTHONPATH=. python scripts/sched_objective_matrix.py

# validation anchors (the §7.1 tables)
PYTHONPATH=. python scripts/eval_sched_chooser.py

# --- RTL output vs TensorFlow golden, all 14 policies (§7.1) ---
# Needs verilator on PATH + cocotb in the venv:
#   pip install cocotb
# TensorFlow is NOT needed: expected.npy is already dumped under models/.
for S in FIFO LIFO SJF RR PRI EDF LRU SRTF HRRN MLQ MLFQ \
         AIMT BATCHDNN BATCHDNN_PP; do
    PYTHONPATH=. python tb/golden/run_golden_multi.py --sched $S
done

# --- the dual-issue measurements (the §8.1 table) ---

./tb/exec/build_exec.sh                                # verilator --binary
PYTHONPATH=. python scripts/run_aimt_eval.py --exp all # sweeps -> CSV
PYTHONPATH=. python scripts/gen_aimt_figs.py           # figures
PYTHONPATH=. python -m pytest tb/unit/test_dnn_scheduler_exec.py -q
```

Artefacts: `results/sched_chooser/objective_matrix.{csv,md}`,
`objective_recommendation.csv`, `eval_anchor_order.csv`,
`eval_anchor_flatness.csv`, `eval_speed.csv`,
`eval_decision_accuracy.csv`; and for §8.1,
`results/aimt_exec/exp{A,C,D,E}_*.csv` plus `results/aimt_exec/REPORT.md`.

---

## 11. Summary for the write-up

**Contribution.** An analytical method that selects, from 14 implemented
scheduling policies, the one best serving a stated optimisation objective
for a given multi-DNN workload on a fixed accelerator — at design time, in
milliseconds, without RTL simulation and without per-query synthesis.

**Evidence in hand.** Policy transcription matches measured RTL dispatch order
for **all 14 policies** on the golden mix, each reproducing its TensorFlow
golden output to ≤ 0.017% FS. Getting there required four hardware fixes, not
model changes (§8.2): three policies had been unable to complete a schedule at
all. The model reproduces measured makespan invariance to 0.0000% against a
measured 0.0075% (1 cycle across all fourteen); full 504-combination sweep in
8.2 ms against a ~31-minute one-off synthesis table; recommendations are stable
across six representative mixes for five of six objectives.

**Evidence still required.** RTL comparison across all 14 policies × **6
mixes** (only the golden 3-task mix has ground truth today), yielding decision
accuracy and Spearman rank correlation (§7.3). Now **executable** — Verilator
5.050 is built and cocotb installed — so it is scheduled work, not a blocked
dependency. It matters more than the raw 14/14 suggests: on the golden mix
eleven policies emit the *same* order, so that result mostly shows absence of
gross failure. Until a reordering-heavy mix is run, the correct phrasing is
*"validated against measured RTL for all 14 policies on one mix, on which most
policies coincide"* — not *"validated"*.

**One claim to retire.** Any sentence asserting that this project cannot
show the benefit AI-MT / BATCH-DNN / BATCH-DNN++ were designed for is now
false. On the dual-issue top the benefit is measured at 1.24–1.67× with array
utilisation rising from 37–73% to 44–90%, and it reproduces the published
mechanisms: overlap peaks when memory and compute are balanced, batching
amortises weight traffic 1.87× at B=16, and adaptive batching separates only
when on-chip memory is tight. The single-issue flatness was a property of the
machine, not of the policies.

**One claim to add.** Dispatch on a run-to-completion machine must be locked.
Three policies (RR, LRU, HRRN) could not complete a schedule until it was,
because a selector that re-decides mid-flight causes the *wrong* task to be
removed from the queue. That is a reusable design rule, and it is the reason
the all-14 golden sweep was worth running: the five-policy version had passed
for years while three of the fourteen were broken.
