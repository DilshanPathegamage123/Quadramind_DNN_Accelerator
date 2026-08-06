# Data bundle — for the Colab validation/results notebook

This folder is a curated copy of real result files already in this repository.
Nothing here is regenerated or altered — every file is copied byte-for-byte
from its source location so it can be uploaded to Google Colab (which has no
access to this machine's filesystem).

## Contents

| Folder | Source | What it is |
|---|---|---|
| `golden_check/raw/` | `results/golden_check/raw/*.json` | Every real Verilator + cocotb RTL run this project recorded: per-run correctness (`verdict.json`), and raw counters (AXI beats, AR requests, bank conflicts, cycles). **Measured (RTL).** |
| `golden_check/figures/` | `results/golden_check/figures/*.csv` | The pre-extracted summary tables behind the 7 golden-check figures (correctness margin, data-delivery traffic, memory management, scheduler behaviour, etc.). **Measured (RTL)**, except `f3_cycle_fidelity.csv` and `f7_loop_optimization.csv`, which are labelled `model` in their own `source` column. |
| `chooser/` | `results/chooser/*.csv` | The analytical configuration-chooser's ranked tables and its 4-part evaluation (decision accuracy, optimality gap, speed, anchor check vs. measured RTL). **Model**, cross-checked against `golden_check/raw/`. |
| `reports/` | `results/golden_check/*.md`, `results/chooser/CHOOSER_REPORT.md` | The full written reports these tables were drawn from, with every claim's measured-vs-model labels and honesty caveats intact. |
| `edge_cloud_sample/` | `results/edge/exp1_.../data.csv`, `results/edge/exp7_.../*.csv` | A **small sample only** — NOT the full edge/cloud suite — included purely to illustrate what that suite is. See the notebook's dedicated section: none of it is RTL-measured; `exp7`'s `rtl_actual` column and FPGA utilisation numbers are computed from fixed assumed multipliers and a hand-authored formula, not from any hardware run. |

## Source of truth

If a number in the notebook ever needs re-verifying, the authoritative copy
is the original path in the repository (`sim_framework/results/...`), not
this bundle. This bundle exists only so Colab — which runs on Google's
servers with no filesystem access to this project — can read the same data.
