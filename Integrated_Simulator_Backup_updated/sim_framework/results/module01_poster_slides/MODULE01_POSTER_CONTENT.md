# Module 01 — Poster Panel (214056U · Dilshan P.)

**Compute & Data Delivery — Stationary Schemes × Memory Layouts × Casting Schemes**

**Lean version.** The earlier draft was mostly prose. Here the Contribution,
Method and Results blocks are **figures instead of bullet lists**, so the panel
reads at a glance. Only ~60 words of body text remain.

---

## Panel layout (top to bottom)

```
┌─────────────────────────────────────────────────────────────────────┐
│  4  Module 01 — Compute & Data Delivery Module            214056U   │
├──────────────────────────┬──────────────────────────────────────────┤
│  RESEARCH GAP            │                                          │
│  (3 short bullets —      │        poster_fig_knobs.png              │
│   the only text block)   │        "what was built"                  │
├──────────────────────────┴──────────────────────────────────────────┤
│                    poster_fig_flow.png    (method, full width)      │
├────────────────────────────────┬────────────────────────────────────┤
│  poster_fig1_knob_impact.png   │  poster_fig2_layout_mechanism.png  │
│  (measured effect of each knob)│  (the headline finding)            │
├────────────────────────────────┴────────────────────────────────────┤
│                  poster_fig_results.png   (numbers + cycle law)     │
├─────────────────────────────────────────────────────────────────────┤
│  FINDINGS — 3 one-line statements                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## The only text you need to typeset

### Panel heading

> **Module 01 — Compute & Data Delivery Module** · 214056U
> *Stationary schemes · Memory layouts · Interconnect casting*

### Research Gap  *(keep as a bordered box, 3 bullets)*

- Stationary schemes and memory layouts are always studied **separately** —
  their combined effect is unknown.
- Interconnect casting is **hard-wired** in existing simulators; it cannot be
  changed and measured.
- No cycle-accurate framework brings all three together as measurable knobs.

### Findings  *(bottom strip, 3 lines — no sub-bullets)*

- **Casting is the biggest lever** on off-chip traffic.
- **Memory layout changes requests, not data volume.**
- **The best configuration is not fixed** — it changes with the array size.

### Figure captions  *(small italic, under each figure)*

| Figure | Caption |
|---|---|
| `poster_fig_knobs.png` | *One parameterised RTL module — every knob is a real hardware control.* |
| `poster_fig_flow.png` | *Measure first, then model: the framework is built on measured hardware.* |
| `poster_fig1_knob_impact.png` | *tiny_cnn layer_00, 8×8 array — measured RTL.* |
| `poster_fig2_layout_mechanism.png` | *Same 1,836 beats in every layout; 13× fewer bursts → 1.86× faster.* |
| `poster_fig_results.png` | *Verified and measured against RTL; energy is modelled.* |

That is the whole text budget. Everything else is a figure.

---

## The five figures

All 300 dpi, generated from measured RTL by `make_poster_figs.py`.

| File | Replaces | Size |
|---|---|---|
| `poster_fig_knobs.png` | the **Contribution** bullet list | wide, short |
| `poster_fig_flow.png` | the **Method** bullet list | full width, very short |
| `poster_fig_results.png` | the **Results** bullet list | full width, short |
| `poster_fig1_knob_impact.png` | the old 3-panel chart | half width |
| `poster_fig2_layout_mechanism.png` | — (kept, redrawn bolder) | half width |

**Why `poster_fig1_knob_impact.png` changed:** the old version was three
side-by-side panels with vertical bars. Shrunk to poster size the labels became
unreadable. It is now **horizontal bars** — the setting names sit flat and
legible, all nine measured settings are on one axis, grouped and separated by
knob, with the best setting in green.

---

## If the panel is still too tall

Drop in this order:

1. `poster_fig1_knob_impact.png` — its message is already in the number tiles.
2. The Findings strip — the figures carry the same three points.
3. The Method flow — merge into one sentence under the knobs figure.

**Never drop:** the knobs figure (says what you built), `poster_fig2` (best
finding), the results tiles (all the evidence numbers in one strip).

---

## Number corrections — do these before printing

**1. "27 / 27 configurations verified" is wrong.** 27 is the size of the design
space (3×3×3), not the number verified. The verified set is **22 / 22** — every
configuration with a TensorFlow verdict file, all passing, worst error 0.0499 %.
The new results figure already says 22 / 22.

> Where 22 comes from: `results/golden_check/raw/*_verdict.json`, excluding 7
> internal debug *probe* runs. Composition: 3 stationary schemes, 3 layouts,
> 3 casting schemes, 3 array sizes (8×8 / 8×2 / 8×1), 2 memory backends
> (STAMP / PAGED), across 5 layer shapes from 2 TensorFlow models.

> Two other counts float around — do not use them: **29** is the raw file count
> including the debug probes (worst error there is 106 %), and **26** is the
> notebook chart, which adds 4 bank-sweep runs belonging to Module 02's axis.

**2. Say "configurations", not "workloads".** A workload is a set of layer
shapes; a configuration is one (stationary × layout × casting × array) setting.

**3. Do not claim bank counts (2/4/8/16) on this panel** — every Module 01
verdict has `num_banks = 4`. The bank sweep is Module 02's.

**4. Label any ResNet-50 / BERT-Large / DLRM chart** as *"analytical model — not
RTL-measured"*, wherever it appears on the poster.

---

## If an evaluator asks "only two small models — how does this generalise?"

> "The framework decides from **workload geometry** — layer dimensions — not from
> the trained model. Weight values never affect cycles or traffic here, so the
> network's identity is irrelevant; only its dimensions matter. Across 22
> verified configurations I cover **all three stationary schemes, all three
> layouts, all three casting schemes and three array sizes** — every axis the
> framework chooses over. The traffic model has **no fitted constants** and
> reproduces measured beats exactly, including at array widths it was never
> fitted to. Larger networks repeat the same validated per-tile computation more
> times; they do not create new behaviour."

**Honest limit, if pressed:** the RTL sweep varies **one knob at a time**, so
each knob's own effect is measured but knob *interactions* are composed
analytically, not measured.
