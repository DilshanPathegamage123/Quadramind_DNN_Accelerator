# Module 01 — poster & presentation material (214056U)

Deliverables for the final evaluation: the poster panel content for Module 01,
two poster-resolution figures, and an update deck for the viva.

| File | What to do with it |
|---|---|
| `MODULE01_POSTER_CONTENT.md` | **Read this first.** The lean panel layout, the ~60 words of text you still need to typeset, figure captions, and the number corrections to make before printing. |
| `poster_fig_knobs.png` | What was built — replaces the Contribution bullet list. |
| `poster_fig_flow.png` | The 6-step method — replaces the Method bullet list. |
| `poster_fig_results.png` | Number tiles + the cycle law — replaces the Results bullet list. |
| `poster_fig1_knob_impact.png` | Measured effect of each knob (horizontal bars, legible when small). |
| `poster_fig2_layout_mechanism.png` | The headline finding. **Keep this one if only one figure fits.** |
| `Module01_Presentation_Update.pptx` | 6 slides: 4 new, 1 corrected, 1 summary. Copy them into the main deck. |
| `make_poster_figs.py` | Regenerates all five figures from the measured RTL data. |
| `make_presentation.py` | Regenerates the deck. |

The panel was previously mostly prose. Three of its text blocks are now figures,
so the only remaining body text is the Research Gap (3 bullets), three
one-line findings, and the figure captions.

## Regenerating

```bash
cd sim_framework
PYTHONPATH=. ~/simenv/bin/python results/module01_poster_slides/make_poster_figs.py
~/simenv/bin/python results/module01_poster_slides/make_presentation.py
```

`make_presentation.py` needs `python-pptx` (installed into `~/simenv` for this).
`make_poster_figs.py` needs only matplotlib and reads
`results/golden_check/raw/*.json` — every number in both figures is measured RTL.

## What the deck contains

| # | Slide | Why it is there |
|---|---|---|
| 1 | How the Work Fits Together | The 6-step flow. This was the missing piece — it separates "verify correctness" from "measure cost", and shows model→validate as a loop. |
| 2 | Where Every Number Comes From | Measured / model / assumed. Pre-empts "is this simulated or calculated?" |
| 3 | Why Large Networks Are Not Run in RTL | The scaling argument with real timings, turned into the justification for the analytical framework. |
| 4 | Verification (corrected) | Replaces the old slide. **26 configurations, not 29** — see the correction note on the slide. |
| 5 | What Generalises — and What Does Not | The generalisation claim plus the honest limits, stated before anyone asks. |
| 6 | Module 01 — Summary | Contribution + the five findings with their evidence. |

## Two things to fix in the existing deck and poster

1. **Verified count → 22.** The deck said "29 workloads", the poster draft said
   "27 / 27". Both are wrong. **22** is the number of configurations carrying a
   TensorFlow verdict file, all passing, worst error 0.0499 %.
   *29* is the raw file count including 7 debug *probe* runs (worst error 106 %);
   *27* is the size of the design space, not the verified set; *26* is the
   notebook chart, which adds 4 bank-sweep runs from Module 02's axis.
2. **"workload" → "configuration".** A workload is a set of layer shapes; a
   configuration is one (stationary × layout × casting × array) setting. You
   verified 22 configurations built from 5 layer shapes.
