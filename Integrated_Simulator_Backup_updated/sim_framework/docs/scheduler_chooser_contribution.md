# Analytical Scheduler Selection for a Multi-DNN Accelerator

**Status of this document.** It states the scientific claim of the scheduler
section, gives the algorithm formally, and reports exactly how much of the
claim is currently backed by measurement. The validation section
distinguishes what has been verified from what has not; the unverified parts
are named as such rather than left implied.

Implementation: [`pysim/scheduler_chooser.py`](../pysim/scheduler_chooser.py),
[`scripts/choose_scheduler.py`](../scripts/choose_scheduler.py),
[`scripts/sched_objective_matrix.py`](../scripts/sched_objective_matrix.py).

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

---

## 2. Scope — what is and is not claimed as novel

| Component | Novel? | Why |
|---|---|---|
| The 14 scheduling policies (FIFO, LIFO, SJF, RR, PRI, EDF, LRU, SRTF, HRRN, MLQ, MLFQ, AI-MT, BatchDNN, BatchDNN++) | **No** | Standard operating-systems policies; AI-MT and BatchDNN are from the literature. |
| Their RTL implementations | **No** | Engineering work, not a research result. |
| The systolic-array simulator | **No** | Infrastructure. |
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
  dataflow $d \in \{\mathrm{OS}, \mathrm{IS}, \mathrm{WS}\}$, data width.
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
> is deliberately not modelled (§8). Any write-up claiming memory provision
> feeds the cost model is wrong.

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
property of the integration, not a modelling shortcut. `multi_dnn_top`'s
dispatch FSM holds a dispatched task until its `task_complete` pulse, so
although RR, LRU, SRTF and MLFQ are preemptive selectors, preemption cannot
manifest. $\Phi_\sigma$ is therefore applied at dispatch points only.

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
\mathcal{M}\rvert$ combinations. That RTL simulation time is **not measured
here** — Verilator is unavailable in this environment — so no speedup ratio
against RTL simulation is quoted. Quoting one would be fabrication. The
defensible statement is the absolute figure: full 504-combination sweep in
8.2 ms, versus a hardware table that costs ~31 min to build once.

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
DeepBench.

---

## 7. Validation — what is established and what is not

This section is deliberately conservative. **The claim is not yet fully
validated**, and the gap is specific.

### 7.1 Established

**Anchor A — policy transcription vs. measured RTL.** Dispatch order
predicted by $\Phi_\sigma$ compared against five measured RTL golden runs
(`results/golden_check/raw/multi_*.json`):

| Policy | Measured order | Model order | Match |
|---|---|---|---|
| FIFO | T0→T1→T2 | T0→T1→T2 | ✅ |
| LIFO | T2→T1→T0 | T2→T1→T0 | ✅ |
| AI-MT | T0→T1→T2 | T0→T1→T2 | ✅ |
| BatchDNN | T0→T1→T2 | T0→T1→T2 | ✅ |
| BatchDNN++ | T0→T1→T2 | T0→T1→T2 | ✅ |

**5/5 exact.** The replay uses the golden harness's *declared* synthetic
attributes ($b = 10/20/30$) verbatim, because those — not the real costs —
are what the RTL decides on.

**Anchor B — makespan invariance.** The theory says makespan is identical
under every order on a single work-conserving machine. Measured RTL spread
across five policies: 13,412–13,413 cycles (0.0075%, one cycle, attributable
to dispatch handshake). Model spread: 0.0000%. The model reproduces the
invariance instead of predicting a speedup — this is the check that would
catch a fabricated performance claim.

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
| $\Phi_\sigma$ — selection rules | **Partially.** 5 of 14 policies, on 1 mix. |
| $\tau_d(\ell)$ — cost estimator | **No.** Never compared to RTL cycle counts in the multi-DNN setting. Documented as a rank score. |

Specifically missing:

1. **9 of 14 policies have no RTL ground truth** — SJF, RR, PRI, EDF, LRU,
   SRTF, HRRN, MLQ, MLFQ were never run against the RTL.
2. **Only one mix has ground truth** — the golden 3-task mix, not the six
   representative mixes.
3. **No rank correlation has been computed** — the claim "the model's
   ranking matches the RTL's ranking" is currently untested. There is no
   Spearman $\rho$ to quote.
4. **Absolute timing is unvalidated by construction** and must never be
   presented as a cycle prediction.

### 7.3 The experiment that closes the gap

Requires Verilator (unavailable in this environment; the cocotb tests are
written to run unmodified once it is present).

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
  84 runs, extending Anchor A from 5/14 to 14/14.
- **Falsifier, stated in advance:** if mean $\rho < 0.8$, or if decision
  accuracy is below the rate obtainable by always answering with the
  co-optimal set from §5, the method does not support the claim and the
  cost model needs revision rather than reinterpretation.

---

## 8. Findings that follow from the model

These are results, not caveats — each is a statement about the hardware that
the model makes explicit and the measurements corroborate.

**F1 — Makespan cannot discriminate policies on this accelerator.** On a
single work-conserving machine, reordering moves *which* task runs when,
never total busy time nor forced idle. `--goal makespan` is therefore
provably an all-way 14-way tie. Measured RTL agrees (1-cycle spread). Any
paper claiming a makespan speedup from scheduling on this integration would
be wrong.

**F2 — `--goal throughput` reduces exactly to ranking by measured
$F_{max}$.** Since throughput $= n F_{max} / \mathrm{makespan}$, makespan is
invariant (F1) and $n$ is fixed, the objective selects the policy with the
fastest clock, not the best dispatch order. The CLI now states this.

**F3 — The 14 policies collapse to 4 behavioural classes.** Across all six
mixes, only four distinct dispatch-order signatures exist:

| Class | Policies |
|---|---|
| Arrival-order | FIFO, MLQ, RR, EDF, LRU, MLFQ, AI-MT, BatchDNN, BatchDNN++ |
| Reverse-order | LIFO, PRI |
| Shortest-first | SJF, SRTF |
| Response-ratio | HRRN |

This is a direct consequence of run-to-completion dispatch plus default task
attributes, and it means the effective design space is far smaller than the
policy count suggests. It also explains why hardware cost (area, power,
$F_{max}$) is usually the *only* discriminator between co-optimal policies.

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

---

## 9. Limitations and threats to validity

1. **Cost model is a rank score.** $\tau_d$ has no validated absolute
   accuracy. All conclusions are ordinal.
2. **MT/CT overlap is not modelled.** AI-MT's memory/compute overlap and
   BatchDNN's sub-batch pipelining are the designed benefit of those
   policies, but this integration serialises MT and CT, and the measured
   golden runs show all five instrumented policies within one cycle.
   Modelling an overlap speedup would produce a number no measurement
   supports, so no overlap term exists. **Consequence:** this framework
   cannot demonstrate the advantage AI-MT and BatchDNN were designed for.
   That is a limitation of the integration, not evidence against those
   policies.
3. **Memory provision does not enter the model.** Direct consequence of (2).
   `--mem` is provenance only.
4. **Run-to-completion erases preemption.** RR, LRU, SRTF and MLFQ are
   preemptive in RTL but cannot preempt here. Results do not generalise to a
   preemptive dispatch FSM.
5. **Arrivals are simultaneous by default** ($a_i = 0$). Staggered arrivals
   are supported via JSON mixes but are not part of the representative set,
   so the reported stability is conditioned on batch arrival.
6. **Single machine.** Every conclusion, especially F1, depends on there
   being exactly one compute engine.
7. **13/14 hardware coverage.** BatchDNN++ lacks a current measured row;
   it is excluded from hardware objectives rather than estimated.
8. **Vectorless power.** Dynamic power is Vivado's vectorless estimate, not
   activity-annotated from real switching.

---

## 10. Reproduction

```bash
cd sim_framework && source .venv/bin/activate

# single query
PYTHONPATH=. python scripts/choose_scheduler.py --mix mix3 --array 8x8 \
    --mem 256KB --goal turnaround_us

# full objective x mix sweep (the §8 F5 table)
PYTHONPATH=. python scripts/sched_objective_matrix.py

# validation anchors (the §7.1 tables)
PYTHONPATH=. python scripts/eval_sched_chooser.py
```

Artefacts: `results/sched_chooser/objective_matrix.{csv,md}`,
`objective_recommendation.csv`, `eval_anchor_order.csv`,
`eval_anchor_flatness.csv`, `eval_speed.csv`,
`eval_decision_accuracy.csv`.

---

## 11. Summary for the write-up

**Contribution.** An analytical method that selects, from 14 implemented
scheduling policies, the one best serving a stated optimisation objective
for a given multi-DNN workload on a fixed accelerator — at design time, in
milliseconds, without RTL simulation and without per-query synthesis.

**Evidence in hand.** Policy transcription matches measured RTL dispatch
order 5/5; the model reproduces measured makespan invariance to 0.0000%
against a measured 0.0075%; full 504-combination sweep in 8.2 ms against a
~31-minute one-off synthesis table; recommendations are stable across six
representative mixes for five of six objectives.

**Evidence still required.** Verilator-based RTL comparison across all 14
policies × 6 mixes, yielding decision accuracy and Spearman rank
correlation (§7.3). Until then the correct phrasing is *"validated against
measured RTL for five policies on one mix, and consistent with the measured
makespan invariance"* — not *"validated"*.
