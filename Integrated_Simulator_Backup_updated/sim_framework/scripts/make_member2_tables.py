#!/usr/bin/env python3
"""
make_member2_tables.py
======================
Build the Member-2 (on-chip memory management) result tables from the
recorded RTL runs, for the thesis notebook and the write-up.

Member 2's contribution has three claims, and this script produces one
table per claim plus a validation table:

  1. bank_conflict_law.csv
        The scratchpad's bank arbitration is fully predicted by a closed
        form derived from the RTL: with interleaved mapping and
        lowest-port-wins priority, the ports served in a cycle equal the
        number of DISTINCT banks the concurrent addresses touch.  Checked
        against the 4-pattern x 4-bank-count microbenchmark sweep.

  2. bank_scaling.csv
        The same arbitration measured under real workload traffic, so the
        microbenchmark law can be tied to an actual layer.  Also records
        which counters do NOT move with bank count -- an invariance that
        matters for how the result should be read.

  3. scheme_comparison.csv
        STAMP (static tagless) vs PAGED (dynamic page table) on the same
        hardware, same layer, same bank count: off-chip traffic, on-chip
        stalls, control overhead and numerical result.

  4. hw_cost.csv
        Measured Vivado area/power/Fmax, if scripts/synth_memory_hw.py has
        been run.  Skipped with a notice if not -- never estimated.

Every number is a hardware counter read out of results/golden_check/raw,
or a value derived from those counters by an arithmetic stated in the
`How it was obtained` column.  Nothing is fitted or interpolated.

Usage (from sim_framework/):
    PYTHONPATH=. python scripts/make_member2_tables.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "results/golden_check/raw"
OUT = ROOT / "results/member2"
BUNDLE = ROOT / "results/thesis_notebook/data_bundle/member2"
HW_CSV = ROOT / "results/member2/hw/memory_hw.csv"

# AXI data bus is 64 bits wide (rtl/tops/single_dnn_top.sv AXI_DATA_WIDTH),
# so one beat carries 8 bytes.  Used only to express beats in bytes; the
# beat counts themselves are the direct hardware counters.
BYTES_PER_BEAT = 8

N_PORTS = 4          # scratchpad_ram N_PORTS in these builds
WINDOW = 200         # microbenchmark window, cycles

# Address patterns driven by tb/golden/test_bank_sweep.py, port 0..3.
PATTERNS = {
    "same_addr":   [0, 0, 0, 0],
    "consecutive": [0, 1, 2, 3],
    "stride4":     [0, 4, 8, 12],
    "stride8":     [0, 8, 16, 24],
}
PATTERN_LABEL = {
    "same_addr":   "All ports -> same address",
    "consecutive": "Ports -> addresses 0,1,2,3",
    "stride4":     "Ports -> addresses 0,4,8,12 (stride 4)",
    "stride8":     "Ports -> addresses 0,8,16,24 (stride 8)",
}


def _load(name: str) -> dict:
    """Read a raw result file, dropping the bulky output tensor."""
    d = json.loads((RAW / name).read_text())
    d.pop("out_fixed", None)
    return d


# ---------------------------------------------------------------------------
# 1. The bank-conflict law
# ---------------------------------------------------------------------------

def predict_served(addrs: list[int], banks: int) -> int:
    """Ports granted per cycle = number of distinct banks touched.

    Derived from rtl/memory/scratchpad_ram.sv, not fitted:
      * bank id = rd_addr[SEL_W-1:0], i.e. addr mod NUM_BANKS (interleaved),
      * on collision the lowest-indexed port wins and the others get
        rd_valid=0 that cycle.
    So exactly one port per distinct bank is served each cycle.
    """
    return len({a % banks for a in addrs})


def build_bank_conflict_law() -> pd.DataFrame:
    rows = []
    for path in sorted(RAW.glob("bank_sweep_b*.json"),
                       key=lambda p: int(p.stem.split("_b")[-1])):
        d = json.loads(path.read_text())
        banks = d["num_banks_build"]
        for pat, addrs in PATTERNS.items():
            m = d["patterns"][pat]
            if banks == 1:
                # The RTL's NUM_BANKS==1 path is a flat single store with no
                # arbitration and no conflict counters at all (documented in
                # the scratchpad_ram header).  It is the no-banking baseline,
                # so the arbitration law simply does not apply to it.
                pred_served = pred_stall = None
                applies = "n/a -- flat mode, no arbitration"
            else:
                distinct = predict_served(addrs, banks)
                # One read completes per granted port per cycle; the first
                # cycle of the window is absorbed by the RAM's 1-cycle read
                # latency, hence WINDOW-1 productive cycles.
                pred_served = distinct * (WINDOW - 1)
                pred_stall = (N_PORTS - distinct) * WINDOW
                applies = "yes"
            rows.append({
                "Number of banks (count)": banks,
                "Access pattern": PATTERN_LABEL[pat],
                "Distinct banks touched (count)":
                    None if banks == 1 else predict_served(addrs, banks),
                "Reads served, measured (count)": m["reads_served"],
                "Reads served, predicted (count)": pred_served,
                "Stalled port-cycles, measured (cycles)":
                    m["stall_port_cycles"],
                "Stalled port-cycles, predicted (cycles)": pred_stall,
                "Model applies": applies,
                "Prediction exact":
                    "" if pred_served is None else
                    ("yes" if (pred_served == m["reads_served"]
                               and pred_stall == m["stall_port_cycles"])
                     else "NO"),
                "Source": "measured (RTL counters) + closed form from "
                          "rtl/memory/scratchpad_ram.sv",
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. Bank scaling under real workload traffic
# ---------------------------------------------------------------------------

def build_bank_scaling() -> pd.DataFrame:
    rows = []
    for path in sorted(RAW.glob("divergence_tiny_cnn_layer_00_STAMP_b*.json"),
                       key=lambda p: int(p.stem.split("_b")[-1])):
        d = _load(path.name)
        t = d["totals"]
        rows.append({
            "Number of banks (count)": d["num_banks_build"],
            "Bank conflicts (events)": d["stats_bank_conflicts"],
            "Stall (port-cycles)": d["stats_bank_conflict_stall_cycles"],
            "Compute (cycles)": t["compute_cycles"],
            "Off-chip traffic (AXI beats)": d["axi_beats"],
            "Off-chip requests (AXI bursts)": d["axi_ar_requests"],
            "Scratchpad reads replayed (count)": t["replay_served"],
            "Max relative error vs golden (%)":
                round(d["verdict"]["max_rel_err_pct"], 6),
            "Source": "measured (RTL counters)",
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 3. STAMP vs PAGED, same hardware and same layer
# ---------------------------------------------------------------------------

# (row label, unit, extractor, which direction is better)
_METRICS = [
    ("Off-chip traffic", "AXI beats",
     lambda d: d["axi_beats"], "lower"),
    ("Off-chip traffic", "bytes",
     lambda d: d["axi_beats"] * BYTES_PER_BEAT, "lower"),
    ("Off-chip requests", "AXI read bursts",
     lambda d: d["axi_ar_requests"], "lower"),
    ("Compute time", "cycles",
     lambda d: d["totals"]["compute_cycles"], "lower"),
    ("Control/setup overhead", "cycles",
     lambda d: d["totals"]["program_cycles"], "lower"),
    ("Bank conflicts", "events",
     lambda d: d["stats_bank_conflicts"], "lower"),
    ("Bank-conflict stalls", "port-cycles",
     lambda d: d["stats_bank_conflict_stall_cycles"], "lower"),
    ("Runtime lookup misses", "events",
     lambda d: d["stats_moves_or_misses"], "lower"),
    ("Numerical error vs golden", "% of full scale",
     lambda d: round(d["verdict"]["max_rel_err_pct"], 6), "equal"),
]

_WORKLOADS = [("tiny_cnn", "tiny_cnn L0"), ("mnist_cnn", "mnist_cnn L0")]


def build_scheme_comparison() -> pd.DataFrame:
    rows = []
    for key, label in _WORKLOADS:
        s = _load(f"divergence_{key}_layer_00_STAMP_b4.json")
        p = _load(f"divergence_{key}_layer_00_PAGED_b4.json")
        for metric, unit, fn, better in _METRICS:
            sv, pv = fn(s), fn(p)
            if better == "equal":
                delta, verdict = "", ("identical" if sv == pv
                                      else "DIFFER -- investigate")
            elif pv == 0 and sv == 0:
                delta, verdict = "0", "tie"
            elif pv == 0:
                delta, verdict = "n/a (PAGED = 0)", "PAGED"
            else:
                pct = (sv - pv) / pv * 100.0
                delta = f"{pct:+.1f}"
                verdict = ("tie" if sv == pv else
                           "STAMP" if (sv < pv) == (better == "lower")
                           else "PAGED")
            rows.append({
                "Workload / layer": label,
                "Metric": metric,
                "Unit": unit,
                "STAMP (static tagless)": sv,
                "PAGED (dynamic page table)": pv,
                "STAMP vs PAGED (%)": delta,
                "Better scheme": verdict,
                "Source": "measured (RTL counters)",
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 4. Measured hardware cost (optional -- only if synthesis has been run)
# ---------------------------------------------------------------------------

def build_hw_cost() -> pd.DataFrame | None:
    if not HW_CSV.exists():
        return None
    hw = pd.read_csv(HW_CSV)
    keep = {"target": "Target", "label": "What was synthesised",
            "family": "Group", "status": "Synthesis status",
            "luts": "LUTs (count)", "ffs": "Flip-flops (count)",
            "brams": "Block RAM tiles (count)", "dsps": "DSPs (count)",
            "fmax_mhz_post_synth": "Fmax, post-synthesis (MHz)",
            "power_total_w": "Total on-chip power (W)",
            "power_dynamic_w": "Dynamic power (W)",
            "power_static_w": "Device static power (W)",
            "power_confidence": "Vivado power confidence",
            "note": "Note", "source": "Source"}
    out = hw[[c for c in keep if c in hw.columns]].rename(columns=keep)
    return out


def main() -> None:
    tables = {
        "bank_conflict_law.csv": build_bank_conflict_law(),
        "bank_scaling.csv": build_bank_scaling(),
        "scheme_comparison.csv": build_scheme_comparison(),
    }

    law = tables["bank_conflict_law.csv"]
    checked = law[law["Prediction exact"] != ""]
    n_ok = (checked["Prediction exact"] == "yes").sum()
    print(f"Bank-conflict law: {n_ok}/{len(checked)} banked configurations "
          f"predicted exactly")
    if n_ok != len(checked):
        print("  WARNING: the closed form does not reproduce every measured "
              "cell -- do not present it as exact.")

    scale = tables["bank_scaling.csv"]
    print(f"\nBank scaling (STAMP, tiny_cnn L0): "
          f"{len(scale)} bank counts measured")
    for col in ("Compute (cycles)", "Off-chip traffic (AXI beats)",
                "Off-chip requests (AXI bursts)"):
        n = scale[col].nunique()
        print(f"  {col:<34} {n} distinct value(s) across all bank counts"
              + ("  <- invariant" if n == 1 else ""))

    cmp_ = tables["scheme_comparison.csv"]
    print(f"\nScheme comparison: {len(cmp_)} measured metric rows "
          f"over {cmp_['Workload / layer'].nunique()} workloads")
    wins = cmp_[cmp_["Better scheme"].isin(["STAMP", "PAGED"])]
    print(f"  STAMP better on {(wins['Better scheme']=='STAMP').sum()} rows, "
          f"PAGED better on {(wins['Better scheme']=='PAGED').sum()} rows")

    hw = build_hw_cost()
    if hw is None:
        print(f"\nHardware cost: SKIPPED -- {HW_CSV.relative_to(ROOT)} not "
              f"found.\n  Run: python scripts/synth_memory_hw.py")
    else:
        tables["hw_cost.csv"] = hw
        ok = (hw["Synthesis status"] == "ok").sum()
        print(f"\nHardware cost: {ok}/{len(hw)} targets synthesised "
              f"(measured, Vivado)")

    for target in (OUT, BUNDLE):
        target.mkdir(parents=True, exist_ok=True)
        for fname, df in tables.items():
            df.to_csv(target / fname, index=False)
        try:
            shown = target.relative_to(ROOT)
        except ValueError:
            shown = target
        print(f"  wrote {len(tables)} tables to {shown}")


if __name__ == "__main__":
    main()
