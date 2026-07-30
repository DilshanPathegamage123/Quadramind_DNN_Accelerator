#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
member3_scheduler_analysis.py
=============================
Member 3 -- Multi-DNN Scheduler Module: results, analytics and findings.

Run this in Google Colab to render the complete evidence pack for the
multi-DNN scheduling contribution: the plug-and-play scheduler framework,
the measured hardware cost of every scheduler, the analytical
scheduler-chooser, its validation against measured RTL, and the four
findings the work produced.

    HOW TO RUN IN COLAB
    -------------------
    1.  Upload `member3_colab.zip` (this file + the data/ folder) using the
        Files pane, or run this in a cell:

            from google.colab import files
            files.upload()          # pick member3_colab.zip
            !unzip -o -q member3_colab.zip

    2.  Then run:

            %run member3_scheduler_analysis.py

        Every table and figure renders inline, in order, with its
        description.  Figures are also written to ./figures/*.png so they
        can be dropped straight into slides.

    Nothing is downloaded and no package beyond pandas/numpy/matplotlib is
    needed -- all three are pre-installed in Colab.

    WHERE THE NUMBERS COME FROM
    ---------------------------
    Every value carries one of four labels, and the label is printed next
    to the figure or table that uses it:

      measured (Vivado)  real out-of-context synthesis of each scheduler
                         module on xc7a100tcsg324-1 (Vivado 2025.2)
      measured (RTL)     recorded golden simulation runs of multi_dnn_top
      model              the queueing simulation over the transcribed RTL
                         selection rules (a RANK score, not a cycle
                         prediction)
      derived            arithmetic on the two above

    One dataset -- 11_exp5_factor_model.csv -- is explicitly NOT measured.
    It is the older hardcoded constant-factor table, included only as the
    contrast case in Section 10.  It is labelled as such everywhere.
"""
from __future__ import annotations

import os
import sys
import textwrap
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# ===========================================================================
# 0.  ENVIRONMENT: locate the data, set up rendering
# ===========================================================================

try:                                    # Colab / Jupyter rich output
    from IPython.display import display, Markdown, HTML
    _RICH = True
except Exception:                       # plain python
    _RICH = False

    def display(x):                     # type: ignore
        print(x)


def _find_data_dir() -> Path:
    """Locate data/ wherever Colab put it; unzip member3_colab.zip if needed."""
    here = Path.cwd()
    candidates = [
        here / "data",
        here / "member3_colab" / "data",
        Path("/content/data"),
        Path("/content/member3_colab/data"),
        Path(__file__).resolve().parent / "data" if "__file__" in globals() else here / "data",
    ]
    for c in candidates:
        if (c / "00_manifest.csv").exists():
            return c

    for z in list(here.glob("*.zip")) + list(Path("/content").glob("*.zip")):
        try:
            with zipfile.ZipFile(z) as zf:
                if any(n.endswith("00_manifest.csv") for n in zf.namelist()):
                    zf.extractall(here)
                    print(f"Extracted {z.name}")
                    return _find_data_dir()
        except Exception:
            continue

    raise SystemExit(
        "\nCould not find the dataset.\n"
        "Upload member3_colab.zip (or the data/ folder) next to this script.\n"
        "In Colab:\n"
        "    from google.colab import files\n"
        "    files.upload()\n"
        "    !unzip -o -q member3_colab.zip\n"
    )


DATA = _find_data_dir()
FIGS = Path.cwd() / "figures"
FIGS.mkdir(exist_ok=True)


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name)


# ---------------------------------------------------------------------------
# Design system: one palette, one chart style, used everywhere.
# Categorical hues are assigned in fixed order and never cycled.
# ---------------------------------------------------------------------------
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
INK3 = "#8a8983"
GRID = "#e6e5e1"

SERIES = ["#2a78d6",  # 1 blue
          "#eb6834",  # 2 orange
          "#1baf7a",  # 3 aqua
          "#eda100",  # 4 yellow
          "#e87ba4",  # 5 magenta
          "#008300",  # 6 green
          "#4a3aa7",  # 7 violet
          "#e34948"]  # 8 red

# Status colours are reserved and never reused as a series colour.
OK_C, WARN_C, BAD_C = "#1baf7a", "#eda100", "#e34948"

FAMILY_C = {"Classical": SERIES[0], "DNN-aware": SERIES[1]}

mpl.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "figure.dpi": 110,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "font.size": 10.5,
    "font.family": "DejaVu Sans",
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK2,
    "axes.titlecolor": INK,
    "axes.titlesize": 12.5,
    "axes.titleweight": "bold",
    "axes.labelsize": 10.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.frameon": False,
    "legend.fontsize": 9.5,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "lines.linewidth": 2.0,
})

_FIGNO = [0]


def finish(fig, ax_or_axes, fname: str, subtitle: str = "", source: str = "",
           source_y: float = -0.02):
    """Grid behind the marks, a source line, save, show."""
    axes = ax_or_axes if isinstance(ax_or_axes, (list, np.ndarray)) else [ax_or_axes]
    for ax in np.ravel(axes):
        ax.set_axisbelow(True)
    if subtitle:
        fig.text(0.005, 1.005, subtitle, ha="left", va="bottom",
                 fontsize=9.5, color=INK2, transform=fig.transFigure)
    if source:
        fig.text(0.005, source_y, source, ha="left", va="top",
                 fontsize=8.5, color=INK3, style="italic",
                 transform=fig.transFigure)
    _FIGNO[0] += 1
    out = FIGS / f"fig{_FIGNO[0]:02d}_{fname}.png"
    fig.savefig(out)
    plt.show()
    plt.close(fig)


# ---------------------------------------------------------------------------
# Narrative helpers
# ---------------------------------------------------------------------------
def md(text: str):
    t = textwrap.dedent(text).strip()
    if _RICH:
        display(Markdown(t))
    else:
        print("\n" + t + "\n")


def h1(t):
    md(f"# {t}")


def h2(t):
    md(f"## {t}")


def h3(t):
    md(f"### {t}")


def note(t):
    """A 'how to read this' line under a figure or table."""
    md(f"> {textwrap.dedent(t).strip()}")


def table(df: pd.DataFrame, caption: str = "", maxrows: int = 60):
    """Render a dataframe as a readable table."""
    if caption:
        md(f"**{caption}**")
    d = df.head(maxrows).fillna("—")
    if _RICH:
        sty = (d.style
               .hide(axis="index")
               .set_table_styles([
                   {"selector": "th",
                    "props": [("background-color", "#f2f1ed"),
                              ("color", INK), ("font-weight", "600"),
                              ("text-align", "left"),
                              ("padding", "6px 10px"),
                              ("border-bottom", f"2px solid {GRID}")]},
                   {"selector": "td",
                    "props": [("padding", "5px 10px"), ("color", INK),
                              ("border-bottom", f"1px solid {GRID}")]},
                   {"selector": "table",
                    "props": [("border-collapse", "collapse"),
                              ("font-size", "13px")]},
               ]))
        display(sty)
    else:
        print(d.to_string(index=False))
    if len(df) > maxrows:
        md(f"*({len(df) - maxrows} further rows not shown)*")


def stat_row(items: list[tuple[str, str, str]]):
    """Headline numbers: (value, label, note)."""
    if not _RICH:
        for v, l, n in items:
            print(f"  {v:>12}   {l}  ({n})")
        return
    cells = "".join(
        f"""<div style="flex:1 1 150px;min-width:150px;padding:12px 14px;
                        background:#f6f5f1;border-radius:10px;
                        border:1px solid {GRID}">
              <div style="font-size:26px;font-weight:700;color:{INK};
                          line-height:1.1">{v}</div>
              <div style="font-size:12.5px;color:{INK2};margin-top:3px;
                          font-weight:600">{l}</div>
              <div style="font-size:11px;color:{INK3};margin-top:2px">{n}</div>
            </div>"""
        for v, l, n in items)
    display(HTML(f"""<div style="display:flex;flex-wrap:wrap;gap:10px;
                                 margin:10px 0 16px 0">{cells}</div>"""))


def label_bars(ax, bars, values, fmt="{:,.0f}", pad=0.01, horizontal=True,
               color=INK2, fontsize=9):
    """Direct labels on bar ends -- selective, never a number on every point
    of a dense series."""
    if horizontal:
        span = ax.get_xlim()[1] - ax.get_xlim()[0]
        for b, v in zip(bars, values):
            ax.text(b.get_width() + span * pad,
                    b.get_y() + b.get_height() / 2, fmt.format(v),
                    va="center", ha="left", fontsize=fontsize, color=color)
    else:
        span = ax.get_ylim()[1] - ax.get_ylim()[0]
        for b, v in zip(bars, values):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + span * pad,
                    fmt.format(v), ha="center", va="bottom",
                    fontsize=fontsize, color=color)


# ===========================================================================
# LOAD EVERYTHING
# ===========================================================================
manifest = load("00_manifest.csv")
inv = load("01_scheduler_inventory.csv")
hw = load("02_scheduler_hw_measured.csv")
ranked = load("03_ranked_all_mixes_goals.csv")
acc = load("04_eval_decision_accuracy.csv")
sens = load("05_eval_sensitivity.csv")
anchor = load("06_eval_anchor_order.csv")
flat = load("07_eval_anchor_flatness.csv")
speed = load("08_eval_speed.csv")
golden = load("09_golden_rtl_runs.csv")
mixes = load("10_workload_mixes.csv")
exp5 = load("11_exp5_factor_model.csv")
factors = load("11b_scheduler_factor_table.csv")
statdyn = load("12_static_vs_dynamic.csv")
findings = load("13_findings.csv")
fmaxgap = load("14_fmax_vs_clock_assumption.csv")

LABEL = dict(zip(inv["scheduler"], inv["label"]))
FAMILY = dict(zip(inv["scheduler"], inv["family"]))

hw_ok = hw[hw["status"] == "ok"].copy()
N_SCHED = len(inv)
N_MEASURED = len(hw_ok)


# ===========================================================================
# SECTION 1 -- WHAT WAS BUILT
# ===========================================================================
h1("Member 3 — Multi-DNN Scheduler Module")

md(f"""
**Goal.** Design and validate multi-task schedulers for a Multi-DNN hardware
accelerator, compare classical scheduling algorithms against the DNN-aware
schedulers **AI-MT**, **BATCH-DNN** and **BATCH-DNN++** under *identical*
hardware conditions, and quantify the impact of the scheduling policy on
performance, utilisation and energy.

**Research gap.** Prior work evaluates a single scheduling method, or
optimises for one objective in isolation. There is no common framework in
which a traditional scheduler and an advanced Multi-DNN scheduler are run on
the same accelerator, on the same workload, and measured with the same
metrics — so published comparisons are not comparable.

**Contribution.** A plug-and-play scheduling simulator in which
**{N_SCHED} schedulers** share one accelerator, one workload set and one
metric set, plus an **analytical chooser** that ranks all {N_SCHED} for any
workload mix and any objective in under a millisecond, and reports which
of them the FPGA can actually build.
""")

stat_row([
    (f"{N_SCHED}", "schedulers integrated",
     "11 classical + 3 DNN-aware, one wrapper"),
    (f"{N_MEASURED}/{N_SCHED}", "measured in Vivado",
     "real OOC synthesis, xc7a100t"),
    (f"{int(inv.drop_duplicates('rtl_module')['rtl_lines'].sum()):,}",
     "lines of scheduler RTL",
     f"{inv['rtl_module'].nunique()} SystemVerilog policy modules"),
    ("32/32", "chooser decisions correct",
     "4 mixes x 8 goals vs exhaustive re-scoring"),
    ("5/5", "dispatch orders match RTL",
     "model vs recorded golden runs"),
])

h2("1.1  The scheduler inventory — what the RTL actually implements")

md("""
All {n} schedulers are addressable at run time through a single 5-bit
`scheduler_select` on `unified_scheduler_wrapper.sv`. That is the
*plug-and-play* property: swapping the scheduling policy changes one input,
not the design. Two families sit behind it because their interfaces are
genuinely different — the classical family consumes a FIFO task queue, the
DNN-aware family consumes a scheduling **table** with split memory-task /
compute-task outputs.
""".format(n=N_SCHED))

inv_show = inv[["select_code", "label", "family", "rtl_module", "rtl_lines",
                "wrapper", "preemptive_in_rtl", "synthesis_status",
                "has_golden_rtl_run"]].copy()
inv_show.columns = ["Select code", "Scheduler", "Family", "RTL module",
                    "RTL lines", "Wrapper", "Preemptive in RTL",
                    "Vivado synthesis", "Has measured RTL run"]
table(inv_show, "Table 1 — the 14 schedulers, their RTL modules and status")

note("""
**How to read this.** *Select code* is the value written to
`scheduler_select`. *Preemptive in RTL* records that the selector re-decides
every cycle — but the dispatch FSM in `multi_dnn_top` holds a task until it
completes, so preemption cannot manifest in this integration; this is why
several policies produce an identical dispatch order.
*Vivado synthesis* = `ok` means the module was really built and measured.
""")

# --- Figure 1: RTL implementation size per module ---------------------------
mod = (inv.drop_duplicates("rtl_module")
          .sort_values("rtl_lines", ascending=True))
fig, ax = plt.subplots(figsize=(9, 4.2))
cols = [FAMILY_C[f] for f in mod["family"]]
bars = ax.barh(mod["rtl_module"].str.replace("rtl/schedulers/", "", regex=False),
               mod["rtl_lines"], color=cols, height=0.62)
ax.set_xlabel("Lines of SystemVerilog in the module")
ax.set_ylabel("Scheduler RTL module")
ax.set_title("Implementation size of the scheduler RTL")
ax.grid(axis="x")
ax.set_xlim(0, mod["rtl_lines"].max() * 1.18)
label_bars(ax, bars, mod["rtl_lines"].values)
ax.legend(handles=[Patch(color=FAMILY_C[k], label=k) for k in FAMILY_C],
          loc="lower right", title="Scheduler family",
          title_fontsize=9.5)
finish(fig, ax, "rtl_size",
       "Figure 1 — the DNN-aware schedulers carry most of the complexity",
       "Source: line counts of rtl/schedulers/*.sv in the project tree.")

note(f"""
**What it shows.** `task_scheduler.sv` implements seven classical policies in
{int(mod.loc[mod['rtl_module'].str.contains('task_scheduler.sv') & ~mod['rtl_module'].str.contains('advanced'), 'rtl_lines'].iloc[0])}
lines, while BATCH-DNN++ alone needs
{int(mod.loc[mod['rtl_module'].str.contains('batchdnn_pp'), 'rtl_lines'].iloc[0])}.
The sub-batch pipelining and scheduling-table machinery of the DNN-aware
family is where the design cost sits — and, as Section 3 shows, where the
silicon cost sits too.
""")


# ===========================================================================
# SECTION 2 -- THE WORKLOADS
# ===========================================================================
h2("2.  The workloads the schedulers are asked to schedule")

md("""
Four multi-DNN workload mixes drive the whole study — two edge mixes and two
cloud mixes, drawn from MLPerf Inference v3.0, MLPerf Tiny v1.0 and
DeepBench. Each DNN is represented by four layers covering its
characteristic stages. The point of a *mix* is heterogeneity: tasks with very
different service costs arriving together is exactly the situation in which
the scheduling policy matters.
""")

mixtab = mixes[["mix_label", "mix_name", "dnn", "domain", "n_layers",
                "total_macs_millions", "model_compute_cycles",
                "model_prefetch_beats"]].copy()
mixtab.columns = ["Mix", "Mix description", "DNN task", "Domain", "Layers",
                  "Total MACs (M)", "Model compute cycles",
                  "Model prefetch beats"]
table(mixtab, "Table 2 — the four workload mixes (14 DNN tasks in total)")

note("""
**How to read this.** *Total MACs* is exact arithmetic on the layer shapes.
*Model compute cycles* and *prefetch beats* come from the framework's own
cost estimators (`software_ref.estimate_cycles`,
`config_chooser.prefetch_traffic`) — they are **rank** scores used to order
tasks, not absolute cycle predictions for the hardware.
""")

# --- Figure 2: per-task cost within each mix --------------------------------
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
for ax, (col, title, xlab) in zip(axes, [
        ("total_macs_millions", "Arithmetic work per task",
         "Multiply–accumulate operations (millions)"),
        ("model_compute_cycles", "Modelled service time per task",
         "Model compute cycles on an 8x8 array (rank score)")]):
    d = mixes.sort_values(["mix_id", col])
    ypos = np.arange(len(d))
    cols = [SERIES[0] if dm == "Edge" else SERIES[1] for dm in d["domain"]]
    b = ax.barh(ypos, d[col], color=cols, height=0.66)
    ax.set_yticks(ypos)
    ax.set_yticklabels([f"{r.dnn}  ·  {r.mix_label.replace('Workload ', '')}"
                        for r in d.itertuples()], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel(xlab)
    ax.set_title(title)
    ax.grid(axis="x")
    ax.set_xlim(0, d[col].max() * 1.22)
    label_bars(ax, b, d[col].values,
               fmt="{:,.0f}" if col != "total_macs_millions" else "{:,.1f}")
axes[0].set_ylabel("DNN task  ·  workload mix")
axes[1].legend(handles=[Patch(color=SERIES[0], label="Edge"),
                        Patch(color=SERIES[1], label="Cloud")],
               loc="lower right", title="Deployment domain",
               title_fontsize=9.5)
fig.tight_layout()
finish(fig, axes, "workload_cost",
       "Figure 2 — the mixes are deliberately heterogeneous",
       "Source: layer shapes in scripts/workloads.py (exact) + model cost "
       "estimators. Left panel and right panel are separate scales — they are "
       "different quantities and are never plotted on one axis.")

_r = mixes.groupby("mix_id")["model_compute_cycles"]
_spread = (_r.max() / _r.min()).max()
note(f"""
**What it shows.** Within a single mix the modelled service time spans up to
**{_spread:.0f}x** between the cheapest and the most expensive task. That
spread is what a scheduling policy has to work with: with equal-cost tasks,
every order gives the same answer and the scheduler is irrelevant. The two
panels also disagree in places — MACs alone do not predict service time,
because the array geometry and the dataflow decide how well a layer maps.
""")


# ===========================================================================
# SECTION 3 -- MEASURED HARDWARE COST
# ===========================================================================
h2("3.  Measured hardware cost of every scheduler (real Vivado synthesis)")

md(f"""
Each scheduler module was synthesised **out of context** on the project's own
target part, `xc7a100tcsg324-1`, with Vivado 2025.2 at a 10 ns clock
constraint. These are tool measurements, not estimates from a formula:
{N_MEASURED} of {N_SCHED} schedulers now have real LUT / FF / DSP / power /
Fmax numbers. The one that does not carries **no number at all** rather than a
substituted value.
""")

hwshow = hw.copy()
hwshow["scheduler"] = hwshow["scheduler"].map(lambda s: LABEL.get(s, s))
hwshow = hwshow[["scheduler", "status", "luts", "ffs", "dsps", "brams",
                 "fmax_mhz_post_synth", "power_dynamic_w", "power_static_w",
                 "crit_warnings", "part"]]
hwshow.columns = ["Scheduler", "Status", "LUTs", "Flip-flops", "DSPs",
                  "BRAMs", "Fmax (MHz)", "Dynamic power (W)",
                  "Static power (W)", "Critical warnings", "FPGA part"]
table(hwshow, "Table 3 — measured post-synthesis hardware cost")

note("""
**How to read this.** *Fmax* is `1000 / (constraint_ns − WNS)`, a
post-synthesis estimate: place-and-route will lower it, never raise it.
*Static power* is 0.084 W for every row because it is Artix-7 device
leakage — a property of the chip, not of the scheduler — so ranking is done
on **dynamic** power only. *Critical warnings* flags a real fidelity caveat
that Section 9 explains, rather than hiding it.
""")

# --- Figure 3: area -------------------------------------------------------
d = hw_ok.sort_values("luts")
y = np.arange(len(d))
fig, ax = plt.subplots(figsize=(9.5, 5.4))
h_ = 0.38
b1 = ax.barh(y - h_ / 2, d["luts"], height=h_ - 0.04, color=SERIES[0],
             label="LUTs")
b2 = ax.barh(y + h_ / 2, d["ffs"], height=h_ - 0.04, color=SERIES[1],
             label="Flip-flops")
ax.set_yticks(y)
ax.set_yticklabels([LABEL.get(s, s) for s in d["scheduler"]])
ax.set_xlabel("Resource count on xc7a100tcsg324-1 (LUTs / flip-flops)")
ax.set_ylabel("Scheduler")
ax.set_title("Measured FPGA area of each scheduler")
ax.grid(axis="x")
ax.set_xlim(0, max(d["luts"].max(), d["ffs"].max()) * 1.16)
label_bars(ax, b1, d["luts"].values, fontsize=8.5)
label_bars(ax, b2, d["ffs"].values, fontsize=8.5)
ax.legend(loc="lower right", title="Resource", title_fontsize=9.5)
finish(fig, ax, "area",
       "Figure 3 — a 6x area spread across schedulers that all do the same job",
       "Source: measured (Vivado 2025.2 out-of-context synthesis).")

_lo = d.iloc[0]
_hi = d.sort_values("luts").iloc[-1]
note(f"""
**What it shows.** {LABEL.get(_lo['scheduler'])} needs
**{int(_lo['luts']):,} LUTs**; {LABEL.get(_hi['scheduler'])} needs
**{int(_hi['luts']):,}** — a **{_hi['luts'] / _lo['luts']:.1f}x** span for
modules that all answer the same question, "which task next?". The DNN-aware
schedulers sit at the expensive end because they hold a full scheduling table
(note their flip-flop counts, {int(hw_ok.loc[hw_ok.scheduler == 'AIMT', 'ffs'].iloc[0]):,}
for AI-MT), while the comparator-tree classical policies stay cheap in
registers and pay in logic depth instead.
""")

# --- Figure 4: Fmax and power side by side ---------------------------------
fig, axes = plt.subplots(1, 2, figsize=(13, 5.0))

d = hw_ok.sort_values("fmax_mhz_post_synth", ascending=True)
ax = axes[0]
cols = [OK_C if v >= 80 else (WARN_C if v >= 20 else BAD_C)
        for v in d["fmax_mhz_post_synth"]]
b = ax.barh([LABEL.get(s, s) for s in d["scheduler"]],
            d["fmax_mhz_post_synth"], color=cols, height=0.62)
ax.set_xlabel("Post-synthesis maximum clock frequency (MHz)")
ax.set_ylabel("Scheduler")
ax.set_title("Measured Fmax")
ax.grid(axis="x")
ax.set_xlim(0, d["fmax_mhz_post_synth"].max() * 1.2)
label_bars(ax, b, d["fmax_mhz_post_synth"].values, fmt="{:,.1f}")

d2 = hw_ok.sort_values("power_dynamic_w", ascending=True)
ax = axes[1]
b = ax.barh([LABEL.get(s, s) for s in d2["scheduler"]],
            d2["power_dynamic_w"], color=SERIES[6], height=0.62)
ax.set_xlabel("Dynamic power (W), vectorless estimate")
ax.set_ylabel("Scheduler")
ax.set_title("Measured dynamic power")
ax.grid(axis="x")
ax.set_xlim(0, d2["power_dynamic_w"].max() * 1.25)
label_bars(ax, b, d2["power_dynamic_w"].values, fmt="{:.3f}")
axes[0].legend(handles=[Patch(color=OK_C, label="fast (>= 80 MHz)"),
                        Patch(color=WARN_C, label="moderate (20-80 MHz)"),
                        Patch(color=BAD_C, label="slow (< 20 MHz)")],
               loc="lower right", title="Speed band", title_fontsize=9.5)
fig.tight_layout()
finish(fig, axes, "fmax_power",
       "Figure 4 — clock speed and dynamic power vary far more than area",
       "Source: measured (Vivado 2025.2). Power is a vectorless estimate at "
       "Medium confidence; static device leakage (0.084 W, identical for all) "
       "is excluded so it cannot mask the dynamic differences.")

_f = hw_ok.sort_values("fmax_mhz_post_synth")
note(f"""
**What it shows.** Fmax spans **{_f['fmax_mhz_post_synth'].min():.1f} MHz**
({LABEL.get(_f.iloc[0]['scheduler'])}) to
**{_f['fmax_mhz_post_synth'].max():.1f} MHz**
({LABEL.get(_f.iloc[-1]['scheduler'])}) — a
**{_f['fmax_mhz_post_synth'].max() / _f['fmax_mhz_post_synth'].min():.0f}x**
range. The comparator-tree policies (SJF, EDF, LRU, SRTF) and HRRN are slow
because their selection logic is a deep combinational tree evaluated in one
cycle. Dynamic power ranges
**{hw_ok['power_dynamic_w'].min():.3f} W** to
**{hw_ok['power_dynamic_w'].max():.3f} W**, a
**{hw_ok['power_dynamic_w'].max() / hw_ok['power_dynamic_w'].min():.0f}x**
spread — much wider than the area spread, which is why area is a poor proxy
for energy here.
""")

# --- Figure 5: the cost/speed trade-off ------------------------------------
# The non-dominated set: no other scheduler is both smaller and faster.
_pf = hw_ok.sort_values("luts")
_best, _front = -1.0, []
for r in _pf.itertuples():
    if r.fmax_mhz_post_synth > _best:
        _best = r.fmax_mhz_post_synth
        _front.append(r.scheduler)

fig, ax = plt.subplots(figsize=(9.8, 5.8))
_x0, _y0 = hw_ok["luts"].min() * 0.88, 0
_xm, _ym = hw_ok["luts"].max() * 1.12, hw_ok["fmax_mhz_post_synth"].max() * 1.14
apex = hw_ok.loc[hw_ok["scheduler"] == _front[0]].iloc[0]
ax.add_patch(plt.Rectangle((apex["luts"], _y0),
                           _xm - apex["luts"], apex["fmax_mhz_post_synth"],
                           facecolor="#efeeea", edgecolor="none", zorder=0))
ax.text(_xm * 0.985, apex["fmax_mhz_post_synth"] * 0.93,
        f"dominated region — bigger AND slower than "
        f"{LABEL.get(apex['scheduler'])}",
        ha="right", va="top", fontsize=9.5, color=INK3, style="italic")

for fam, colr in FAMILY_C.items():
    sub = hw_ok[hw_ok["scheduler"].map(FAMILY) == fam]
    ax.scatter(sub["luts"], sub["fmax_mhz_post_synth"], s=115, color=colr,
               edgecolor=SURFACE, linewidth=2, zorder=3, label=fam)

# Manual label offsets where points would otherwise collide.
_OFF = {"SJF": (10, -16), "SRTF": (-10, 10), "FIFO": (10, -16),
        "LIFO": (10, 6), "HRRN": (10, -4), "BATCHDNN": (-12, 12),
        "MLQ": (12, 0)}
for r in hw_ok.itertuples():
    dx, dy = _OFF.get(r.scheduler, (10, 6))
    ax.annotate(LABEL.get(r.scheduler, r.scheduler),
                (r.luts, r.fmax_mhz_post_synth),
                textcoords="offset points", xytext=(dx, dy),
                ha="right" if dx < 0 else "left",
                fontsize=9.5,
                color=INK if r.scheduler in _front else INK2,
                fontweight="bold" if r.scheduler in _front else "normal")

ax.set_xlim(_x0, _xm)
ax.set_ylim(_y0, _ym)
ax.set_xlabel("Area — LUTs on xc7a100tcsg324-1 (lower is better)")
ax.set_ylabel("Post-synthesis Fmax (MHz) — higher is better")
ax.set_title("Area vs achievable clock: the scheduler design space")
ax.grid(True)
ax.legend(loc="lower left", title="Scheduler family", title_fontsize=9.5)
finish(fig, ax, "pareto",
       "Figure 5 — cheap does not mean slow; expensive does not mean fast",
       "Source: measured (Vivado 2025.2). Each point is one synthesised "
       "scheduler module. The shaded region contains every design that is "
       "both larger and slower than the non-dominated one.")

note(f"""
**What it shows.** The design space is *not* a trade-off curve — it has a
single corner. **{LABEL.get(apex['scheduler'])}** is simultaneously the
smallest ({int(apex['luts']):,} LUT) **and** the fastest
({apex['fmax_mhz_post_synth']:.1f} MHz), so every one of the other
{len(hw_ok) - 1} measured schedulers sits in the shaded region: strictly worse
on both axes. HRRN is large *and* the slowest of all, because exact
response-ratio comparison infers ~30 wide multipliers — it is the only
scheduler that consumes DSP blocks (60 of the part's 240). This is how a
designer reads the chart: if a policy is not buying you better *scheduling*,
there is no hardware reason to pay for it.
""")


# ===========================================================================
# SECTION 4 -- FINDING 4: THE CLOCK ASSUMPTION
# ===========================================================================
h2("4.  The measured clock, against the clock the project assumed")

md("""
The framework's evaluation scripts assume a **1.0 GHz** operating frequency
for every throughput and GOPS figure. Synthesising the schedulers made that
assumption checkable for the first time. It does not hold: the *fastest*
scheduler module runs at 112.4 MHz, and the complete accelerator cannot be
faster than its slowest component.
""")

fg = fmaxgap.copy()
fgs = fg[["label", "fmax_mhz_measured", "assumed_clock_mhz",
          "optimism_factor", "wns_ns"]]
fgs.columns = ["Scheduler", "Measured Fmax (MHz)", "Assumed clock (MHz)",
               "Assumption is optimistic by", "Worst negative slack (ns)"]
table(fgs, "Table 4 — measured Fmax vs the assumed 1.0 GHz")

fig, ax = plt.subplots(figsize=(9.5, 5.4))
d = fg.sort_values("optimism_factor")
cols = [WARN_C if v < 20 else BAD_C for v in d["optimism_factor"]]
b = ax.barh(d["label"], d["optimism_factor"], color=cols, height=0.62)
ax.axvline(1.0, color=INK2, linewidth=1.4, linestyle="--", zorder=4)
ax.text(1.6, len(d) - 0.42, "1x = the assumption holds", fontsize=9,
        color=INK2, va="bottom")
ax.set_xlabel("Optimism factor of the 1.0 GHz assumption  "
              "(assumed clock / measured Fmax)")
ax.set_ylabel("Scheduler")
ax.set_title("How far the assumed clock is from measured silicon")
ax.grid(axis="x")
ax.set_xlim(0, d["optimism_factor"].max() * 1.16)
label_bars(ax, b, d["optimism_factor"].values, fmt="{:.0f}x")
ax.legend(handles=[Patch(color=WARN_C, label="< 20x optimistic"),
                   Patch(color=BAD_C, label=">= 20x optimistic")],
          loc="lower right", title="Severity", title_fontsize=9.5)
finish(fig, ax, "clock_gap",
       "Figure 6 — every published throughput number is an upper bound",
       "Source: measured Fmax (Vivado) against the CLOCK_GHZ = 1.0 constant "
       "in scripts/run_full_eval.py:80. Derived: assumed / measured.")

note(f"""
**What it shows and why it matters.** Even the best case is
**{fg['optimism_factor'].min():.0f}x** optimistic, and the worst is
**{fg['optimism_factor'].max():.0f}x**. This is a *project-level* finding: it
affects every throughput figure in the repository, not only the scheduling
experiments. The constructive consequence is in Section 6 — once the measured
clock is applied, the ranking of schedulers **inverts**, so any comparison
done in cycles alone gives the wrong recommendation.
""")


# ===========================================================================
# SECTION 5 -- THE ANALYTICAL CHOOSER
# ===========================================================================
h2("5.  The analytical scheduler-chooser")

md(f"""
The chooser answers: *given this workload mix, this array size and this
objective, which of the {N_SCHED} schedulers should be instantiated?* It
scores all {N_SCHED} exhaustively — no RTL run and no synthesis per query —
by combining three ingredients that already existed and were validated
elsewhere in the project:

| Ingredient | Where it comes from | Label |
|---|---|---|
| Per-task service cost | `software_ref.estimate_cycles` | model |
| Memory-task cost | `config_chooser.prefetch_traffic` | model |
| Area / power / Fmax | `synth_scheduler_hw.py` → Vivado | **measured** |

The only genuinely new logic is the **queueing discipline**, transcribed line
by line from the RTL selectors. There are **zero fitted constants**. Eight
objectives are supported:

`makespan` · `turnaround` · `wait` · `weighted` · `turnaround_us` ·
`throughput` · `area` · `power`
""")

# --- Live demo: the chooser as a callable ----------------------------------
GOAL_NICE = {
    "makespan": "Makespan (cycles)",
    "turnaround": "Mean turnaround (cycles)",
    "wait": "Mean wait (cycles)",
    "weighted": "Weighted timing score",
    "turnaround_us": "Mean turnaround (µs, wall-clock)",
    "throughput": "Throughput (tasks/s)",
    "area": "Area (LUTs)",
    "power": "Dynamic power (W)",
}


def recommend(mix_id: str = "mix3", goal: str = "turnaround_us",
              top: int = 14) -> pd.DataFrame:
    """Reproduce a chooser query from the exported ranking table."""
    d = ranked[(ranked.mix_id == mix_id) & (ranked.goal == goal)].copy()
    d = d.sort_values("rank", na_position="last")
    out = d[["rank", "scheduler", "dispatch_order", "mean_turnaround_cycles",
             "mean_wait_cycles", "mean_turnaround_us", "luts", "ffs",
             "power_dynamic_w", "fmax_mhz_post_synth", "hw_status"]].copy()
    out["scheduler"] = out["scheduler"].map(lambda s: LABEL.get(s, s))
    out.columns = ["Rank", "Scheduler", "Dispatch order",
                   "Mean turnaround (cycles)", "Mean wait (cycles)",
                   "Mean turnaround (µs)", "LUTs", "FFs",
                   "Dynamic power (W)", "Fmax (MHz)", "Synthesis"]
    return out.head(top)


h3("5.1  A live query — mix 3 (cloud NLP + vision), goal = wall-clock turnaround")

_q = ranked[(ranked.mix_id == "mix3") & (ranked.goal == "turnaround_us")
            & (ranked["rank"] == 1)].iloc[0]
md(f"""
```
RECOMMENDED: {LABEL.get(_q.scheduler)}
  dispatch order    : {_q.dispatch_order}
  mean turnaround   : {float(_q.mean_turnaround_cycles):,.0f} cycles      (model)
  area              : {int(_q.luts):,} LUT / {int(_q.ffs):,} FF   (measured, Vivado)
  dynamic power     : {float(_q.power_dynamic_w):.3f} W               (measured, Vivado)
  Fmax              : {float(_q.fmax_mhz_post_synth):,.1f} MHz             (measured, post-synthesis)
  turnaround (real) : {float(_q.mean_turnaround_us):,.1f} us            (derived: cycles / Fmax)
```
""")
table(recommend("mix3", "turnaround_us"),
      "Table 5 — full ranking, mix 3, goal = wall-clock turnaround")

_exc = ranked[(ranked.mix_id == "mix3") & (ranked.goal == "turnaround_us")
              & (ranked.excluded)]
note(f"""
**How to read this.** Rank is blank for **excluded** schedulers: a scheduler
with no measured Fmax cannot be ranked on a wall-clock goal, so it is
*excluded and named* rather than given a substituted number. Here that is
{', '.join(LABEL.get(s, s) for s in _exc.scheduler)} — its RTL fixes are in
place and it elaborates cleanly, but Vivado needed roughly 12 GB to
synthesise it and was killed by the memory limit on the build machine.
Change `mix3`/`turnaround_us` in the `recommend(...)` call to query any of the
32 combinations.
""")


# ===========================================================================
# SECTION 6 -- THE HEADLINE RESULT: THE RANKING INVERTS
# ===========================================================================
h2("6.  Headline result — ranking schedulers in cycles gives the wrong answer")

md("""
This is the single most useful thing the framework produces, and it is only
visible because modelled timing and **measured** clock frequency are combined
in the same table.

A scheduler that needs fewer cycles is not necessarily faster in wall-clock
time, because a cleverer selection rule costs combinational depth, which
lowers Fmax. Below, the same schedulers are ranked twice on the same
workload: once on cycles, once on real time.
""")

m3c = ranked[(ranked.mix_id == "mix3") & (ranked.goal == "turnaround")
             & (~ranked.excluded)].copy()
m3u = ranked[(ranked.mix_id == "mix3") & (ranked.goal == "turnaround_us")
             & (~ranked.excluded)].copy()
common = sorted(set(m3c.scheduler) & set(m3u.scheduler))
rc = {r.scheduler: int(r.rank) for r in m3c.itertuples() if r.scheduler in common}
ru = {r.scheduler: int(r.rank) for r in m3u.itertuples() if r.scheduler in common}
# re-rank the cycle side over the common set so both sides are 1..N
rc = {s: i for i, s in enumerate(sorted(common, key=lambda s: rc[s]), 1)}
ru = {s: i for i, s in enumerate(sorted(common, key=lambda s: ru[s]), 1)}

fig, ax = plt.subplots(figsize=(9.5, 6.2))
movers = sorted(common, key=lambda s: abs(ru[s] - rc[s]), reverse=True)[:4]
for s in common:
    delta = ru[s] - rc[s]
    if s in movers and delta > 0:
        colr, lw, alpha, z = BAD_C, 2.6, 1.0, 4       # fell badly
    elif s in movers and delta < 0:
        colr, lw, alpha, z = OK_C, 2.6, 1.0, 4        # rose
    else:
        colr, lw, alpha, z = INK3, 1.4, 0.55, 2
    ax.plot([0, 1], [rc[s], ru[s]], color=colr, linewidth=lw, alpha=alpha,
            zorder=z, marker="o", markersize=7, markeredgecolor=SURFACE,
            markeredgewidth=1.6)
    ax.text(-0.035, rc[s], f"{LABEL.get(s, s)}", ha="right", va="center",
            fontsize=9.5, color=INK if s in movers else INK2,
            fontweight="bold" if s in movers else "normal")
    ax.text(1.035, ru[s], f"{LABEL.get(s, s)}", ha="left", va="center",
            fontsize=9.5, color=INK if s in movers else INK2,
            fontweight="bold" if s in movers else "normal")
ax.set_xlim(-0.42, 1.42)
ax.set_ylim(len(common) + 0.6, 0.4)
ax.set_xticks([0, 1])
ax.set_xticklabels(["Ranked on\nmean turnaround (CYCLES)\n— model only",
                    "Ranked on\nmean turnaround (µs)\n— model x measured Fmax"],
                   fontsize=10.5, color=INK)
ax.set_ylabel("Rank (1 = best)")
ax.set_yticks(range(1, len(common) + 1))
ax.set_title("The same schedulers, the same workload, two different verdicts")
ax.grid(axis="y")
ax.spines["bottom"].set_visible(False)
fig.subplots_adjust(bottom=0.26)
fig.legend(handles=[Line2D([], [], color=BAD_C, lw=2.6, marker="o",
                           label="falls once the real clock is applied"),
                    Line2D([], [], color=OK_C, lw=2.6, marker="o",
                           label="rises once the real clock is applied"),
                    Line2D([], [], color=INK3, lw=1.4, marker="o",
                           label="little change")],
           loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=3,
           title="Rank movement", title_fontsize=9.5)
finish(fig, ax, "rank_inversion",
       "Figure 7 — workload mix 3 (ResNet-50 + BERT-Large + 3D-UNet), 8x8 array",
       "Left: model cycles. Right: model cycles / measured Fmax (derived). "
       "Only schedulers with a measured Fmax appear, since the right-hand "
       "ranking is undefined without one.", source_y=-0.04)

_sjf_c, _sjf_u = rc.get("SJF"), ru.get("SJF")
_sjf_us = float(m3u[m3u.scheduler == "SJF"]["mean_turnaround_us"].iloc[0])
_mlq_us = float(m3u[m3u.scheduler == "MLQ"]["mean_turnaround_us"].iloc[0])
note(f"""
**What it shows.** SJF has the **best** cycle-turnaround on this mix
(rank {_sjf_c}) and the **{_sjf_u}th-best** wall-clock turnaround —
{_sjf_us:,.0f} µs against MLQ's {_mlq_us:,.0f} µs, a
**{_sjf_us / _mlq_us:.1f}x** difference in the direction opposite to what the
cycle count says. The cause is Figure 4: SJF's comparator tree runs at
20.3 MHz while MLQ runs at 112.4 MHz. A scheduler study that reports cycles
alone — which is the norm — would recommend SJF here and be wrong.
""")

# --- Figure 8: the two metrics as absolute values --------------------------
fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), sharey=True)
order = sorted(common, key=lambda s: ru[s])
ypos = np.arange(len(order))

ax = axes[0]
vals = [float(m3c[m3c.scheduler == s]["mean_turnaround_cycles"].iloc[0])
        for s in order]
b = ax.barh(ypos, vals, color=SERIES[0], height=0.62)
ax.set_yticks(ypos)
ax.set_yticklabels([LABEL.get(s, s) for s in order])
ax.invert_yaxis()
ax.set_xlabel("Mean turnaround (thousands of cycles) — model")
ax.set_title("Ranked in cycles")
ax.grid(axis="x")
ax.set_xlim(0, max(vals) * 1.2)
ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, p: f"{v/1e3:,.0f}k"))
label_bars(ax, b, vals, fmt="{:,.0f}", fontsize=8.5)

ax = axes[1]
vals2 = [float(m3u[m3u.scheduler == s]["mean_turnaround_us"].iloc[0])
         for s in order]
cols = [OK_C if v <= 1500 else (WARN_C if v <= 6000 else BAD_C) for v in vals2]
b = ax.barh(ypos, vals2, color=cols, height=0.62)
ax.set_xlabel("Mean turnaround (µs, wall-clock) — derived")
ax.set_title("Ranked in real time")
ax.grid(axis="x")
ax.set_xlim(0, max(vals2) * 1.2)
label_bars(ax, b, vals2, fmt="{:,.0f}", fontsize=8.5)
ax.legend(handles=[Patch(color=OK_C, label="under 1.5 ms"),
                   Patch(color=WARN_C, label="1.5 – 6 ms"),
                   Patch(color=BAD_C, label="over 6 ms")],
          loc="upper right", title="Wall-clock band", title_fontsize=9.5)
fig.tight_layout()
finish(fig, axes, "cycles_vs_time",
       "Figure 8 — both panels are workload mix 3, sorted by real time",
       "Left: model. Right: derived (model cycles / measured Fmax). Separate "
       "axes because the quantities differ; the row order is identical so the "
       "disagreement between panels is the point.")

_cyc_spread = max(vals) / min(vals)
_us_spread = max(vals2) / min(vals2)
_n_distinct = len(set(round(v) for v in vals))
note(f"""
**What it shows.** In cycles, the {len(order)} schedulers collapse into only
**{_n_distinct} distinct values** spanning **{_cyc_spread:.1f}x** — because
policies that pick the same dispatch order are identical on every timing
metric. In real time the same schedulers spread **{_us_spread:.0f}x**, and the
order changes. The information that separates them is measured hardware, not
scheduling theory.
""")


# ===========================================================================
# SECTION 7 -- VALIDATION AGAINST MEASURED RTL
# ===========================================================================
h2("7.  Validation — does the model agree with the hardware?")

md("""
A model that is not anchored to measurement is an opinion. Two anchors were
available from the project's recorded golden simulation runs of
`multi_dnn_top`, and the model was checked against both.
""")

h3("7.1  Anchor A — dispatch order, 5 of 5 exact")

a = anchor.copy()
a["scheduler"] = a["scheduler"].map(lambda s: LABEL.get(s, s))
a = a[["scheduler", "measured_order", "model_order", "match",
       "measured_cycles"]]
a.columns = ["Scheduler", "Measured order (RTL)", "Model order",
             "Exact match", "Measured total cycles"]
table(a, "Table 6 — model dispatch order vs recorded RTL simulation")

# --- Figure 9: dispatch timeline (Gantt) -----------------------------------
g = golden.copy()
scheds = ["FIFO", "LIFO", "AIMT", "BATCHDNN", "BATCHDNN_PP"]
task_colors = {0: SERIES[0], 1: SERIES[1], 2: SERIES[2]}
task_names = {int(r.task_id): Path(str(r.layer)).parent.name + "/" +
              Path(str(r.layer)).name
              for r in g.itertuples()}

fig, ax = plt.subplots(figsize=(12, 5.0))
for i, s in enumerate(scheds):
    sub = g[g.scheduler == s]
    for r in sub.itertuples():
        ax.barh(i, r.task_cycles_measured, left=r.dispatch_cycle_measured,
                height=0.55, color=task_colors[int(r.task_id)],
                edgecolor=SURFACE, linewidth=2)
        if r.task_cycles_measured > 1200:
            ax.text(r.dispatch_cycle_measured + r.task_cycles_measured / 2, i,
                    f"T{int(r.task_id)}", ha="center", va="center",
                    color="white", fontsize=10, fontweight="bold")
ax.set_yticks(range(len(scheds)))
ax.set_yticklabels([LABEL.get(s, s) for s in scheds])
ax.invert_yaxis()
ax.set_xlabel("Simulation cycle (measured in RTL)")
ax.set_ylabel("Scheduler")
ax.set_title("Measured dispatch timeline — the policy changes the order, "
             "not the total")
ax.grid(axis="x")
ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, p: f"{v:,.0f}"))
tot = g.groupby("scheduler")["total_cycles_measured"].first()
ax.set_xlim(0, tot.max() * 1.16)
ax.axvline(tot.max(), color=INK2, linestyle="--", linewidth=1.4)
ax.text(tot.max() * 1.02, len(scheds) - 1,
        f"every scheduler finishes\nwithin 1 cycle of\n{tot.max():,} cycles",
        ha="left", va="center", fontsize=9.5, color=INK2)
fig.subplots_adjust(bottom=0.28)
fig.legend(handles=[Patch(color=task_colors[k],
                          label=f"T{k}  ·  {task_names.get(k, '')}")
                    for k in sorted(task_colors)],
           loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=3,
           title="DNN task in the golden mix", title_fontsize=9.5)
finish(fig, ax, "dispatch_timeline",
       "Figure 9 — recorded RTL execution of the 3-task golden mix, 8x8 array",
       "Source: measured (RTL) — results/golden_check/raw/multi_*_8x8.json. "
       "Bar start = dispatch cycle, bar length = measured task cycles.",
       source_y=-0.04)

note(f"""
**What it shows.** FIFO runs T0 → T1 → T2; LIFO runs T2 → T1 → T0; the three
DNN-aware schedulers all run T0 → T1 → T2. The model predicts every one of
these orders exactly, for all five schedulers. And every scheduler finishes
within one cycle of every other
({tot.min():,} vs {tot.max():,}) — the reordering moves *which* task waits,
never the total busy time.
""")

h3("7.2  Anchor B — makespan flatness, PASS")

f = flat.copy()
f.columns = ["Quantity", "Minimum", "Maximum", "Spread (%) / verdict", "Source"]
table(f, "Table 7 — spread of total execution time, hardware vs model")

note("""
**Why this check exists, and why it is the important one.** On a single
machine that never idles while work is queued, total completion time is
*provably* identical under every ordering — reordering changes who waits, not
how much work there is. The hardware confirms it (0.0075 % spread, one cycle).
The model reproduces that invariance exactly (0.0000 % spread) instead of
inventing a speedup.

This is the check that would catch a fabricated performance claim, and it is
the reason the older constant-factor table in Section 10 — which asserts
1.26x / 1.37x / 1.48x speedups for the DNN-aware schedulers — is **not** used
anywhere in the chooser. The project's own measured runs contradict it.
""")


# ===========================================================================
# SECTION 8 -- CHOOSER EVALUATION
# ===========================================================================
h2("8.  Evaluating the chooser itself")

n_ok = int((acc["match"].astype(str).str.lower() == "true").sum())
h3(f"8.1  Decision accuracy — {n_ok} / {len(acc)}")

md(f"""
For every combination of workload mix and objective, the chooser's top pick
was compared against an independent exhaustive re-scoring pass:
**{n_ok}/{len(acc)} ({100 * n_ok / len(acc):.0f} %)**.

*Stated honestly:* the chooser **is** exhaustive over {N_SCHED} schedulers —
that is the correct algorithm at this size. So this result verifies argmin and
sort consistency, determinism, and that ties are handled by a documented rule.
It is **not** evidence that a heuristic got lucky, and it is not claimed to be.
""")

accs = acc[["mix", "goal", "pick", "pick_value", "true_best_value", "match",
            "n_tied_at_best", "n_ranked", "n_excluded", "source"]].copy()
accs["goal"] = accs["goal"].map(lambda g: GOAL_NICE.get(g, g))
accs["pick"] = accs["pick"].map(lambda s: LABEL.get(s, s))
accs.columns = ["Workload mix", "Objective", "Chooser pick", "Pick value",
                "True best value", "Match", "Schedulers tied at best",
                "Schedulers ranked", "Schedulers excluded", "Source"]
table(accs, "Table 8 — chooser pick vs exhaustive re-scoring, all 32 cases")

h3("8.2  Sensitivity — the recommendation genuinely depends on the question")

pivot = sens.pivot(index="mix", columns="goal", values="pick")
goal_order = [g for g in ["makespan", "turnaround", "wait", "weighted",
                          "turnaround_us", "throughput", "area", "power"]
              if g in pivot.columns]
pivot = pivot[goal_order]

winners = sorted(sens["pick"].unique(),
                 key=lambda s: -int((sens["pick"] == s).sum()))
wcol = {s: SERIES[i] for i, s in enumerate(winners)}

fig, ax = plt.subplots(figsize=(11.5, 3.9))
for yi, mixname in enumerate(pivot.index):
    for xi, g in enumerate(pivot.columns):
        s = pivot.loc[mixname, g]
        ax.add_patch(plt.Rectangle((xi, yi), 0.94, 0.9,
                                   facecolor=wcol[s], edgecolor=SURFACE,
                                   linewidth=2))
        ax.text(xi + 0.47, yi + 0.45, LABEL.get(s, s), ha="center",
                va="center", color="white", fontsize=10.5, fontweight="bold")
ax.set_xlim(0, len(pivot.columns))
ax.set_ylim(len(pivot.index), 0)
GOAL_SHORT = {
    "makespan": "Makespan\n(cycles)",
    "turnaround": "Turnaround\n(cycles)",
    "wait": "Wait\n(cycles)",
    "weighted": "Weighted\nscore",
    "turnaround_us": "Turnaround\n(µs, real)",
    "throughput": "Throughput\n(tasks/s)",
    "area": "Area\n(LUTs)",
    "power": "Power\n(W)",
}
ax.set_xticks([i + 0.47 for i in range(len(pivot.columns))])
ax.set_xticklabels([GOAL_SHORT.get(g, g) for g in pivot.columns], fontsize=9.5)
ax.set_yticks([i + 0.45 for i in range(len(pivot.index))])
ax.set_yticklabels(pivot.index)
ax.set_xlabel("Objective the user asked for", labelpad=10)
ax.set_ylabel("Workload mix")
ax.set_title("Which scheduler the framework recommends")
for sp in ax.spines.values():
    sp.set_visible(False)
ax.tick_params(length=0)
fig.subplots_adjust(bottom=0.36)
fig.legend(handles=[Patch(color=wcol[s], label=LABEL.get(s, s))
                    for s in winners],
           loc="lower center", bbox_to_anchor=(0.5, 0.0),
           ncol=len(winners), title="Recommended scheduler",
           title_fontsize=9.5)
finish(fig, ax, "sensitivity",
       "Figure 10 — 4 workload mixes x 8 objectives = 32 recommendations",
       "Source: model (timing goals) and measured Vivado (area / power / "
       "throughput / wall-clock goals). Cell text names the scheduler, so "
       "identity never depends on colour alone.", source_y=-0.06)

counts = sens["pick"].value_counts()
note(f"""
**What it shows.** {len(counts)} different schedulers win across the 32 cases:
{', '.join(f'**{LABEL.get(k, k)}** {v}x' for k, v in counts.items())}. That
spread is the evidence that the framework is doing real work — a chooser that
always returned the same scheduler would be the hardcoded-constant failure
mode of Section 10 reappearing. Concretely: **MLQ** wins the hardware goals
because it is the smallest and fastest module, **SJF** wins the cycle-timing
goals because it is a genuinely better ordering, and the wall-clock goal —
the one that reflects reality — splits between them.
""")

h3("8.3  Query cost")

sp = speed.copy()
sp.columns = ["What was timed", "Seconds", "Source"]
table(sp, "Table 9 — measured timings")

fig, ax = plt.subplots(figsize=(10, 3.8))
lbl = ["Score 14 schedulers,\none mix (warm)",
       "Score 4 mixes x\n14 schedulers (warm)",
       "Full CLI query,\ncold start",
       "Vivado synthesis of\none scheduler"]
vals = [float(str(speed.iloc[0]["seconds"]).lstrip("~")),
        float(str(speed.iloc[1]["seconds"]).lstrip("~")),
        float(str(speed.iloc[2]["seconds"]).lstrip("~")),
        float(str(speed.iloc[3]["seconds"]).lstrip("~"))]
cols = [OK_C, OK_C, SERIES[0], BAD_C]
b = ax.barh(lbl, vals, color=cols, height=0.6)
ax.set_xscale("log")
ax.set_xlabel("Wall-clock time (seconds, log scale)")
ax.set_ylabel("Operation")
ax.set_title("What a scheduler recommendation costs")
ax.grid(axis="x")
ax.invert_yaxis()
ax.set_xlim(min(vals) * 0.35, max(vals) * 6)
_approx = [str(s).strip().startswith("~") for s in speed["seconds"]]
for bar, v, ap in zip(b, vals, _approx):
    ax.text(bar.get_width() * 1.35, bar.get_y() + bar.get_height() / 2,
            ("~" if ap else "") + (f"{v:,.4f} s" if v < 1 else f"{v:,.0f} s"),
            va="center", fontsize=9.5, color=INK2)
finish(fig, ax, "speed",
       "Figure 11 — the synthesis cost is paid once and cached, not per query",
       "Source: measured. Log scale, because the range spans six orders of "
       "magnitude.")

note(f"""
**What it shows.** Scoring all {N_SCHED} schedulers for one workload mix takes
**{vals[0] * 1e3:.1f} ms** once the libraries are loaded — about
**{vals[3] / vals[0]:,.0f}x** faster than synthesising a single scheduler, and
that comparison understates it, since answering the question by synthesis
would need all {N_SCHED} modules. The Vivado cost is paid once by
`synth_scheduler_hw.py` and cached in a CSV that every later query reads.
""")

h3("8.4  Regression tests")

md("""
`tb/unit/test_scheduler_chooser.py` (21 tests) and
`tb/unit/test_scheduler_synth_fix.py` (13 tests) — **34 passing** — lock down
each policy transcription, the golden-order anchors, the makespan-invariance
property, the behaviour-preservation of the two RTL synthesis fixes over all
32x32 in-range layer windows, and the no-fabrication guarantee: a missing
hardware value must stay empty and must *exclude* the scheduler rather than
be substituted. They run without cocotb, Verilator or Vivado.
""")


# ===========================================================================
# SECTION 9 -- FINDINGS
# ===========================================================================
h2("9.  Findings the framework produced")

md("""
Building a common evaluation framework exposed four problems that no
single-scheduler study would have surfaced. Two were fixed within this work;
two are disclosed with evidence.
""")

for r in findings.itertuples():
    status = str(r.status)
    badge = (OK_C if status.lower().startswith("fixed")
             else (WARN_C if "disclosed" in status.lower() else BAD_C))
    if _RICH:
        display(HTML(f"""
        <div style="border-left:5px solid {badge};background:#f6f5f1;
                    padding:12px 16px;margin:10px 0;border-radius:0 8px 8px 0">
          <div style="font-size:15px;font-weight:700;color:{INK}">
            {r.id} — {r.title}</div>
          <div style="font-size:12px;color:white;background:{badge};
                      display:inline-block;padding:2px 9px;border-radius:20px;
                      margin:7px 0 9px 0;font-weight:600">{status}</div>
          <div style="font-size:13px;color:{INK2};margin-bottom:5px">
            <b style="color:{INK}">Evidence:</b> {r.evidence}</div>
          <div style="font-size:13px;color:{INK2};margin-bottom:5px">
            <b style="color:{INK}">Impact:</b> {r.impact}</div>
          <div style="font-size:13px;color:{INK2}">
            <b style="color:{INK}">Action:</b> {r.action}</div>
        </div>"""))
    else:
        print(f"\n{r.id} — {r.title}  [{status}]\n  Evidence: {r.evidence}"
              f"\n  Impact: {r.impact}\n  Action: {r.action}")

h3("9.1  The synthesis fixes, before and after")

md("""
Three schedulers — HRRN, BATCH-DNN and BATCH-DNN++ — simulated correctly but
could not be synthesised. HRRN computed its response ratio in `real`
(floating-point) arithmetic, which has no hardware mapping; the two BATCH-DNN
variants used a loop whose *start* bound was a runtime value, which the tool
cannot unroll. Both were rewritten behaviour-preservingly on a dedicated
branch, and re-synthesised with the real tool.
""")

before, after = 11, N_MEASURED
fig, ax = plt.subplots(figsize=(9, 3.4))
bars = ax.barh(["Before the fixes", "After the fixes"], [before, after],
               color=[WARN_C, OK_C], height=0.5)
ax.barh(["Before the fixes", "After the fixes"],
        [N_SCHED - before, N_SCHED - after], left=[before, after],
        color="#e6e5e1", height=0.5)
ax.set_xlim(0, N_SCHED)
ax.set_xlabel(f"Schedulers with real measured synthesis results "
              f"(out of {N_SCHED})")
ax.set_ylabel("")
ax.set_title("Buildable schedulers, before and after the RTL synthesis fixes")
ax.grid(axis="x")
for bar, v in zip(bars, [before, after]):
    ax.text(v - 0.25, bar.get_y() + bar.get_height() / 2,
            f"{v} / {N_SCHED}", va="center", ha="right", color="white",
            fontsize=12, fontweight="bold")
ax.invert_yaxis()
finish(fig, ax, "synth_fixes",
       "Figure 12 — 11/14 → 13/14 measured",
       "Source: measured (Vivado 2025.2). The remaining gap is BATCH-DNN++, "
       "whose synthesis exceeded the build machine's memory; it is reported "
       "as 'unavailable' rather than carrying stale numbers.")

note("""
**Honesty note that belongs in the presentation.** HRRN is now buildable, but
the honest measurement is unflattering: exact integer ratio comparison infers
~30 wide multipliers, so it is the only scheduler consuming DSP blocks
(60 of 240) and its Fmax collapses to 6.5 MHz — last place on wall-clock
turnaround. That is a *real cost of exact HRRN*, not an artefact of the
rewrite, and it retires a genuine risk: HRRN wins 4 of the 32 cases on
cycle-only timing, so a cycle-only analysis would have recommended a
scheduler that could not be built at all before this work.
""")


# ===========================================================================
# SECTION 10 -- PROVENANCE / WHAT WAS DELIBERATELY NOT USED
# ===========================================================================
h2("10.  Provenance — what is measured, what is modelled, what was discarded")

md("""
The framework's central discipline is that **no number is invented**. Every
value in every table above is one of four kinds, and the kind travels with the
value into the CSV and into this notebook.
""")

man = manifest.copy()
man.columns = ["Data file", "Provenance", "What it contains"]
table(man, "Table 10 — dataset manifest, with the provenance of each file")

h3("10.1  The constant-factor table that was NOT used")

md("""
An earlier version of the scheduling experiment ranked schedulers using a
hardcoded factor table (`run_full_eval.py:295`), asserting a fixed throughput
multiplier per scheduler — AI-MT 1.26x, BATCH-DNN 1.37x, BATCH-DNN++ 1.48x
over FIFO. That table has **no derivation and no measurement behind it
anywhere in the repository**, and because the factors are constants, it makes
the ranking identical for every workload mix *by construction*.

It is plotted here only to show the failure mode the current framework
replaced. Compare it against Anchor B in Section 7.2, which measured all five
schedulers finishing within **one cycle** of each other.
""")

ft = load("11b_scheduler_factor_table.csv").sort_values(
    "throughput_factor_vs_fifo")
fig, ax = plt.subplots(figsize=(10, 4.6))
b = ax.barh(ft["label"], ft["throughput_factor_vs_fifo"], color=INK3,
            height=0.6)
ax.axvline(1.0, color=INK2, linestyle="--", linewidth=1.4)
ax.set_xlabel("Asserted throughput relative to FIFO (a constant, "
              "identical for every workload)")
ax.set_ylabel("Scheduler")
ax.set_title("NOT MEASURED — the constant-factor model the chooser replaced")
ax.grid(axis="x")
ax.set_xlim(0, ft["throughput_factor_vs_fifo"].max() * 1.2)
label_bars(ax, b, ft["throughput_factor_vs_fifo"].values, fmt="{:.2f}x")
ax.text(0.5, 0.5, "ASSUMED VALUES", fontsize=34, color=BAD_C,
        alpha=0.15, ha="center", va="center", rotation=16,
        fontweight="bold", transform=ax.transAxes)
finish(fig, ax, "assumed_factors",
       "Figure 13 — shown as the contrast case, not as a result",
       "Source: the SCHEDULER_MODEL constant table read directly from "
       "scripts/run_full_eval.py. NOT measured. Contradicted by the "
       "project's own golden runs, which show a 1-cycle spread across five "
       "schedulers.")

note(f"""
**A second reason not to trust it.** The experiment-5 result CSVs committed in
the repository were produced by an *earlier revision* of the same script, and
their speedup column no longer equals these constants — e.g. BATCH-DNN++ is
**{float(ft[ft.scheduler == 'BATCHDNN_PP']['throughput_factor_vs_fifo'].iloc[0]):.2f}x**
in the current source but
**{float(exp5[(exp5.scheduler == 'BATCHDNN_PP') & (exp5.workload_mix == 'Workload mix 3')]['speedup'].iloc[0]):.2f}x**
in the stored `Workload mix 3` result. Both files ship in this dataset
(`11b_` and `11_`) rather than being quietly reconciled. An undocumented
constant table cannot be checked against anything, which is exactly the
failure the measured/model/derived labelling discipline exists to prevent.
""")

h3("10.2  Limits stated plainly")

md("""
1. **Absolute cycle counts are not claimed.** `estimate_cycles` is a rank
   estimator. In the one task where model and measurement are directly
   comparable, the model says 309 cycles and the hardware measured 11,782 —
   a 38x under-prediction, because the estimator models compute while the
   measurement is dominated by the memory-delivery schedule. The framework
   uses it to **order** schedulers, never to predict a cycle count.
2. **Nine of the fourteen schedulers have no measured dispatch behaviour.**
   Only FIFO, LIFO, AI-MT, BATCH-DNN and BATCH-DNN++ have recorded golden
   runs; the other nine orders are model predictions from the transcribed RTL
   selectors. A standalone wrapper testbench would close this.
3. **MT/CT overlap is deliberately not modelled.** AI-MT's memory/compute
   overlap and BATCH-DNN's sub-batch pipelining are the designed benefit of
   those schedulers, but this integration serialises the two phases and the
   measured runs show no overlap gain. Modelling one would produce a number no
   measurement in this project supports.
4. **Power is a vectorless estimate** (Vivado Medium confidence). A SAIF from
   a simulation of the real workload would raise it to High and make it
   activity-dependent; that is scoped, not built.
5. **Fmax is post-synthesis.** Place-and-route will lower it.
6. **AI-MT's and BATCH-DNN's netlists have multi-driven registers** (Finding
   F3), so their measured area is honest but describes a netlist that does not
   faithfully implement the simulated design.
""")


# ===========================================================================
# SECTION 11 -- SUMMARY
# ===========================================================================
h2("11.  Summary of the contribution")

stat_row([
    (f"{N_SCHED}", "schedulers, one framework",
     "11 classical + AI-MT + BATCH-DNN + BATCH-DNN++"),
    (f"{N_MEASURED}/{N_SCHED}", "with real silicon numbers",
     "up from 11/14 — two RTL fixes"),
    ("32/32", "chooser decisions verified",
     "against exhaustive re-scoring"),
    ("5/5", "dispatch orders match RTL",
     "plus makespan flatness PASS"),
    (f"{vals[0]*1e3:.1f} ms", "to rank all 14",
     f"vs ~{vals[3]:,.0f} s per synthesis"),
    ("4", "findings raised",
     "2 fixed, 2 disclosed with evidence"),
])

md(f"""
**What did not exist before this work.** A single accelerator on which a
classical scheduler and a DNN-aware scheduler can be compared under identical
hardware conditions, with the same metrics, and with the comparison anchored
to measured silicon.

**What the framework produces that a conventional study cannot.**

1. *The cycle ranking of multi-DNN schedulers inverts once the measured clock
   is applied* — SJF is 1st in cycles and {_sjf_u}th in wall-clock time on
   mix 3. Cycle-only scheduler comparisons give the wrong recommendation.
2. *Makespan cannot discriminate schedulers on this accelerator* — proved from
   the machine model and confirmed in hardware to within one cycle. The
   metrics that do move are turnaround, wait and the scheduler's own hardware
   cost.
3. *Three of the fourteen schedulers were simulation-only RTL* — correct in
   simulation, unbuildable in hardware. Two are now fixed and measured.
4. *The project-wide 1.0 GHz clock assumption is
   {fmaxgap['optimism_factor'].min():.0f}x–{fmaxgap['optimism_factor'].max():.0f}x
   optimistic*, which bounds every throughput figure in the repository.

**The selection framework itself** ranks all {N_SCHED} schedulers for any
workload mix and any of 8 objectives in {vals[0]*1e3:.1f} ms, excludes rather
than fabricates when a measured value is missing, and names the best
buildable alternative whenever the winner cannot be synthesised.
""")

md(f"""
---
*Figures written to* `{FIGS}` *(PNG, 200 dpi) — ready to drop into slides.*
*Data read from* `{DATA}`.
""")
