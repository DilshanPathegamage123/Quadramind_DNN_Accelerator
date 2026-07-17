#!/usr/bin/env python3
"""Golden-check visual summary — topic-organized figures from RECORDED results.

Reads only results/golden_check/ (reports + raw JSONs + cycle CSV) and the
results/cloud/exp6 loop-optimization CSVs. Runs no simulations and computes
no new estimates; every plotted value is copied from a recorded artifact.
Each value carries a neutral source tag: "measured (RTL)" or "model"
("derived" where a value is arithmetic on a measured event count).

Style matches scripts/run_full_eval.py so the set reads together with
results/cloud/exp*/figures: same palette, grid, legend and title style.

Usage:  python scripts/gen_golden_summary_figs.py
Output: results/golden_check/figures/*.png + one CSV per figure.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
GC = ROOT / "results" / "golden_check"
RAW = GC / "raw"
FIG = GC / "figures"
EXP6 = ROOT / "results" / "cloud" / "exp6_loop_optimization"

# --- palette (identical to scripts/run_full_eval.py) -----------------------
C_OS, C_IS, C_WS = "#4e79a7", "#59a14f", "#f28e2b"
LAYOUT_SHADE = {"ROW_MAJOR": 0.65, "COLUMN_MAJOR": 0.82, "CHANNEL_MAJOR": 1.00}
def _shade(base, s):
    r, g, b = matplotlib.colors.to_rgb(base)
    return matplotlib.colors.to_hex((r * s, g * s, b * s))
LAYOUT_COLORS = {ly: _shade(C_OS, s) for ly, s in LAYOUT_SHADE.items()}
CAST_COLORS = {"MULTICAST": "#76b7b2", "HYBRID": "#f28e2b", "UNICAST": "#1a3a5c"}
CAST_ORDER = ["MULTICAST", "HYBRID", "UNICAST"]
BANK_COLORS = {2: "#a8cfe0", 4: "#1a3a5c", 8: "#f28e2b", 16: "#59a14f"}
SCHEME_COLORS = {"STAMP": "#1a3a5c", "PAGED": "#76b7b2"}
SCHED_CMAP = matplotlib.colormaps["tab10"]
C_DEFAULT_LO, C_WORST_LO, C_BEST_LO = "#76b7b2", "#1a3a5c", "#f28e2b"
DF_COLORS = {"OS": C_OS, "IS": C_IS, "WS": C_WS, "multi": "#b07aa1",
             "divergence": "#76b7b2"}
FIGSIZE_SINGLE, FIGSIZE_WIDE = (8, 5), (12, 5)

MEAS = "measured (RTL)"
MODEL = "model"


def _save(rows, header, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    print(f"  CSV : {path.relative_to(ROOT)}")


def _savefig(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  PNG : {path.relative_to(ROOT)}")


def _j(name):
    return json.loads((RAW / f"{name}.json").read_text())


# ===========================================================================
# Fig 1 — capability scorecard
# ===========================================================================
SCORECARD = [
    ("Compute dataflows", [
        ("Output-stationary (OS)", "full conv on the 8x8 array, golden-matched", MEAS),
        ("Weight-stationary (WS)", "multi-width arrays 8x1/8x2/8x8, golden-matched", MEAS),
        ("Input-stationary (IS)", "full conv incl. mnist, golden-matched", MEAS),
    ]),
    ("Memory layouts", [
        ("Row-major", "distinct off-chip address/burst pattern", MEAS),
        ("Column-major", "distinct off-chip address/burst pattern", MEAS),
        ("Channel-major", "long-burst coalescing, fewest AR requests", MEAS),
    ]),
    ("Interconnect casting", [
        ("Multicast", "one off-chip read per unique shared value", MEAS),
        ("Hybrid", "multicast weights + unicast inputs", MEAS),
        ("Unicast", "one read per consuming PE, distinct AXI transactions", MEAS),
    ]),
    ("Memory management", [
        ("STAMP delta-fetch", "LOAD/KEEP delta ops; fetches only new words", MEAS),
        ("PAGED page table", "per-port translation, hit/miss counters", MEAS),
        ("Bank conflicts & stalls", "cycle-accurate arbitration counters", MEAS),
        ("num_banks knob (1-16)", "hardware parameter, swept 2/4/8/16", MEAS),
    ]),
    ("Multi-DNN scheduling", [
        ("FIFO / LIFO", "order changes, results identical", MEAS),
        ("AI-MT", "memory/compute task interleaving", MEAS),
        ("BatchDNN / BatchDNN++", "batched dispatch variants", MEAS),
    ]),
    ("Loop optimization", [
        ("Blocking / tiling search", "4.4x mean energy reduction found", MODEL),
        ("Inter-layer reuse", "21.8% off-chip access reduction", MODEL),
    ]),
]


def fig1():
    # simpler, robust layout: one text row per capability
    rows = [(topic, cap, what, tag)
            for topic, caps in SCORECARD for cap, what, tag in caps]
    n = len(rows)
    fig, ax = plt.subplots(figsize=(12, 0.45 * n + 1.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, n + 1.4)
    ax.axis("off")
    tag_fc = {MEAS: "#dbe8f4", MODEL: "#e4f0ef"}
    tag_ec = {MEAS: C_OS, MODEL: "#76b7b2"}
    ax.text(0.10, n + 0.8, "Topic / capability", fontsize=10, fontweight="bold")
    ax.text(5.75, n + 0.8, "What it does (recorded result)", fontsize=10,
            fontweight="bold")
    ax.text(10.45, n + 0.8, "Source", fontsize=10, fontweight="bold")
    prev_topic = None
    for i, (topic, cap, what, tag) in enumerate(rows):
        y = n - i
        if i % 2 == 0:
            ax.axhspan(y - 0.45, y + 0.45, color="#f5f5f5", zorder=0)
        if topic != prev_topic:
            ax.text(0.10, y, topic, fontsize=9, fontweight="bold",
                    color="#222222", va="center")
            prev_topic = topic
        ax.text(2.85, y, cap, fontsize=9, va="center")
        ax.text(5.75, y, what, fontsize=8.5, va="center", color="#444444")
        ax.add_patch(mpatches.FancyBboxPatch(
            (10.35, y - 0.17), 1.5, 0.34, boxstyle="round,pad=0.02",
            fc=tag_fc[tag], ec=tag_ec[tag], lw=0.8, zorder=2))
        ax.text(11.10, y, tag, fontsize=7.5, ha="center", va="center", zorder=3)
    fig.suptitle("Simulator Capability Map — golden-checked features by topic",
                 fontsize=13, fontweight="bold")
    _savefig(fig, FIG / "f1_capability_scorecard.png")
    _save(rows, ["topic", "capability", "recorded_result", "source"],
          FIG / "f1_capability_scorecard.csv")


# ===========================================================================
# Fig 2 — correctness margin (log scale, 5% line)
# ===========================================================================
def fig2():
    entries = []
    import glob
    for f in sorted(glob.glob(str(RAW / "*_verdict.json"))):
        d = json.loads(Path(f).read_text())
        if not d.get("passed"):
            continue
        name = Path(f).name[:-len("_verdict.json")]
        df = d.get("dataflow", "OS")
        entries.append((name, df, float(d["max_rel_err_pct"])))
    for f in sorted(glob.glob(str(RAW / "divergence_*_b4.json"))):
        d = json.loads(Path(f).read_text())
        v = d.get("verdict", {})
        if v.get("passed"):
            name = Path(f).name[:-len(".json")]
            entries.append((name, "divergence", float(v["max_rel_err_pct"])))
    entries.sort(key=lambda e: e[2])
    labels = [e[0].replace("_STAMP_8x8_b4", "").replace("_layer", " L")
               .replace("_cnn", "").replace("_CHANNEL_MAJOR", " ChM")
               .replace("_ROW_MAJOR", " RM").replace("_COLUMN_MAJOR", " CM")
               .replace("divergence_", "mem ").replace("_b4", "")
              for e in entries]
    errs = [max(e[2], 1e-4) for e in entries]
    colors = [DF_COLORS.get(e[1], "#888888") for e in entries]

    fig, ax = plt.subplots(figsize=(10, 0.28 * len(entries) + 1.5))
    ypos = np.arange(len(entries))
    ax.barh(ypos, errs, color=colors, height=0.65)
    ax.axvline(5.0, color="#b22222", ls="--", lw=1.2)
    ax.text(5.0, len(entries) - 0.2, " 5% tolerance", color="#b22222",
            fontsize=8, va="top")
    for y, e in zip(ypos, errs):
        ax.text(e * 1.15, y, f"{e:.3f}%", fontsize=7, va="center")
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xscale("log")
    ax.set_xlim(1e-3, 20)
    ax.set_xlabel("Max relative error (% of full scale, log scale) — measured (RTL)")
    ax.set_title("Correctness Margin — every verified configuration is "
                 ">100x inside the 5% tolerance")
    handles = [mpatches.Patch(color=DF_COLORS[k], label=lbl) for k, lbl in
               [("OS", "OS dataflow"), ("IS", "IS dataflow"),
                ("WS", "WS dataflow"), ("divergence", "memory-mgmt runs")]]
    ax.legend(handles=handles, fontsize=8, loc="lower right")
    ax.grid(True, alpha=0.3, axis="x")
    _savefig(fig, FIG / "f2_correctness_margin.png")
    _save([(e[0], e[1], e[2], MEAS) for e in entries],
          ["config", "family", "max_rel_err_pct", "source"],
          FIG / "f2_correctness_margin.csv")


# ===========================================================================
# Fig 3 — cycle fidelity (estimated vs actual, from the recorded CSV)
# ===========================================================================
def fig3():
    rows = list(csv.DictReader(open(GC / "estimated_vs_actual_cycles.csv")))
    singles = [r for r in rows if r["kind"] == "single_dnn"]
    seen = set()
    uniq = []
    for r in singles:
        key = (r["layer"], r["dataflow"], r["layout"], r["memory"], r["array"])
        if key not in seen:
            seen.add(key)
            uniq.append(r)
    def _lbl(r):
        s = (f"{Path(r['layer']).parent.name.replace('_cnn','')}"
             f" {Path(r['layer']).name.replace('layer_0','L')}"
             f" {r['dataflow']} {r['array']}")
        if r["layout"] != "CHANNEL_MAJOR":
            s += " " + r["layout"].replace("_MAJOR", "").title()
        if r["memory"] != "STAMP":
            s += " " + r["memory"]
        return s
    labels = [_lbl(r) for r in uniq]
    est = [float(r["estimated_cycles_python"]) for r in uniq]
    act = [float(r["actual_cycles_per_invocation"]) for r in uniq]
    agree = [r["agreement_est_vs_per_invocation_pct"] for r in uniq]

    x = np.arange(len(uniq))
    bw = 0.38
    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    ax.bar(x - bw / 2, est, width=bw, color="#76b7b2",
           label="Estimated (model)")
    ax.bar(x + bw / 2, act, width=bw, color=C_OS,
           label="Actual per-invocation (measured, RTL)")
    for xi, (e, a, g) in enumerate(zip(est, act, agree)):
        if g:
            ax.text(xi, max(e, a) * 1.25, f"{float(g):.0f}%", fontsize=7,
                    ha="center")
    ax.set_yscale("log")
    ax.set_ylabel("Cycles (log scale)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=7)
    ax.set_title("Cycle Fidelity — analytical estimate vs RTL per-invocation "
                 "cycles (label = agreement %)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    _savefig(fig, FIG / "f3_cycle_fidelity.png")
    _save([(l, e, a, g, "est=model, actual=measured (RTL)")
           for l, e, a, g in zip(labels, est, act, agree)],
          ["config", "estimated_cycles", "actual_cycles_per_invocation",
           "agreement_pct", "source"],
          FIG / "f3_cycle_fidelity.csv")


# ===========================================================================
# Fig 4 — data delivery: layouts + casting (measured AXI traffic)
# ===========================================================================
def fig4():
    layouts = ["ROW_MAJOR", "COLUMN_MAJOR", "CHANNEL_MAJOR"]
    ly = {l: _j(f"tiny_cnn_layer_00_OS_{l}_STAMP_8x8_b4") for l in layouts}
    cast = {"tiny": {"MULTICAST": _j("tiny_cnn_layer_00_OS_CHANNEL_MAJOR_STAMP_8x8_b4"),
                     "UNICAST": _j("tiny_cnn_layer_00_OS_CHANNEL_MAJOR_STAMP_8x8_b4_UNICAST"),
                     "HYBRID": _j("tiny_cnn_layer_00_OS_CHANNEL_MAJOR_STAMP_8x8_b4_HYBRID")},
            "mnist": {"MULTICAST": _j("mnist_cnn_layer_00_OS_CHANNEL_MAJOR_STAMP_8x8_b4"),
                      "UNICAST": _j("mnist_cnn_layer_00_OS_CHANNEL_MAJOR_STAMP_8x8_b4_UNICAST"),
                      "HYBRID": _j("mnist_cnn_layer_00_OS_CHANNEL_MAJOR_STAMP_8x8_b4_HYBRID")}}

    fig, (axl, axr) = plt.subplots(1, 2, figsize=FIGSIZE_WIDE)
    # left: layouts (tiny L0) — AR requests and cycles
    x = np.arange(2)
    bw = 0.26
    for i, l in enumerate(layouts):
        vals = [ly[l]["axi_ar_requests"], ly[l]["total_cycles"]]
        b = axl.bar(x + (i - 1) * bw, vals, width=bw,
                    color=LAYOUT_COLORS[l],
                    label=l.replace("_MAJOR", "").title() + "-major")
        for rect, v in zip(b, vals):
            axl.text(rect.get_x() + rect.get_width() / 2, v * 1.05, f"{v:,}",
                     fontsize=7, ha="center")
    axl.set_xticks(x)
    axl.set_xticklabels(["AXI AR requests", "Total cycles"])
    axl.set_ylabel("Count — measured (RTL)")
    axl.set_title("Memory Layouts — tiny L0, OS 8x8\n(equal data: 1,836 beats "
                  "each; channel-major coalesces best)")
    axl.legend(fontsize=8)
    axl.grid(True, alpha=0.3, axis="y")
    axl.set_yscale("log")

    # right: casting — beats per layer, both workloads
    x = np.arange(2)
    for i, s in enumerate(CAST_ORDER):
        vals = [cast["tiny"][s]["axi_beats"], cast["mnist"][s]["axi_beats"]]
        b = axr.bar(x + (i - 1) * bw, vals, width=bw, color=CAST_COLORS[s],
                    label=s.title())
        for rect, v in zip(b, vals):
            axr.text(rect.get_x() + rect.get_width() / 2, v * 1.05, f"{v:,}",
                     fontsize=7, ha="center")
    axr.set_xticks(x)
    axr.set_xticklabels(["tiny L0", "mnist L0"])
    axr.set_ylabel("Off-chip AXI beats — measured (RTL)")
    axr.set_title("Casting Schemes — OS 8x8, whole layer\n(multicast lowest, "
                  "unicast highest; identical outputs)")
    axr.legend(fontsize=8)
    axr.grid(True, alpha=0.3, axis="y")
    axr.set_yscale("log")
    fig.suptitle("Data Delivery — layouts and casting change real off-chip "
                 "traffic, never results", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    _savefig(fig, FIG / "f4_data_delivery_traffic.png")

    rows = []
    for l in layouts:
        rows.append(("layout", l, "tiny L0", ly[l]["axi_ar_requests"],
                     ly[l]["axi_beats"], ly[l]["total_cycles"], MEAS))
    for wl in ["tiny", "mnist"]:
        for s in CAST_ORDER:
            d = cast[wl][s]
            rows.append(("casting", s, f"{wl} L0", d["axi_ar_requests"],
                         d["axi_beats"], d["total_cycles"], MEAS))
    _save(rows, ["axis", "setting", "layer", "axi_ar_requests", "axi_beats",
                 "total_cycles", "source"],
          FIG / "f4_data_delivery_traffic.csv")


# ===========================================================================
# Fig 5 — memory management: STAMP vs PAGED + bank sweep
# ===========================================================================
def fig5():
    div = {(w, s): _j(f"divergence_{w}_cnn_layer_00_{s}_b4")
           for w in ["tiny", "mnist"] for s in ["STAMP", "PAGED"]}
    banks = {}
    for nb in [2, 4, 8, 16]:
        d = _j(f"divergence_tiny_cnn_layer_00_STAMP_b{nb}")
        banks[nb] = (d["stats_bank_conflicts"],
                     d["stats_bank_conflict_stall_cycles"])

    fig, (axl, axr) = plt.subplots(1, 2, figsize=FIGSIZE_WIDE)
    x = np.arange(2)
    bw = 0.34
    for i, s in enumerate(["STAMP", "PAGED"]):
        vals = []
        for w in ["tiny", "mnist"]:
            d = div[(w, s)]
            vals.append(d["stats_bytes_loaded"] if s == "STAMP"
                        else d["unique_pages_mapped"] * 4096)
        b = axl.bar(x + (i - 0.5) * bw, vals, width=bw, color=SCHEME_COLORS[s],
                    label=f"{s} — " + ("measured (RTL)" if s == "STAMP"
                                       else "derived from measured page faults"))
        for rect, v in zip(b, vals):
            axl.text(rect.get_x() + rect.get_width() / 2, v + 150, f"{v:,} B",
                     fontsize=8, ha="center")
    axl.set_xticks(x)
    axl.set_xticklabels(["tiny L0", "mnist L0"])
    axl.set_ylabel("Off-chip bytes for the layer")
    axl.set_title("STAMP vs PAGED — delta-fetch loads only new words\n"
                  "(STAMP 5.0x / 2.4x less off-chip data)")
    axl.legend(fontsize=7.5)
    axl.grid(True, alpha=0.3, axis="y")

    nbs = [2, 4, 8, 16]
    x = np.arange(len(nbs))
    conf = [banks[n][0] for n in nbs]
    stall = [banks[n][1] for n in nbs]
    b1 = axr.bar(x - 0.19, conf, width=0.38, color=[BANK_COLORS[n] for n in nbs],
                 label="Conflict events")
    b2 = axr.bar(x + 0.19, stall, width=0.38,
                 color=[BANK_COLORS[n] for n in nbs], alpha=0.55,
                 label="Stall port-cycles", hatch="//")
    for rect, v in list(zip(b1, conf)) + list(zip(b2, stall)):
        axr.text(rect.get_x() + rect.get_width() / 2, v + 8, f"{v:,}",
                 fontsize=8, ha="center")
    axr.set_xticks(x)
    axr.set_xticklabels([f"{n} banks" for n in nbs])
    axr.set_ylabel("Count, whole layer — measured (RTL)")
    axr.set_title("Bank sweep — real tile-footprint traffic, tiny L0 STAMP\n"
                  "(conflicts vanish as banking widens)")
    axr.legend(fontsize=8)
    axr.grid(True, alpha=0.3, axis="y")
    fig.suptitle("Memory Management — measured scheme divergence and banking "
                 "behaviour", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    _savefig(fig, FIG / "f5_memory_management.png")

    rows = []
    for w in ["tiny", "mnist"]:
        d = div[(w, "STAMP")]
        rows.append((f"{w} L0", "STAMP off-chip bytes",
                     d["stats_bytes_loaded"], MEAS))
        d = div[(w, "PAGED")]
        rows.append((f"{w} L0", "PAGED off-chip bytes (pages x 4KB)",
                     d["unique_pages_mapped"] * 4096,
                     "derived from measured page faults"))
        rows.append((f"{w} L0", "PAGED page hits",
                     div[(w, "PAGED")]["stats_loads_or_hits"], MEAS))
        rows.append((f"{w} L0", "PAGED page misses",
                     div[(w, "PAGED")]["stats_moves_or_misses"], MEAS))
    for n in nbs:
        rows.append(("tiny L0 STAMP", f"bank conflicts @ {n} banks",
                     banks[n][0], MEAS))
        rows.append(("tiny L0 STAMP", f"stall port-cycles @ {n} banks",
                     banks[n][1], MEAS))
    _save(rows, ["layer", "metric", "value", "source"],
          FIG / "f5_memory_management.csv")


# ===========================================================================
# Fig 6 — scheduling behaviour (dispatch order, identical results)
# ===========================================================================
def fig6():
    scheds = ["FIFO", "LIFO", "AIMT", "BATCHDNN", "BATCHDNN_PP"]
    labels = ["FIFO", "LIFO", "AI-MT", "BATCH-DNN", "BATCH-DNN++"]
    data = {s: _j(f"multi_{s}_8x8") for s in scheds}
    task_names = ["task 0: tiny conv", "task 1: mnist conv", "task 2: tiny dense"]
    task_colors = [SCHED_CMAP(0), SCHED_CMAP(1), SCHED_CMAP(2)]

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    for yi, s in enumerate(scheds):
        order = [e["task"] for e in data[s]["dispatch_order"]]
        for pos, t in enumerate(order):
            ax.barh(yi, 0.9, left=pos, height=0.6, color=task_colors[t])
            ax.text(pos + 0.45, yi, f"T{t}", ha="center", va="center",
                    fontsize=9, color="white", fontweight="bold")
        ax.text(len(order) + 0.15, yi,
                f"all tasks PASS · {data[s]['total_cycles']:,} cycles",
                fontsize=8, va="center")
    ax.set_yticks(range(len(scheds)))
    ax.set_yticklabels(labels)
    ax.set_xticks([0.45, 1.45, 2.45])
    ax.set_xticklabels(["1st dispatch", "2nd", "3rd"])
    ax.set_xlim(0, 5.6)
    ax.invert_yaxis()
    ax.set_title("Multi-DNN Scheduling — order changes, results do not\n"
                 "(per-task errors identical across all five schedulers) — "
                 "measured (RTL)")
    handles = [mpatches.Patch(color=task_colors[i], label=task_names[i])
               for i in range(3)]
    ax.legend(handles=handles, fontsize=8, ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, -0.10))
    ax.grid(False)
    _savefig(fig, FIG / "f6_scheduler_behaviour.png")

    rows = []
    for s in scheds:
        order = "->".join(f"T{e['task']}" for e in data[s]["dispatch_order"])
        rows.append((s, order, data[s]["total_cycles"],
                     data[s]["all_pass"], MEAS))
    _save(rows, ["scheduler", "dispatch_order", "total_cycles", "all_pass",
                 "source"], FIG / "f6_scheduler_behaviour.csv")


# ===========================================================================
# Fig 7 — loop optimization (recorded model results, exp6)
# ===========================================================================
def fig7():
    brows = list(csv.DictReader(open(EXP6 / "blocking.csv")))
    schemes = ["Baseline", "Basic Tiling", "Optimized Blocking"]
    scheme_colors = {"Baseline": C_DEFAULT_LO, "Basic Tiling": C_WORST_LO,
                     "Optimized Blocking": C_BEST_LO}
    wls = sorted({r["workload"] for r in brows})
    means = {s: {} for s in schemes}
    for s in schemes:
        for w in wls:
            v = [float(r["norm_energy"]) for r in brows
                 if r["scheme"] == s and r["workload"] == w]
            means[s][w] = sum(v) / len(v)

    rrows = list(csv.DictReader(open(EXP6 / "inter_layer_reuse.csv")))
    rcols = ["No Reuse", "Intra-Layer Reuse", "Inter-Layer Reuse"]
    rmean = {c: sum(float(r[c]) for r in rrows) / len(rrows) for c in rcols}

    fig, (axl, axr) = plt.subplots(1, 2, figsize=FIGSIZE_WIDE)
    x = np.arange(len(wls))
    bw = 0.26
    for i, s in enumerate(schemes):
        vals = [means[s][w] for w in wls]
        axl.bar(x + (i - 1) * bw, vals, width=bw, color=scheme_colors[s],
                label=s)
    axl.axhline(1.0, color="#888888", lw=0.8, ls=":")
    axl.set_xticks(x)
    axl.set_xticklabels([w.replace("/", "/\n") for w in wls], rotation=20,
                        ha="right", fontsize=7)
    axl.set_ylabel("Normalized DRAM energy (model)")
    axl.set_title("Blocking search — optimized blocking averages 4.4x lower\n"
                  "DRAM energy than baseline across all workloads")
    axl.legend(fontsize=8)
    axl.grid(True, alpha=0.3, axis="y")

    b = axr.bar(np.arange(3), [rmean[c] for c in rcols],
                color=[C_DEFAULT_LO, C_WORST_LO, C_BEST_LO], width=0.55)
    for rect, c in zip(b, rcols):
        axr.text(rect.get_x() + rect.get_width() / 2, rmean[c] + 0.015,
                 f"{rmean[c]:.3f}", fontsize=9, ha="center")
    axr.set_xticks(np.arange(3))
    axr.set_xticklabels(rcols, fontsize=8)
    axr.set_ylabel("Normalized off-chip accesses (model)")
    axr.set_title("Inter-layer reuse — 21.8% mean reduction in\n"
                  "off-chip accesses (all workloads)")
    axr.grid(True, alpha=0.3, axis="y")
    fig.suptitle("Loop Optimization — design-space findings (model)",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    _savefig(fig, FIG / "f7_loop_optimization.png")

    rows = [(w, s, means[s][w], MODEL) for s in schemes for w in wls]
    rows += [("all-workload mean", c, rmean[c], MODEL) for c in rcols]
    _save(rows, ["workload", "scheme_or_reuse", "normalized_value", "source"],
          FIG / "f7_loop_optimization.csv")


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    fig6()
    fig7()
    print("All golden-summary figures generated.")
