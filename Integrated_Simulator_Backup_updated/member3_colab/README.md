# Member 3 — Multi-DNN Scheduler Module: Colab presentation pack

Everything needed to render the Member-3 evidence pack (tables, charts and
narrative) in Google Colab, from the project's own real data.

```
member3_colab/
├── member3_scheduler_analysis.py   ← the script you run in Colab
├── member3_colab.zip               ← the whole pack, ready to upload
├── data/                           ← 16 CSVs exported from the project
└── figures/                        ← PNGs (regenerated on every run, 200 dpi)
```

---

## 1. Running it in Google Colab (three steps)

**Step 1 — new notebook.** Go to <https://colab.research.google.com>,
`File → New notebook`.

**Step 2 — upload the pack.** In the first cell, paste and run:

```python
from google.colab import files
files.upload()          # a file picker appears — choose member3_colab.zip
!unzip -o -q member3_colab.zip
```

*(Alternative: open the Files pane on the left, drag `member3_colab.zip` in,
then run just the `!unzip -o -q member3_colab.zip` line.)*

**Step 3 — run the analysis.** In the next cell:

```python
%run member3_scheduler_analysis.py
```

That is all. Every section, table and figure renders inline, in order, with
its description. It takes a few seconds and needs no `pip install` — pandas,
numpy and matplotlib are pre-installed in Colab.

### Optional extras once it has run

Query the chooser for any of the 32 workload-mix × objective combinations:

```python
recommend("mix1", "area")           # mix1..mix4
recommend("mix4", "turnaround_us")  # makespan | turnaround | wait | weighted
                                    # turnaround_us | throughput | area | power
```

Download all the figures as PNGs for your slide deck:

```python
!zip -q -r figures.zip figures
from google.colab import files
files.download("figures.zip")
```

### If Colab cannot find the data

The script searches `./data`, `./member3_colab/data`, `/content/data` and
`/content/member3_colab/data`, and will auto-extract any zip in the working
directory that contains the dataset. If it still fails, check that
`data/00_manifest.csv` exists after unzipping:

```python
!ls data | head
```

---

## 2. What the notebook shows

| Section | Content | Figures |
|---|---|---|
| 1 | Goal, research gap, contribution; the 14-scheduler inventory | Fig 1 |
| 2 | The 4 multi-DNN workload mixes and their per-task cost | Fig 2 |
| 3 | Measured Vivado hardware cost: area, Fmax, power, design space | Figs 3–5 |
| 4 | The measured clock vs the project's assumed 1.0 GHz | Fig 6 |
| 5 | The analytical scheduler-chooser + a live query | — |
| 6 | **Headline:** the ranking inverts once the real clock is applied | Figs 7–8 |
| 7 | Validation against measured RTL: dispatch order, makespan flatness | Fig 9 |
| 8 | Chooser evaluation: accuracy, sensitivity, speed, tests | Figs 10–11 |
| 9 | The four findings, and the synthesis fixes | Fig 12 |
| 10 | Provenance; the constant-factor model that was **not** used | Fig 13 |
| 11 | Summary scorecard | — |

---

## 3. The dataset — and where every number comes from

`data/00_manifest.csv` carries this same table, machine-readable.

| File | Rows | Provenance |
|---|---|---|
| `01_scheduler_inventory.csv` | 14 | RTL source + Vivado status |
| `02_scheduler_hw_measured.csv` | 14 | **measured (Vivado 2025.2 OOC)** |
| `03_ranked_all_mixes_goals.csv` | 448 | model + measured + derived |
| `04_eval_decision_accuracy.csv` | 32 | model / measured |
| `05_eval_sensitivity.csv` | 32 | model / measured |
| `06_eval_anchor_order.csv` | 5 | **measured (RTL)** vs model |
| `07_eval_anchor_flatness.csv` | 3 | **measured (RTL)** vs model |
| `08_eval_speed.csv` | 4 | measured |
| `09_golden_rtl_runs.csv` | 15 | **measured (RTL)** |
| `10_workload_mixes.csv` | 14 | workload definition + model |
| `11_exp5_factor_model.csv` | 40 | **ASSUMED — not measured** (contrast case only) |
| `11b_scheduler_factor_table.csv` | 10 | **ASSUMED — not measured** (contrast case only) |
| `12_static_vs_dynamic.csv` | 28 | analytical model × assumed factors |
| `13_findings.csv` | 4 | measured (Vivado tool output) |
| `14_fmax_vs_clock_assumption.csv` | 13 | measured vs source constant |

Four labels are used throughout, and each one travels with its value into the
CSV and into the rendered figure caption:

- **measured (Vivado)** — real out-of-context synthesis of each scheduler
  module on `xc7a100tcsg324-1`, Vivado 2025.2, 10 ns constraint. LUT, FF,
  DSP, BRAM, power, WNS → Fmax.
- **measured (RTL)** — dispatch order, per-task cycles and total cycles from
  the recorded golden simulation runs of `multi_dnn_top`.
- **model** — the queueing simulation over the RTL selection rules,
  transcribed line by line. Zero fitted constants. A **rank** score, never an
  absolute cycle prediction.
- **derived** — arithmetic on the two above (wall-clock turnaround,
  throughput, scheduler energy, the Fmax-vs-assumption factor).

Schedulers with no measured value are **excluded and named**, never given a
substitute number. That rule is enforced by the unit tests.

---

## 4. Regenerating the dataset

The dataset is produced by a script inside the framework, so it can always be
refreshed against the current results:

```bash
cd Integrated_Simulator_Backup_updated/sim_framework
source .venv/bin/activate
PYTHONPATH=. python scripts/eval_sched_chooser.py      # refresh the evaluations
PYTHONPATH=. python scripts/export_member3_dataset.py  # rebuild member3_colab/data
cd ../member3_colab && zip -r member3_colab.zip member3_scheduler_analysis.py data README.md
```

To re-measure the hardware (needs Vivado):

```bash
PYTHONPATH=. python scripts/synth_scheduler_hw.py            # all 14, ~25 min
PYTHONPATH=. python scripts/synth_scheduler_hw.py --only BATCHDNN_PP
```

`BATCHDNN_PP` is the one scheduler still unmeasured: its RTL fixes are in
place and it elaborates cleanly, but Vivado needs roughly 12 GB to synthesise
it and was OOM-killed four times on the build machine. Re-run that command on
a host with more memory or swap and the table becomes 14/14.

---

## 5. Source files in the project

| What | Path (relative to `sim_framework/`) |
|---|---|
| Scheduler RTL | `rtl/schedulers/*.sv` |
| Chooser module | `pysim/scheduler_chooser.py` |
| Chooser CLI | `scripts/choose_scheduler.py` |
| Vivado synthesis harness | `scripts/synth_scheduler_hw.py` |
| The five evaluations | `scripts/eval_sched_chooser.py` |
| Dataset exporter | `scripts/export_member3_dataset.py` |
| Unit tests (34 passing) | `tb/unit/test_scheduler_chooser.py`, `tb/unit/test_scheduler_synth_fix.py` |
| Full written report | `results/sched_chooser/SCHEDULER_CHOOSER_REPORT.md` |
| Raw Vivado reports | `results/sched_chooser/hw/reports/` |
