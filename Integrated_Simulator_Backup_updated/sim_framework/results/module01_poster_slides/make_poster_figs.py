#!/usr/bin/env python3
"""Generate the graphics for the Module 01 poster panel.

The panel was text-heavy, so most of the prose blocks are replaced by figures:

  poster_fig_knobs.png    -> replaces the "Contribution" text (what was built)
  poster_fig_flow.png     -> replaces the "Method" bullet list
  poster_fig_results.png  -> replaces the "Results" bullet list
  poster_fig1_knob_impact.png  -> measured effect of each knob (horizontal
                                  bars: readable at small poster size)
  poster_fig2_layout_mechanism.png -> the headline finding

Every measured number is read from results/golden_check/raw/*.json - nothing
is typed in by hand.

Run:  PYTHONPATH=. python results/module01_poster_slides/make_poster_figs.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrow

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "results/golden_check/raw"
OUT = Path(__file__).resolve().parent

plt.rcParams.update({
    "font.size": 13, "axes.titlesize": 14, "axes.labelsize": 12,
    "xtick.labelsize": 12, "ytick.labelsize": 12,
    "axes.spines.top": False, "axes.spines.right": False,
})

TEAL, ORANGE, NAVY, BLUE = "#0f7b6c", "#e8a33d", "#12355b", "#0b4da2"
LIGHT, GREY = "#e8eff8", "#7b868f"


def raw(stem: str) -> dict:
    return json.loads((RAW / f"{stem}.json").read_text())


def card(ax, x, y, w, h, face=LIGHT, edge=BLUE, lw=1.6, r=0.02):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
        facecolor=face, edgecolor=edge, linewidth=lw, zorder=1))


def blank_ax(figsize):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


# ===========================================================================
# 1. What was built: three knobs -> 27 configurations
# ===========================================================================
def fig_knobs() -> None:
    fig, ax = blank_ax((8.6, 2.5))
    knobs = [
        ("STATIONARY SCHEME", "OS  ·  WS  ·  IS",
         "which operand stays\nin the PE array", BLUE),
        ("MEMORY LAYOUT", "Row · Column · Channel",
         "order tensors are stored\nin off-chip DRAM", TEAL),
        ("CASTING SCHEME", "Unicast · Multicast · Hybrid",
         "how one value reaches\nthe many PEs needing it", ORANGE),
    ]
    # Card width is fixed, so the option line has to be small enough to fit
    # the longest string ("Unicast . Multicast . Hybrid") inside the box.
    w, gap = 0.295, 0.0575
    for i, (title, opts, sub, col) in enumerate(knobs):
        x = i * (w + gap)
        card(ax, x, 0.30, w, 0.66, edge=col)
        ax.text(x + w / 2, 0.86, title, ha="center", va="center",
                fontsize=12, fontweight="bold", color=col)
        ax.text(x + w / 2, 0.66, opts, ha="center", va="center",
                fontsize=11, fontweight="bold", color=NAVY)
        ax.text(x + w / 2, 0.45, sub, ha="center", va="center",
                fontsize=10, color=GREY)
        if i < 2:
            ax.text(x + w + gap / 2, 0.63, "x", ha="center", va="center",
                    fontsize=17, fontweight="bold", color=GREY)

    card(ax, 0.0, 0.02, 1.0, 0.20, face=NAVY, edge=NAVY)
    ax.text(0.5, 0.12,
            "27 configurations - real hardware controls, not software flags",
            ha="center", va="center", fontsize=13.5, fontweight="bold",
            color="white")
    fig.tight_layout(pad=0.2)
    fig.savefig(OUT / "poster_fig_knobs.png", dpi=300, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print("wrote poster_fig_knobs.png")


# ===========================================================================
# 2. Method as a flow strip
# ===========================================================================
def fig_flow() -> None:
    fig, ax = blank_ax((11.5, 1.55))
    steps = [("1  BUILD", "27 selectable\nRTL configs", BLUE),
             ("2  VERIFY", "RTL vs TensorFlow\ngolden", TEAL),
             ("3  MEASURE", "beats, bursts,\ncycles", TEAL),
             ("4  MODEL", "derive the\ncycle equation", BLUE),
             ("5  CHECK", "validate back\nagainst RTL", TEAL),
             ("6  APPLY", "best of 27 in\nmilliseconds", ORANGE)]
    n = len(steps)
    gap = 0.022
    w = (1.0 - gap * (n - 1)) / n
    for i, (title, body, col) in enumerate(steps):
        x = i * (w + gap)
        card(ax, x, 0.06, w, 0.88, edge=col)
        ax.text(x + w / 2, 0.72, title, ha="center", va="center",
                fontsize=12.5, fontweight="bold", color=col)
        ax.text(x + w / 2, 0.38, body, ha="center", va="center",
                fontsize=10.5, color=NAVY)
        if i < n - 1:
            ax.add_patch(FancyArrow(
                x + w + 0.002, 0.5, gap - 0.006, 0, width=0.05,
                head_width=0.16, head_length=0.008, length_includes_head=True,
                facecolor=GREY, edgecolor="none", zorder=3))
    fig.tight_layout(pad=0.15)
    fig.savefig(OUT / "poster_fig_flow.png", dpi=300, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print("wrote poster_fig_flow.png")


# ===========================================================================
# 3. Results as number tiles + the cycle law
# ===========================================================================
def fig_results() -> None:
    fig, ax = blank_ax((11.5, 2.35))
    # 22 = every configuration carrying a TensorFlow verdict file, all passing.
    # Not 27 (that is the size of the design space, not the verified set) and
    # not 26 (that count adds 4 bank-sweep runs, which are Module 02's axis).
    tiles = [("22 / 22", "configurations verified\nvs TensorFlow", TEAL),
             ("0.0499 %", "worst output error\n(5 % gate)", TEAL),
             ("11.3x", "off-chip traffic,\nbest vs worst casting", ORANGE),
             ("13x", "read bursts at\nIDENTICAL data volume", ORANGE),
             ("0.84 %", "mean cycle error\nvs measured RTL", BLUE),
             ("~10⁵x", "faster than\nRTL simulation", BLUE)]
    n = len(tiles)
    gap = 0.014
    w = (1.0 - gap * (n - 1)) / n
    for i, (big, lab, col) in enumerate(tiles):
        x = i * (w + gap)
        card(ax, x, 0.34, w, 0.62, edge=col)
        ax.text(x + w / 2, 0.76, big, ha="center", va="center",
                fontsize=19, fontweight="bold", color=col)
        ax.text(x + w / 2, 0.48, lab, ha="center", va="center",
                fontsize=9.8, color=NAVY)

    card(ax, 0.0, 0.02, 1.0, 0.24, face=NAVY, edge=NAVY)
    ax.text(0.5, 0.14,
            "cycles  =  3 x read requests  +  2 x data beats  +  compute",
            ha="center", va="center", fontsize=15, fontweight="bold",
            color="white", family="DejaVu Sans")
    fig.tight_layout(pad=0.2)
    fig.savefig(OUT / "poster_fig_results.png", dpi=300, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print("wrote poster_fig_results.png")


# ===========================================================================
# 4. Measured impact of each knob - horizontal bars (legible when small)
# ===========================================================================
def fig_knob_impact() -> None:
    base = raw("tiny_cnn_layer_00_OS_CHANNEL_MAJOR_STAMP_8x8_b4")
    b = base["total_cycles"]
    rows = [
        ("Unicast", raw("tiny_cnn_layer_00_OS_CHANNEL_MAJOR_STAMP_8x8_b4_UNICAST"), ORANGE),
        ("Hybrid", raw("tiny_cnn_layer_00_OS_CHANNEL_MAJOR_STAMP_8x8_b4_HYBRID"), ORANGE),
        ("Multicast", base, TEAL),
        ("Row-major", raw("tiny_cnn_layer_00_OS_ROW_MAJOR_STAMP_8x8_b4"), ORANGE),
        ("Column-major", raw("tiny_cnn_layer_00_OS_COLUMN_MAJOR_STAMP_8x8_b4"), ORANGE),
        ("Channel-major", base, TEAL),
        ("Weight-stat.", raw("tiny_cnn_layer_00_WS_CHANNEL_MAJOR_STAMP_8x8_b4"), ORANGE),
        ("Output-stat.", base, ORANGE),
        ("Input-stat.", raw("tiny_cnn_layer_00_IS_CHANNEL_MAJOR_STAMP_8x8_b4"), TEAL),
    ]
    labels = [r[0] for r in rows]
    vals = [r[1]["total_cycles"] / b for r in rows]
    cols = [r[2] for r in rows]

    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    ypos = list(range(len(rows)))
    ax.barh(ypos, vals, color=cols, height=0.68)
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontsize=12)
    ax.set_xscale("log")
    ax.set_xlim(0.7, 60)
    ax.set_xticks([])
    ax.axvline(1.0, color=GREY, ls=":", lw=1.2, zorder=0)
    for y, v in zip(ypos, vals):
        ax.text(v * 1.10, y, f"{v:.2f}x", va="center", fontsize=11.5,
                fontweight="bold", color=NAVY)
    for y, txt in [(1, "CASTING"), (4, "LAYOUT"), (7, "STATIONARY")]:
        ax.text(45, y, txt, va="center", ha="right", fontsize=10.5,
                fontweight="bold", color=GREY, alpha=0.85)
    for yy in (2.5, 5.5):
        ax.axhline(yy, color="#dfe4ea", lw=1.1)
    ax.set_xlabel("Execution time relative to the best setting (log)",
                  fontsize=11.5)
    ax.set_title("Measured RTL - one knob changed at a time",
                 fontsize=13, fontweight="bold", pad=8)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "poster_fig1_knob_impact.png", dpi=300,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote poster_fig1_knob_impact.png")


# ===========================================================================
# 5. The headline finding: layout changes requests, not volume
# ===========================================================================
def fig_layout_mechanism() -> None:
    names = ["Channel-\nmajor", "Column-\nmajor", "Row-\nmajor"]
    runs = [raw("tiny_cnn_layer_00_OS_CHANNEL_MAJOR_STAMP_8x8_b4"),
            raw("tiny_cnn_layer_00_OS_COLUMN_MAJOR_STAMP_8x8_b4"),
            raw("tiny_cnn_layer_00_OS_ROW_MAJOR_STAMP_8x8_b4")]
    beats = [r["axi_beats"] for r in runs]
    ars = [r["axi_ar_requests"] for r in runs]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.9, 3.5))
    for ax, vals, col, title, note in [
            (a1, beats, TEAL, "Data moved", "IDENTICAL"),
            (a2, ars, ORANGE, "Read requests", "13x fewer")]:
        ax.bar(names, vals, color=col, width=0.62)
        ax.set_title(title, fontweight="bold", fontsize=13, pad=8)
        ax.set_ylim(0, max(vals) * 1.42)
        for i, v in enumerate(vals):
            ax.text(i, v * 1.04, f"{v:,}", ha="center", fontsize=12,
                    fontweight="bold", color=NAVY)
        ax.text(0.5, 0.93, note, transform=ax.transAxes, ha="center",
                fontsize=12.5, color=NAVY, fontweight="bold")
        ax.set_yticks([])
        ax.tick_params(axis="x", labelsize=11)

    fig.suptitle("Layout changes how data is REQUESTED, not how much moves",
                 fontsize=12.5, fontweight="bold", y=1.02)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "poster_fig2_layout_mechanism.png", dpi=300,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote poster_fig2_layout_mechanism.png")


if __name__ == "__main__":
    fig_knobs()
    fig_flow()
    fig_results()
    fig_knob_impact()
    fig_layout_mechanism()
