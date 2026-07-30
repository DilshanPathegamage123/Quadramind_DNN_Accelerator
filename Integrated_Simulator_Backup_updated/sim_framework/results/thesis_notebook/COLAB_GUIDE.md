# Running the results notebook in Google Colab — step by step

This folder contains everything needed to present this project's results in
Google Colab, for a live evaluation or for pulling tables and figures into a
thesis. The notebook covers two parts:

- **Part A — Member 1** (stationary schemes / memory layouts / casting
  schemes / analytical chooser)
- **Part B — Member 2** (on-chip scratchpad banking, bank conflicts and
  memory-side stalls; stamp-based static tagless vs page-table dynamic
  memory management)

| File | What it is |
|---|---|
| `chooser_validation.ipynb` | The notebook itself — loads real data, prints tables, draws charts |
| `data_bundle.zip` | A ~0.5 MB copy of the real result files the notebook reads (RTL verdicts, traffic CSVs, chooser evaluation CSVs) |
| `data_bundle/README.md` | Exactly which file came from which source path in this repo, and its measured/model status |

Both files were verified by extracting every code cell and running it end to
end against `data_bundle.zip` before being committed — it runs clean with no
errors.

## Step 1 — Open Colab

Go to **[colab.research.google.com](https://colab.research.google.com)**.
Sign in with any Google account (a personal one is fine — nothing here is
uploaded anywhere except to your own Colab session).

## Step 2 — Upload the notebook

`File → Upload notebook → Browse` → select `chooser_validation.ipynb` from
this folder. It opens as a live, editable notebook, exactly like a local
Jupyter notebook.

*(Alternative: if this repository is pushed to GitHub, you can instead use
`File → Open notebook → GitHub`, paste the repo URL, and pick the file
directly — no manual upload needed on the day of the evaluation.)*

## Step 3 — Run the first cell and upload the data

Click the first code cell (the one starting with `# Setup`) and press
**Shift+Enter**. Colab will show a file picker — select `data_bundle.zip`
from this folder. It unzips automatically into the session; nothing further
to configure.

*(If you re-run the notebook later in the same session, this step is
skipped automatically — Colab detects the folder is already there.)*

## Step 4 — Run everything

`Runtime → Run all`. Every remaining cell runs top to bottom in under a few
seconds — there are no external installs and no network calls; `pandas`,
`numpy`, and `matplotlib` are preinstalled in every Colab session.

## Step 5 — Using it live in an evaluation

- Run all cells **before** the session starts, so nothing has to load on
  screen while you're being watched.
- Each section has its own markdown header (`## 1 · Simulator correctness…`,
  `## 2 · Off-chip traffic…`, then `# Part B — On-chip memory management`
  with subsections `B1`–`B4`) — use Colab's outline view (the ☰ icon,
  top-left) to jump straight to a section if a panel member asks about one
  specific topic.
- **For the Member-2 walkthrough**, the four anchors are: `B1` the exact
  bank-conflict law (16/16 configurations), `B2` banking affects on-chip
  stalls only, `B3` the STAMP-vs-PAGED trade-off scorecard, `B4` measured
  silicon cost. The `Part B summary` cell at the end states the claim and,
  deliberately, the three things that are *not* claimed — have that on
  screen if the panel probes the limits.
- Every printed table and chart states its own provenance
  (`[MEASURED (RTL)]` or `[MODEL (analytical)]`) directly above it — you
  don't have to remember which is which mid-answer.

## Step 6 — Pulling results into the thesis

- **Figures:** right-click any chart output → *Save image as…* (PNG).
  Colab renders at 110 DPI by default here, high enough for print.
- **Tables:** the last cell exports the correctness-margin table as
  `correctness_margin_export.csv` — download it from the file browser (the
  folder icon on the left sidebar). Every other table in the notebook can be
  exported the same way by adding `.to_csv('name.csv')` to its cell.
- **LaTeX:** if your thesis is written in LaTeX, add `!pip install jinja2`
  in a new cell (one-time, only needed for this), then `df.to_latex()` on
  any table produces a ready-to-paste LaTeX table — the last cell in the
  notebook already shows this pattern.
- **Whole notebook as a PDF appendix:** `File → Print → Save as PDF`
  produces a clean, paginated version of the entire notebook (text, tables,
  and inline charts together) — usable directly as a thesis appendix.

## If a data file goes stale

The bundle is a frozen copy. If the underlying results change (e.g. the
chooser is re-evaluated after a further fix), regenerate the bundle from
the live repo before re-zipping:

```bash
cd sim_framework
rm -rf results/thesis_notebook/data_bundle
mkdir -p results/thesis_notebook/data_bundle/{golden_check/raw,golden_check/figures,chooser,reports,edge_cloud_sample,member2}
cp results/golden_check/raw/*.json        results/thesis_notebook/data_bundle/golden_check/raw/
cp results/golden_check/figures/*.csv     results/thesis_notebook/data_bundle/golden_check/figures/
cp results/chooser/*.csv                  results/thesis_notebook/data_bundle/chooser/
cp results/golden_check/*.md results/chooser/CHOOSER_REPORT.md \
                                           results/thesis_notebook/data_bundle/reports/
cp results/edge/exp7_hw_verification/*.csv results/edge/exp1_stationary_layout/data.csv \
                                           results/thesis_notebook/data_bundle/edge_cloud_sample/

# Part B (Member 2) tables -- regenerated from the raw RTL counters
PYTHONPATH=. python scripts/make_member2_tables.py

cd results/thesis_notebook && zip -r -q data_bundle.zip data_bundle
```

`make_member2_tables.py` writes into both `results/member2/` and the bundle,
so the copy step above is not needed for those tables.

## Regenerating the Member-2 (Part B) results from scratch

The tables in Part B are built from the raw RTL counter files that are
already in `results/golden_check/raw/`, so no re-simulation is needed:

```bash
cd sim_framework
PYTHONPATH=. python scripts/make_member2_tables.py
```

The **hardware-cost table (B4)** is the one part that needs Vivado, because
it is real out-of-context synthesis rather than an estimate:

```bash
python scripts/synth_memory_hw.py            # ~15-40 min, 9 targets
PYTHONPATH=. python scripts/make_member2_tables.py   # picks up the results
```

If synthesis has not been run, the B4 cells print instructions and skip
cleanly — the rest of Part B is unaffected. Nothing in B4 is ever estimated:
a target that fails to synthesise is reported as unavailable with Vivado's
own error text.

To re-insert or update the Part B notebook cells after editing them:

```bash
python scripts/add_member2_notebook_cells.py
```

This replaces the previously inserted Part B block rather than appending a
second copy, and leaves every Part A cell untouched.

Nothing in the notebook itself needs to change — it reads from whatever is
in the bundle at run time.
