#!/usr/bin/env python3
"""
add_member2_notebook_cells.py
=============================
Insert the Member-2 (on-chip memory management) section into the thesis
notebook, leaving every existing cell exactly as it is.

The section is inserted just before the notebook's closing epilogue, so the
Member-1 material and the closing provenance statement keep their order.
Re-running the script replaces the previously inserted Member-2 block
rather than adding a second copy, so it is safe to run repeatedly.

Usage (from sim_framework/):
    python scripts/add_member2_notebook_cells.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB = ROOT / "results/thesis_notebook/chooser_validation.ipynb"

# Every inserted cell carries this tag so the block can be found and
# replaced on a re-run instead of duplicated.
TAG = "member2"


def md(text: str) -> dict:
    return {"cell_type": "markdown",
            "metadata": {"tags": [TAG]},
            "source": text.strip("\n").splitlines(keepends=True)}


def code(text: str) -> dict:
    return {"cell_type": "code", "execution_count": None,
            "metadata": {"tags": [TAG]}, "outputs": [],
            "source": text.strip("\n").splitlines(keepends=True)}


CELLS = [

md(r"""
---
# Part B — On-chip memory management (Member 2)

Everything above concerns how data is *ordered and delivered* to the array.
This part concerns what happens to it **once it is on the chip**: how the
scratchpad is banked, what happens when several read ports collide, and how
two different schemes for deciding *what lives in the scratchpad* compare on
identical hardware.

**The research gap this addresses.** Cycle-accurate DNN-accelerator
simulators generally model on-chip memory as a flat, always-hit buffer: no
banks, no arbitration, no memory-side stalls. That abstraction hides a real
cost. The three claims below are each backed by hardware counters read out
of RTL simulation, not by a memory model:

| # | Claim | Evidence below |
|---|-------|----------------|
| B1 | Bank arbitration is **exactly predictable** from a closed form derived from the RTL | 16/16 configurations, zero error |
| B2 | Banking changes **on-chip stalls only** — it does not change off-chip traffic | 4 bank counts, 3 invariant counters |
| B3 | STAMP (static tagless) and PAGED (dynamic page table) trade off against each other — **neither dominates** | 18 measured metric rows, 2 workloads |
| B4 | Measured hardware cost of each scheme and of banking itself | Vivado synthesis |

Both schemes produce **numerically identical results**, which is what makes
the comparison fair: they are interchangeable implementations of the same
function, differing only in cost.
"""),

md(r"""
## B1 — Bank conflicts follow an exact law

The scratchpad ([`rtl/memory/scratchpad_ram.sv`](scratchpad_ram.sv)) uses
**interleaved banking**: the low bits of the address select the bank, so
bank index = `address mod (number of banks)`. When two read ports want the
same bank in the same cycle, the lower-numbered port wins and the other is
stalled for that cycle.

Those two sentences fully determine the behaviour. If several ports issue
addresses at once, the number of ports that can be served in one cycle is
simply **how many distinct banks those addresses land in**:

$$\text{ports served per cycle} \;=\; \bigl|\{\, a_p \bmod B \;:\; p \in \text{active ports} \,\}\bigr|$$

$$\text{stalled port-cycles} \;=\; (N_{\text{ports}} - \text{ports served}) \times \text{cycles}$$

This is **derived from the RTL, not fitted to the data** — no constant in it
was tuned. The table below tests it against a microbenchmark that drives the
scratchpad's four read ports with four fixed address patterns for a 200-cycle
window, at five different bank counts, and reads the hardware's own conflict
counters.

*One-bank builds are excluded from the test:* the RTL's `NUM_BANKS == 1`
path is a flat single store with no arbitration logic and no conflict
counters at all, so it is the **no-banking baseline**, not a
zero-conflict optimum. Its reported "0 conflicts" means *not measured*,
not *none occurred*.
"""),

code(r"""
m2_law = pd.read_csv(M2 / 'bank_conflict_law.csv')
source_tag('Bank arbitration: measured RTL counters vs closed form derived '
           'from scratchpad_ram.sv', 'measured')

_checked = m2_law[m2_law['Prediction exact'].notna()]
print(f"Closed form reproduces {(_checked['Prediction exact'] == 'yes').sum()}"
      f"/{len(_checked)} banked configurations exactly "
      f"(the 4 one-bank rows have no arbitration to predict).\n")

m2_law
"""),

md(r"""
**Reading the two panels below.** The left panel is a *parity plot*: every
measured stall count is placed against what the closed form predicted. If the
law is right, every point sits exactly on the diagonal — and it does, for all
16 banked configurations. There is no scatter and no fitted line here,
because there is nothing to fit.

The right panel shows **why the answer changes**: it maps how many of the
four ports get served each cycle for each pattern and bank count. The
striping is the `address mod banks` rule made visible. Reading a row
left-to-right shows that more banks only help if the *access pattern* spreads
across them — the `stride 8` pattern still collides at 8 banks, because
0, 8, 16, 24 are all ≡ 0 (mod 8).
"""),

code(r"""
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# ---- (a) parity: measured vs predicted stall port-cycles -----------------
banked = m2_law[m2_law['Prediction exact'].notna()].copy()
ax = axes[0]
lim = banked['Stalled port-cycles, measured (cycles)'].max() * 1.15
ax.plot([0, lim], [0, lim], color=GAP, linestyle='--', linewidth=1.2,
        zorder=1, label='perfect agreement (y = x)')
ax.scatter(banked['Stalled port-cycles, predicted (cycles)'],
           banked['Stalled port-cycles, measured (cycles)'],
           s=140, color=MEASURED, edgecolor='white', linewidth=1.5,
           zorder=3, label=f'{len(banked)} banked configurations')
ax.set_xlim(-30, lim); ax.set_ylim(-30, lim)
ax.set_xlabel('Predicted stalled port-cycles (closed form, from RTL)')
ax.set_ylabel('Measured stalled port-cycles (hardware counter)')
ax.set_title('Every configuration lands exactly on the diagonal\n'
             '(points overlap: only 3 distinct values occur)')
ax.legend(loc='upper left', fontsize=9)

# ---- (b) heatmap: ports served per cycle ---------------------------------
ax = axes[1]
banked['ports_served'] = (banked['Reads served, measured (count)'] / 199).round().astype(int)
short = {'All ports -> same address': 'same\naddress',
         'Ports -> addresses 0,1,2,3': 'consecutive\n0,1,2,3',
         'Ports -> addresses 0,4,8,12 (stride 4)': 'stride 4\n0,4,8,12',
         'Ports -> addresses 0,8,16,24 (stride 8)': 'stride 8\n0,8,16,24'}
grid = banked.pivot(index='Number of banks (count)',
                    columns='Access pattern', values='ports_served')
grid = grid[list(short)].rename(columns=short).sort_index()

im = ax.imshow(grid.values, cmap='YlGnBu', vmin=1, vmax=4, aspect='auto')
ax.set_xticks(range(len(grid.columns)))
ax.set_xticklabels(grid.columns, fontsize=9)
ax.set_yticks(range(len(grid.index)))
ax.set_yticklabels([f'{b} banks' for b in grid.index])
for i in range(grid.shape[0]):
    for j in range(grid.shape[1]):
        v = grid.values[i, j]
        ax.text(j, i, f'{v} of 4', ha='center', va='center', fontsize=11,
                color='white' if v >= 3 else '#222',
                fontweight='bold' if v == 4 else 'normal')
ax.set_title('Read ports served per cycle (of 4)\n'
             'darker = better; the pattern decides, not just the bank count')
ax.grid(False)
cb = fig.colorbar(im, ax=ax, ticks=[1, 2, 3, 4])
cb.set_label('Ports served per cycle (count)')

fig.tight_layout()
plt.show()
"""),

md(r"""
**Why this matters.** A simulator that models the scratchpad as a flat buffer
would report *zero* stalls for every cell in that grid. The measured hardware
loses **three of its four read ports** on the worst patterns — a 4× loss of
memory bandwidth that a flat model cannot see at all. That is the gap this
part of the project closes, and the law above is what makes the loss
predictable in advance rather than only observable after a run.
"""),

md(r"""
## B2 — Banking changes on-chip stalls only, not off-chip traffic

The microbenchmark above used synthetic address patterns. The table below
runs a **real layer** (`tiny_cnn` layer 0, STAMP scheme) at four different
bank counts and reads the same counters, so the effect can be tied to actual
workload traffic rather than a chosen pattern.

Two things happen at once, and they need to be read separately:

* **Conflicts collapse** — 438 conflicts at 2 banks, 2 at 4 banks, 0 at 16.
* **Three counters do not move at all** — compute cycles, off-chip beats and
  off-chip bursts are *identical* at every bank count.

The second point is the more important one. It means banking is a purely
**on-chip** design knob: it buys back stall cycles without changing how much
data crosses the memory interface. So the choice of bank count can be made
independently of the memory-layout and dataflow choices studied in Part A —
the two decisions do not interact.
"""),

code(r"""
m2_scale = pd.read_csv(M2 / 'bank_scaling.csv')
source_tag('Bank-count sweep under real workload traffic '
           '(tiny_cnn L0, STAMP scheme)', 'measured')

_inv = [c for c in ['Compute (cycles)', 'Off-chip traffic (AXI beats)',
                    'Off-chip requests (AXI bursts)']
        if m2_scale[c].nunique() == 1]
print('Counters that are INVARIANT across all bank counts: '
      + ', '.join(_inv) + '\n')

m2_scale
"""),

code(r"""
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
banks = m2_scale['Number of banks (count)'].values

# ---- (a) what banking DOES change ---------------------------------------
ax = axes[0]
ax.plot(banks, m2_scale['Bank conflicts (events)'], marker='o', linewidth=2,
        color=MEASURED, label='Bank conflicts (events)')
ax.plot(banks, m2_scale['Stall (port-cycles)'], marker='s', linewidth=2,
        color=GAP, label='Stalled port-cycles')
for x, y in zip(banks, m2_scale['Bank conflicts (events)']):
    # Below the marker: the stall series runs just above this one, so
    # labelling upwards would collide with it.
    ax.annotate(f'{int(y)}', (x, y), textcoords='offset points',
                xytext=(0, -15), ha='center', va='top', fontsize=9,
                color=MEASURED, fontweight='bold')
ax.set_xscale('log', base=2); ax.set_yscale('symlog', linthresh=1)
ax.set_xticks(banks); ax.set_xticklabels(banks)
# Room above for the highest line and below for the zero-value label.
ax.set_ylim(bottom=-0.9, top=m2_scale['Stall (port-cycles)'].max() * 3)
ax.set_xlabel('Number of scratchpad banks (count)')
ax.set_ylabel('Events / port-cycles (log scale)')
ax.set_title('What banking changes: on-chip stalls\n'
             '438 conflicts to 2 between 2 and 4 banks, then flat')
ax.legend(fontsize=9)

# ---- (b) what banking does NOT change -----------------------------------
ax = axes[1]
# All three ratios are exactly 1.0, so the lines sit on top of one another.
# Nested marker sizes and dash patterns keep all three visible instead of
# only whichever was drawn last.
series = [('Compute (cycles)', '#2a78d6', 'o', 16, '-'),
          ('Off-chip traffic (AXI beats)', '#eb6834', 's', 10, '--'),
          ('Off-chip requests (AXI bursts)', '#1baf7a', '^', 5, ':')]
for col, c, mk, ms, ls in series:
    base = m2_scale[col].iloc[0]
    ax.plot(banks, m2_scale[col] / base, marker=mk, markersize=ms,
            linewidth=2, linestyle=ls, color=c,
            label=f'{col}  (constant at {base:,})')
ax.annotate('all three series coincide exactly at 1.0',
            xy=(banks[1], 1.0), xytext=(0, -34), textcoords='offset points',
            ha='center', fontsize=9, style='italic', color='#555')
ax.set_xscale('log', base=2)
ax.set_xticks(banks); ax.set_xticklabels(banks)
ax.set_ylim(0.90, 1.10)
ax.axhline(1.0, color='#888', linewidth=0.8, linestyle=':')
ax.set_xlabel('Number of scratchpad banks (count)')
ax.set_ylabel('Value relative to the 2-bank build (dimensionless)')
ax.set_title('What banking does NOT change: off-chip traffic\n'
             'all three lines are exactly flat at 1.0')
ax.legend(fontsize=8, loc='upper right')

fig.tight_layout()
plt.show()

print('Numerical results were identical at every bank count '
      f"(max relative error vs golden: "
      f"{m2_scale['Max relative error vs golden (%)'].unique()} %), "
      'so the stall reduction costs nothing in accuracy.')
"""),

md(r"""
**The design conclusion.** For this workload the useful operating point is
**4 banks**. Going from 2 to 4 banks removes 99.5% of the conflicts
(438 → 2); going from 4 to 16 removes only the last 2. Bank count 8 buys
nothing over 4 here. That is a concrete, measured sizing recommendation, and
Part B4 below puts the hardware cost against it.
"""),

md(r"""
## B3 — STAMP vs PAGED: neither scheme dominates

The two memory-management schemes are run on **the same RTL, the same layer,
the same bank count (4), and the same golden reference**. They differ only in
how the scratchpad's contents are decided:

* **STAMP (static, tagless)** — the schedule of what to load and what to keep
  is computed *ahead of time* and written into the hardware as a table of
  delta-operations. There is no tag, no lookup, and therefore nothing that
  can miss at run time.
* **PAGED (dynamic page table)** — a TLB-style page table translates
  addresses at run time; a reference to an unmapped page is a miss that must
  be resolved before the read completes.

The first row of the table to check is the **last** one: both schemes produce
the *same numerical output*, to the last digit. That is what licenses the
comparison — any difference in the other rows is a difference in cost, not a
difference in what was computed.
"""),

code(r"""
m2_cmp = pd.read_csv(M2 / 'scheme_comparison.csv')
source_tag('STAMP vs PAGED on identical hardware, layer and bank count',
           'measured')

def _fmt(v):
    return f'{v:,.6f}'.rstrip('0').rstrip('.') if v % 1 else f'{v:,.0f}'

_show = m2_cmp.copy()
for c in ['STAMP (static tagless)', 'PAGED (dynamic page table)']:
    _show[c] = _show[c].map(_fmt)
_show
"""),

md(r"""
**Reading the four panels below.** Each panel is one metric, with both
workloads side by side, and the two schemes as paired bars. They are split
this way deliberately: **the top row is where PAGED wins, the bottom row is
where STAMP wins.** Presenting only one row would be cherry-picking.

* **(a) Off-chip traffic** — PAGED moves 18.3% fewer beats on `tiny_cnn` and
  7.5% fewer on `mnist_cnn`. Its page granularity happens to coalesce this
  layer's accesses better than STAMP's delta schedule does.
* **(b) Control/setup overhead** — STAMP must *program* its delta-op table
  before the phase can start (41 and 527 cycles); PAGED needs 2. This is the
  price of deciding everything ahead of time.
* **(c) Bank-conflict stalls** — on `tiny_cnn` STAMP loses 4 port-cycles
  where PAGED loses 240, a 98.3% reduction; on `mnist_cnn` it is 202 against
  488, a 58.6% reduction. A statically-planned access order collides with
  itself far less than a dynamically-resolved one.
* **(d) Runtime lookup misses** — **STAMP records exactly zero, in both
  workloads.** This is not a tuning result that happened to come out well; it
  is structural, and it is the central claim of the scheme.
"""),

code(r"""
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
wls = ['tiny_cnn L0', 'mnist_cnn L0']
x = np.arange(len(wls)); width = 0.36

panels = [
    ('Off-chip traffic', 'AXI beats', 'Off-chip traffic (AXI beats)',
     '(a) PAGED moves less data off-chip', False),
    ('Control/setup overhead', 'cycles', 'Control / setup overhead (cycles)',
     "(b) STAMP pays to program its schedule", True),
    ('Bank-conflict stalls', 'port-cycles', 'Bank-conflict stalls (port-cycles)',
     '(c) STAMP stalls far less on-chip', False),
    ('Runtime lookup misses', 'events', 'Runtime lookup misses (events)',
     '(d) STAMP cannot miss, by construction', False),
]

for ax, (metric, unit, ylabel, title, logy) in zip(axes.flat, panels):
    sel = m2_cmp[(m2_cmp['Metric'] == metric) & (m2_cmp['Unit'] == unit)]
    s = [sel[sel['Workload / layer'] == w]['STAMP (static tagless)'].iloc[0] for w in wls]
    p = [sel[sel['Workload / layer'] == w]['PAGED (dynamic page table)'].iloc[0] for w in wls]
    b1 = ax.bar(x - width/2, s, width, color=MEASURED, label='STAMP (static tagless)')
    b2 = ax.bar(x + width/2, p, width, color='#c9903a', label='PAGED (dynamic page table)')
    if logy:
        # Headroom on a log axis so the tallest bar's label is not clipped.
        ax.set_yscale('log'); ax.set_ylim(bottom=1, top=max(s + p) * 3)
    for bars, vals in ((b1, s), (b2, p)):
        for bar, v in zip(bars, vals):
            ax.annotate(f'{v:,.0f}', (bar.get_x() + bar.get_width()/2,
                                      bar.get_height()),
                        textcoords='offset points', xytext=(0, 3),
                        ha='center', fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(wls)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=11)
    ax.legend(fontsize=8)
    if metric == 'Runtime lookup misses':
        ax.set_ylim(top=max(p) * 1.25)
        ax.annotate('zero — structural guarantee', (0 - width/2, 0),
                    textcoords='offset points', xytext=(-4, 26), fontsize=9,
                    color=MEASURED, fontweight='bold', rotation=90)

fig.suptitle('STAMP vs PAGED — same hardware, same layer, same bank count, '
             'identical numerical output', fontsize=12.5)
fig.tight_layout()
plt.show()
"""),

md(r"""
### An important correction to how off-chip traffic is compared

An earlier table in this notebook (the `f5` memory-management table above)
reports *"STAMP off-chip bytes = 1640"* against *"PAGED off-chip bytes
(pages × 4KB) = 8192"*, and the chart beside it concludes that STAMP fetches
less. **Those two numbers are not the same quantity and should not be
compared.**

* STAMP's 1,640 B is `stats_bytes_loaded` — a counter of bytes the *stamp
  controller* loaded into the scratchpad.
* PAGED's 8,192 B is `2 pages × 4 KB` — a *derived footprint bound* from the
  page count, not a measured traffic figure. PAGED has no byte counter of its
  own in this hardware revision.

The directly comparable, directly measured quantity is the **AXI beat
counter**, which both schemes carry. On that counter the conclusion goes the
other way: **PAGED moves 18% less off-chip traffic on `tiny_cnn` and 8% less
on `mnist_cnn`**, as panel (a) shows. The f5 table and chart are left
unchanged above for continuity, but the beat-counter comparison is the one to
quote.
"""),

md(r"""
### The honest scorecard

Summing up B3 as it should be presented — with the losses shown, not just
the wins:
"""),

code(r"""
_wins = m2_cmp[m2_cmp['Better scheme'].isin(['STAMP', 'PAGED'])]
score = (_wins.groupby(['Metric', 'Better scheme']).size()
         .unstack(fill_value=0).reindex(columns=['STAMP', 'PAGED'],
                                        fill_value=0))
score.columns = ['Rows where STAMP wins', 'Rows where PAGED wins']
source_tag('Which scheme wins which metric (2 workloads, so 2 rows per metric)',
           'measured')
print(f"Overall: STAMP better on {(_wins['Better scheme']=='STAMP').sum()} "
      f"metric rows, PAGED better on {(_wins['Better scheme']=='PAGED').sum()}.")
print('Numerical output: identical for both schemes on both workloads.\n')
score
"""),

md(r"""
**How to state this result.** Not *"STAMP is better"* — the data does not
support that. The defensible claim is:

> STAMP trades **more off-chip traffic and a one-off programming cost** for
> **near-elimination of on-chip stalls and a structural guarantee of zero
> runtime misses**, at identical numerical accuracy. PAGED is the better
> choice when off-chip bandwidth is the bottleneck; STAMP is the better
> choice when on-chip stall behaviour must be predictable — and it is the
> only one of the two whose worst case can be *bounded in advance*, because
> it has no runtime lookup that can fail.

That last clause is the real contribution. A dynamic scheme's worst case
depends on the access stream and can only be measured; a static tagless
scheme's is fixed at compile time.
"""),

md(r"""
## B4 — Measured hardware cost

The comparison above is about *time*. This one is about *area and power* —
the third axis of the comparison, and the one the cycle-accurate runs cannot
provide. These figures come from real Vivado out-of-context synthesis on an
`xc7a100tcsg324-1` part with a 10 ns (100 MHz) clock constraint. Nothing is
estimated: a target that fails to synthesise is reported as unavailable with
the tool's own reason.

**Two caveats that must be stated with these numbers.**

*First — reduced depth.* The scratchpad is synthesised at **256 words, not
the 4,096 words used in simulation.** Running synthesis at the simulation
depth produced a genuine finding: `scratchpad_ram` is a *behaviourally
modelled* 4-read/4-write-port SRAM, and since Xilinx BRAM has only two
ports, Vivado cannot infer a memory and refuses to dissolve 131,072 bits
into flip-flops — which would not fit on this part in any case. Vivado's own
error text is preserved in
`results/member2/hw/reports/spad_depth4096_does_not_synthesise.log`.

This makes the numbers below a valid **relative** comparison — the cost of
adding banks, and the cost of STAMP's control logic against PAGED's — which
is exactly what the comparison needs. They are **not** the area of the
simulated design, and should never be quoted as such. Getting an absolute
figure would require restructuring the scratchpad into true dual-port BRAM
instances, which is a hardware change, not a measurement.

*Second — Fmax is post-synthesis.* Placement and routing will reduce it, so
it is useful for comparing these blocks against each other, not as an
absolute speed claim.
"""),

code(r"""
_hw_path = M2 / 'hw_cost.csv'
if not _hw_path.exists():
    print('Hardware-cost table not present in this data bundle.')
    print('Generate it in the repo with:')
    print('    python scripts/synth_memory_hw.py')
    print('    PYTHONPATH=. python scripts/make_member2_tables.py')
    m2_hw = None
else:
    m2_hw = pd.read_csv(_hw_path)
    source_tag('Vivado OOC synthesis, xc7a100tcsg324-1, 10 ns constraint',
               'measured')
    print(f"{(m2_hw['Synthesis status'] == 'ok').sum()}/{len(m2_hw)} "
          f"targets synthesised successfully.\n")
    display(m2_hw)
"""),

code(r"""
if m2_hw is not None and (m2_hw['Synthesis status'] == 'ok').any():
    ok = m2_hw[m2_hw['Synthesis status'] == 'ok'].copy()
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # ---- (a) cost of banking ---------------------------------------------
    spad = ok[ok['Group'] == 'scratchpad'].copy()
    ax = axes[0]
    if not spad.empty:
        spad['banks'] = spad['Target'].str.extract(r'b(\d+)').astype(int)
        spad = spad.sort_values('banks')
        ax.plot(spad['banks'], spad['LUTs (count)'], marker='o', linewidth=2,
                color=MEASURED, label='LUTs')
        ax.plot(spad['banks'], spad['Flip-flops (count)'], marker='s',
                linewidth=2, color=GAP, label='Flip-flops')
        ax.set_xscale('log', base=2)
        ax.set_xticks(spad['banks']); ax.set_xticklabels(spad['banks'])
        ax.set_xlabel('Number of scratchpad banks (count)')
        ax.set_ylabel('Resource usage (count)')
        ax.set_title('(a) What banking costs in hardware\n'
                     'trade against the conflict reduction in B2')
        ax.legend(fontsize=9)
    else:
        ax.text(0.5, 0.5, 'no scratchpad targets synthesised',
                ha='center', va='center'); ax.grid(False)

    # ---- (b) scheme cost --------------------------------------------------
    ax = axes[1]
    sch = ok[ok['Group'].isin(['backend', 'controller'])].copy()
    if not sch.empty:
        lbl = sch['What was synthesised'].str.replace(r'\s*\(.*\)', '',
                                                      regex=True)
        xs = np.arange(len(sch)); w = 0.38
        ax.bar(xs - w/2, sch['LUTs (count)'], w, color=MEASURED, label='LUTs')
        ax.bar(xs + w/2, sch['Flip-flops (count)'], w, color='#c9903a',
               label='Flip-flops')
        ax.set_xticks(xs)
        ax.set_xticklabels(lbl, rotation=18, ha='right', fontsize=8)
        ax.set_ylabel('Resource usage (count)')
        ax.set_title('(b) Hardware cost of each memory-management scheme')
        ax.legend(fontsize=9)
    else:
        ax.text(0.5, 0.5, 'no scheme targets synthesised',
                ha='center', va='center'); ax.grid(False)

    # A target that failed to synthesise is absent from the bars above.
    # Say so on the figure -- a silently missing bar reads as "not measured
    # and not worth mentioning", which would misrepresent the comparison.
    missing = m2_hw[m2_hw['Synthesis status'] != 'ok']
    if not missing.empty:
        fig.text(0.5, -0.03,
                 'Not shown (did not synthesise): '
                 + ', '.join(missing['What was synthesised']),
                 ha='center', fontsize=9, color=GAP, style='italic')

    fig.tight_layout()
    plt.show()

    if not missing.empty:
        print('Unavailable targets and the reason Vivado gave:')
        for _, r in missing.iterrows():
            print(f"  {r['What was synthesised']}: {r['Note']}")
else:
    print('Skipping hardware-cost chart -- no synthesis results in this bundle.')
"""),

md(r"""
## Part B summary — what Member 2 contributes

| Contribution | What was built | What the measurement shows |
|---|---|---|
| **Multi-bank scratchpad with real arbitration** | Interleaved banking, priority arbitration and conflict counters in SystemVerilog | Bank conflicts follow an **exact closed form**, verified on 16/16 configurations. Flat-buffer simulators report zero stalls where the hardware loses up to 3 of 4 read ports. |
| **Stamp-based static tagless scheme** (novel) | Compiler-assisted delta-op schedule; no tags, no runtime lookup | **Zero runtime misses in both workloads, by construction.** 59–98% fewer bank-conflict stalls than the dynamic baseline. |
| **Page-table dynamic scheme** (baseline) | TLB-style translation with miss handling | Moves 7.5–18% less off-chip traffic; needs almost no setup. Its miss count is workload-dependent and can only be measured, not bounded. |
| **Like-for-like comparison framework** | Both schemes behind one interface, same golden check | Identical numerical output confirms interchangeability; the differences are pure cost, measured on traffic, stalls, and silicon. |

**The scientific claim, stated carefully:**

> On-chip memory behaviour in a systolic-array accelerator is not an
> implementation detail that can be abstracted away. Bank arbitration costs
> up to 75% of read bandwidth on adversarial patterns and follows a closed
> form that is exactly predictable from the address mapping. And the choice
> between static-tagless and dynamic page-table management is a genuine
> trade-off rather than a ranking: the static scheme eliminates runtime
> misses and on-chip stalls at the cost of off-chip traffic and setup time,
> with both schemes computing bit-identical results.

**What is *not* claimed, and should be said before anyone asks:**

* Both schemes are compared at **4 banks on two conv layers**. The direction
  of the off-chip-traffic result could change on a layer with a different
  reuse pattern — it has not been swept.
* PAGED was measured at 4 banks only, so the **bank-scaling result (B2) is
  STAMP-only**. It is not known whether PAGED's conflicts fall the same way.
* The conflict law is verified on the **4-port** scratchpad used here. The
  form generalises to any port count, but that has not been measured.
* The hardware-cost figures in B4 are at **reduced scratchpad depth** and are
  a relative comparison only, for the reason given in that section.

### Finding for the team

Synthesis surfaced one issue worth recording, separate from the results
above:

> `rtl/memory/scratchpad_ram.sv` at its simulation depth (4,096 words,
> 4 read + 4 write ports) **does not synthesise** — Vivado cannot infer a
> multi-port memory, and the flip-flop fallback (131,072 bits) exceeds the
> target part. The module is correct as a *simulation* model and all
> cycle-accurate results above are unaffected, but an FPGA implementation
> would need the banks restructured into true dual-port BRAM instances with
> arbitration in front. Evidence:
> `results/member2/hw/reports/spad_depth4096_does_not_synthesise.log`.

This is reported, not fixed — changing the scratchpad would invalidate the
golden-check runs and belongs on its own branch.
"""),
]


def main() -> None:
    nb = json.loads(NB.read_text())
    cells = nb["cells"]

    before = len(cells)
    cells = [c for c in cells
             if TAG not in c.get("metadata", {}).get("tags", [])]
    removed = before - len(cells)
    if removed:
        print(f"Replacing {removed} previously inserted Member-2 cells")

    # Insert before the closing epilogue: find the last markdown cell that
    # states the provenance of the notebook, and go in ahead of it.
    anchor = next((i for i, c in enumerate(cells)
                   if c["cell_type"] == "markdown"
                   and "The numbers are real" in "".join(c["source"])),
                  len(cells))
    cells[anchor:anchor] = CELLS
    nb["cells"] = cells

    # The Member-2 tables live in their own bundle folder; make sure the
    # setup cell defines M2 for them.
    setup = next(c for c in cells if c["cell_type"] == "code"
                 and "EDGE_CLOUD =" in "".join(c["source"]))
    src = "".join(setup["source"])
    if "M2 =" not in src:
        src = src.replace(
            "EDGE_CLOUD = BUNDLE_DIR / 'edge_cloud_sample'",
            "EDGE_CLOUD = BUNDLE_DIR / 'edge_cloud_sample'\n"
            "M2 = BUNDLE_DIR / 'member2'          # Member-2 memory-management tables")
        setup["source"] = src.splitlines(keepends=True)
        print("Added M2 path to the setup cell")

    NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
    print(f"Inserted {len(CELLS)} Member-2 cells at position {anchor}; "
          f"notebook now has {len(cells)} cells")


if __name__ == "__main__":
    main()
