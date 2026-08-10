"""Render the 14 multi-DNN scheduling algorithms as one reference figure.

    PYTHONPATH=. python scripts/gen_scheduler_algorithm_map.py

Writes docs/figures/multi_dnn_scheduler_algorithms.{png,pdf} on a white
background.  Every fact on the card faces is transcribed from, in order:

  rtl/schedulers/unified_scheduler_wrapper.sv   the 5-bit select encoding
  rtl/schedulers/{task,advanced_task}_scheduler.sv, aimt/batchdnn*.sv
                                                the selection rules
  pysim/scheduler_chooser.py                    NON_PREEMPTIVE, NUM_QUEUES
  results/sched_chooser/hw/scheduler_hw.csv     measured LUTs and Fmax

The numbers are pasted rather than read from the CSV on purpose: this is a
reference plate for the write-up, so it should not silently change when the
hardware table is re-synthesised.  Re-run it deliberately after a synthesis
refresh.
"""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

WHITE = "#ffffff"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
HAIR = "#e1e0d9"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
CARD = "#fbfbfa"

mpl.rcParams.update({
    "font.family": "sans-serif", "figure.facecolor": WHITE,
    "savefig.facecolor": WHITE, "axes.facecolor": WHITE,
})

# (name, select, rule lines, tag, hw, citation)
BASIC = [
    ("FIFO",  0, ["first task in the queue"], "non-preemptive", "1,501 LUT · 106.6 MHz", ""),
    ("LIFO",  1, ["most recently enqueued task"], "non-preemptive", "1,516 LUT · 111.1 MHz", ""),
    ("SJF",   2, ["min declared burst_time"], "non-preemptive", "1,999 LUT · 20.3 MHz", ""),
    ("RR",    3, ["round-robin pointer,", "wraps past the end"], "preemptive selector", "1,594 LUT · 93.4 MHz", ""),
    ("PRI",   4, ["max declared priority"], "non-preemptive", "1,663 LUT · 41.7 MHz", ""),
    ("EDF",   5, ["min declared deadline"], "non-preemptive", "2,374 LUT · 19.0 MHz", ""),
    ("LRU",   6, ["min last-access time"], "preemptive selector", "3,035 LUT · 19.2 MHz", ""),
]
ADVANCED = [
    ("SRTF",  7, ["min remaining time"], "preemptive selector", "1,854 LUT · 21.1 MHz", ""),
    ("HRRN",  8, ["max (wait + burst) / burst,", "by integer cross-multiply"], "", "2,941 LUT · 6.5 MHz", ""),
    ("MLQ",   9, ["scans levels high→low; levels", "never change ⇒ acts as FIFO"], "", "755 LUT · 112.4 MHz", ""),
    ("MLFQ", 10, ["scans levels low→high; demote", "on dispatch, promote at wait>100"], "preemptive selector", "2,295 LUT · 90.9 MHz", ""),
]
DNN = [
    ("AI-MT", 11, ["layer-granularity memory/compute overlap;",
                   "walks the scheduling table gated by the",
                   "MT/CT balance condition"],
     "", "3,417 LUT · 86.7 MHz", "Baek et al., ISCA 2020"),
    ("BATCH-DNN", 12, ["the AI-MT memory path, plus sub-batch",
                       "splitting and merging on a per-DNN",
                       "LIFO stack when memory is tight"],
     "", "4,657 LUT · 10.7 MHz", "Ranawaka & Stenström, EuroPar 2025"),
    ("BATCH-DNN++", 13, ["adds distance-based MT throttling (≤5",
                         "layers), bottleneck-layer expedition,",
                         "dependency-aware compute dispatch"],
     "", "no current synthesis result", "Ranawaka & Stenström, 2025"),
]

# columns: (x-slot, algos, card height, group colour)
COLS = [
    (0, BASIC[:4], 1.34, BLUE),
    (1, BASIC[4:], 1.34, BLUE),
    (2, ADVANCED, 1.34, ORANGE),
    (3, DNN, 1.86, AQUA),
]
# group headers: (first col, span, name, subtitle, colour)
HEADERS = [
    (0, 2, "Basic", "task_scheduler.sv   ·   select 0–6   ·   one FIFO task queue, "
                    "selection applied at dispatch", BLUE),
    (2, 1, "Advanced", "advanced_task_scheduler.sv   ·   select 7–10   ·   4 queue levels", ORANGE),
    (3, 1, "DNN-aware", "own modules   ·   select 11–13   ·   scheduling table + MT/CT split", AQUA),
]

COL_W, GAP = 4.55, 0.30
CARD_GAP = 0.17
HEAD_H = 1.00
MARGIN = 0.5
TITLE_H = 1.60
STRIP_H = 2.30
FIG_W = 4 * COL_W + 3 * GAP + 2 * MARGIN
BODY_H = HEAD_H + 0.26 + max(len(a) * (h + CARD_GAP) for _, a, h, _ in COLS)
FIG_H = TITLE_H + BODY_H + STRIP_H

fig = plt.figure(figsize=(FIG_W, FIG_H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")


def colx(i):
    return MARGIN + i * (COL_W + GAP)


# ------------------------------------------------------------------ title --
ax.text(MARGIN, FIG_H - 0.52,
        "Multi-DNN scheduler — the 14 scheduling algorithms",
        fontsize=22, color=INK, va="top", fontweight="bold")
ax.text(MARGIN, FIG_H - 1.06,
        "Every policy is implemented in RTL and picked by the 5-bit "
        "scheduler_select of unified_scheduler_wrapper.sv.   "
        "Area and Fmax are measured — Vivado 2025.2 out-of-context "
        "synthesis, xc7a100tcsg324-1.",
        fontsize=11, color=INK2, va="top")

y_top = FIG_H - TITLE_H

# --------------------------------------------------------------- headers ---
for first, span, name, sub, col in HEADERS:
    x = colx(first)
    w = span * COL_W + (span - 1) * GAP
    ax.add_patch(FancyBboxPatch((x, y_top - HEAD_H), w, HEAD_H,
                                boxstyle="round,pad=0,rounding_size=0.09",
                                facecolor=col, edgecolor="none"))
    n_alg = sum(len(a) for c, a, _, _ in COLS if first <= c < first + span)
    ax.text(x + 0.26, y_top - 0.34, name, fontsize=14.5, color=WHITE,
            fontweight="bold", va="center")
    ax.text(x + w - 0.26, y_top - 0.34, f"{n_alg} policies", fontsize=10,
            color=WHITE, va="center", ha="right", alpha=0.94)
    ax.text(x + 0.26, y_top - 0.72, sub, fontsize=8.6, color=WHITE,
            va="center", alpha=0.94)

# ----------------------------------------------------------------- cards ---
for ci, algos, card_h, col in COLS:
    x = colx(ci)
    yc = y_top - HEAD_H - 0.26
    for name, sel, rule, tag, hw, cite in algos:
        yc -= card_h
        ax.add_patch(FancyBboxPatch((x, yc), COL_W, card_h,
                                    boxstyle="round,pad=0,rounding_size=0.07",
                                    facecolor=CARD, edgecolor=HAIR,
                                    linewidth=0.9))
        ax.add_patch(Rectangle((x, yc + 0.07), 0.055, card_h - 0.14,
                               facecolor=col, edgecolor="none"))

        ax.text(x + 0.26, yc + card_h - 0.29, name, fontsize=12.5,
                color=INK, fontweight="bold", va="center")
        ax.text(x + COL_W - 0.24, yc + card_h - 0.29, f"sel {sel}",
                fontsize=8.6, color=MUTED, va="center", ha="right",
                bbox=dict(boxstyle="round,pad=0.32", facecolor=WHITE,
                          edgecolor=HAIR, linewidth=0.9))

        ry = yc + card_h - 0.60
        for line in rule:
            ax.text(x + 0.26, ry, line, fontsize=9.2, color=INK2, va="center")
            ry -= 0.245
        if cite:
            ax.text(x + 0.26, ry - 0.02, cite, fontsize=8.4, color=MUTED,
                    va="center", style="italic")

        foot = f"{tag}  ·  {hw}" if tag else hw
        ax.text(x + 0.26, yc + 0.19, foot, fontsize=8.6, color=MUTED,
                va="center")

# --------------------------------------------------------- wrapper strip ---
sy = 0.92
ax.add_patch(FancyBboxPatch((MARGIN, sy), FIG_W - 2 * MARGIN, 1.05,
                            boxstyle="round,pad=0,rounding_size=0.09",
                            facecolor="#f5f5f2", edgecolor=HAIR, linewidth=0.9))
ax.text(MARGIN + 0.3, sy + 0.75, "How they are wired", fontsize=11, color=INK,
        fontweight="bold", va="center")

parts = [("unified_scheduler_wrapper.sv", INK2, True), ("   →   ", MUTED, False),
         ("multi_scheduler_wrapper.sv", BLUE, True),
         (" (Basic + Advanced — one FIFO queue)", INK2, False),
         ("      or      ", MUTED, False),
         ("dnn_scheduler_wrapper.sv", AQUA, True),
         (" (DNN-aware — scheduling-table load, separate MT/CT outputs)", INK2, False)]
tx = MARGIN + 0.3
fig.canvas.draw()
rend = fig.canvas.get_renderer()
for txt, col, mono in parts:
    t = ax.text(tx, sy + 0.32, txt, fontsize=9.8, color=col, va="center",
                family="monospace" if mono else "sans-serif")
    tx += t.get_window_extent(renderer=rend).width / fig.dpi

ax.text(MARGIN, 0.55,
        "The two families have incompatible interfaces: Basic and Advanced "
        "consume a FIFO task queue, DNN-aware consume a scheduling-table load "
        "and emit separate memory-task and compute-task outputs.",
        fontsize=9, color=MUTED, va="center")
ax.text(MARGIN, 0.26,
        "RR, LRU, SRTF and MLFQ re-decide every cycle in RTL, but the dispatch "
        "FSM of multi_dnn_top is single-issue run-to-completion, so preemption "
        "cannot manifest in this integration.   "
        "BATCH-DNN++ has no current synthesis result — see "
        "results/sched_chooser/hw/scheduler_hw.csv.",
        fontsize=9, color=MUTED, va="center")

ROOT = Path(__file__).resolve().parent.parent
out = ROOT / "docs/figures/multi_dnn_scheduler_algorithms.png"
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=200, facecolor=WHITE)
fig.savefig(out.with_suffix(".pdf"), facecolor=WHITE)
print("wrote", out, f"{FIG_W:.1f} x {FIG_H:.1f} in")
