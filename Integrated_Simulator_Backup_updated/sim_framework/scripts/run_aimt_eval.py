"""Multi-DNN scheduler evaluation on the dual-issue execution hardware.

Every number this script produces comes from a Verilator simulation of the
RTL in rtl/exec/ + rtl/schedulers/.  Nothing is interpolated and no scheduler
carries a hand-written speedup factor -- which is the whole point, since the
figures this replaces were driven by a hardcoded SCHEDULER_MODEL table in
run_full_eval.py.

EXPERIMENTS
-----------
  A  scheduler comparison per workload mix (batch 1)
  B  MT/CT timeline for the Gantt / utilisation figure
  C  speedup vs arithmetic intensity (DRAM bandwidth sweep)
  D  batch sweep -- where BATCH-DNN / BATCH-DNN++ separate from AI-MT
  E  on-chip capacity sweep (re-elaborates: capacity is a parameter)

FAIR BATCH ACCOUNTING -- read before interpreting Experiment D
--------------------------------------------------------------
A requested batch of B means B inferences must be completed, whatever the
scheduler.  The families differ in how they can pay for that:

  AI-MT and the basic schedulers have no batching mechanism, so they run B
  independent passes and RELOAD THE WEIGHTS EACH TIME:
        bytes = B * (weight + ifmap),  compute = B * compute
    -> encoded as footprints scaled by B with batch = 1.

  BATCH-DNN / BATCH-DNN++ batch the inferences and load weights ONCE:
        bytes = weight + B * ifmap,    compute = B * compute
    -> encoded as unscaled footprints with batch = B.

Both do identical compute; only weight traffic differs.  That asymmetry IS
the batching thesis, so the comparison neither flatters nor handicaps either
family -- it just lets each pay its real price.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.aimt_workload_gen import (build_table, mix_by_label,
                                       table_summary, write_table)
from scripts.workloads import SCHED_EVAL_MIXES

FW = Path(__file__).resolve().parent.parent
RESULTS = FW / "results" / "aimt_exec"
RAW = RESULTS / "raw"
WLDIR = RESULTS / "workloads"

# scheduler_select -> label.  Basic family runs the serial MT->CT channel;
# DNN-aware family runs the dual-issue channels.
# RR (select 3) is deliberately absent: on this machine it fails to retire
# every layer (10-11 of 12) because the legacy task_scheduler round-robin
# pointer can re-select an already-dispatched slot. That is a pre-existing
# defect in the basic family, unrelated to the MT/CT work here, and an
# incomplete run is not comparable -- so it is excluded rather than shown
# with a flattering short cycle count.
SCHEDULERS: Dict[int, str] = {
    0:  "FIFO",
    2:  "SJF",
    11: "AI-MT",
    12: "BATCH-DNN",
    13: "BATCH-DNN++",
}
DNN_AWARE = {11, 12, 13}
BATCHING = {12, 13}          # can amortise weights across a batch

DEFAULT_CAPACITY = 46137344  # 44 MiB (AI-MT paper, Table 1a)
DEFAULT_BAL = 1000


# ---------------------------------------------------------------------------
# Simulator invocation
# ---------------------------------------------------------------------------
def sim_binary(capacity: int = DEFAULT_CAPACITY,
               bal: int = DEFAULT_BAL) -> Path:
    return FW / "build" / f"exec_sim_{capacity}_{bal}" / "exec_sim"


def ensure_built(capacity: int = DEFAULT_CAPACITY,
                 bal: int = DEFAULT_BAL) -> Path:
    binary = sim_binary(capacity, bal)
    if not binary.exists():
        script = FW / "tb" / "exec" / "build_exec.sh"
        print(f"  building simulator (capacity={capacity}, bal={bal}) ...")
        subprocess.run([str(script), str(capacity), str(bal)],
                       check=True, capture_output=True, text=True)
    return binary


def run_sim(workload: Path, sched: int, out_json: Path,
            dram_bw: int = 64, dram_lat: int = 20, fill_drain: int = 16,
            capacity: int = DEFAULT_CAPACITY, bal: int = DEFAULT_BAL,
            timeout_cycles: int = 40_000_000) -> Optional[Dict]:
    binary = ensure_built(capacity, bal)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    cmd = [str(binary),
           f"+sched={sched}", f"+workload={workload}", f"+json={out_json}",
           f"+dram_bw={dram_bw}", f"+dram_lat={dram_lat}",
           f"+fill_drain={fill_drain}", f"+timeout={timeout_cycles}"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if not out_json.exists():
        print(f"    !! no output for sched={sched}: {proc.stdout[-300:]}")
        return None
    return json.loads(out_json.read_text())


def _record(res: Dict, sched: int, **extra) -> Dict:
    st = res["stats"]
    row = {
        "scheduler":       SCHEDULERS[sched],
        "sched_select":    sched,
        "family":          "DNN-aware" if sched in DNN_AWARE else "basic",
        "total_cycles":    st["total_cycles"],
        "array_util_pct":  st["array_utilization_pct"],
        "dma_util_pct":    st["dma_utilization_pct"],
        "overlap_pct":     st["overlap_pct"],
        "mt_tasks":        st["mt_tasks"],
        "ct_tasks":        st["ct_tasks"],
        "inferences":      st["inferences"],
        "bytes_moved":     st["bytes_moved"],
        "layers_completed": st["layers_completed"],
        "layers_expected": st["layers_expected"],
        "incomplete":      bool(st["incomplete"]),
        "timed_out":       bool(st["timed_out"]),
    }
    row.update(extra)
    return row


def _valid(rows: List[Dict]) -> List[Dict]:
    """Drop runs that did not finish the workload -- they are not comparable."""
    bad = [r for r in rows if r["incomplete"] or r["timed_out"]]
    for r in bad:
        print(f"    REJECTED {r['scheduler']}: completed "
              f"{r['layers_completed']}/{r['layers_expected']} layers")
    return [r for r in rows if not (r["incomplete"] or r["timed_out"])]


def _add_speedup(rows: List[Dict], baseline: str = "FIFO") -> List[Dict]:
    base = next((r["total_cycles"] for r in rows
                 if r["scheduler"] == baseline), None)
    for r in rows:
        r["speedup_vs_fifo"] = (base / r["total_cycles"]) if base else float("nan")
    return rows


# ---------------------------------------------------------------------------
# Experiment A -- scheduler comparison across the workload mixes
# ---------------------------------------------------------------------------
def expA_scheduler_comparison(dram_bw: int = 64) -> List[Dict]:
    print("\n=== Exp A: scheduler comparison per workload mix (batch=1) ===")
    out: List[Dict] = []

    for mix in SCHED_EVAL_MIXES:
        label = mix["label"]
        rows_t = build_table(mix, dram_bw=dram_bw, batch=1)
        wl = write_table(rows_t, WLDIR / f"{label.replace(' ', '_')}_b1.txt")
        summ = table_summary(rows_t, dram_bw=dram_bw)
        print(f"\n  {label}: {summ['n_layers']} layers / {summ['n_dnns']} DNNs, "
              f"mem/compute={summ['mem_compute_ratio']:.2f}")

        mix_rows = []
        for sched in SCHEDULERS:
            res = run_sim(wl, sched,
                          RAW / f"expA_{label.replace(' ', '_')}_s{sched}.json",
                          dram_bw=dram_bw)
            if res is None:
                continue
            r = _record(res, sched, workload_mix=label,
                        mem_compute_ratio=summ["mem_compute_ratio"],
                        dram_bw=dram_bw, batch=1)
            mix_rows.append(r)
            print(f"    {SCHEDULERS[sched]:<12s} {r['total_cycles']:>10,d} cyc  "
                  f"util={r['array_util_pct']:5.1f}%  "
                  f"overlap={r['overlap_pct']:5.1f}%"
                  + ("   INCOMPLETE" if r["incomplete"] else ""))

        out.extend(_add_speedup(_valid(mix_rows)))

    return out


# ---------------------------------------------------------------------------
# Experiment C -- speedup vs arithmetic intensity (DRAM bandwidth sweep)
# ---------------------------------------------------------------------------
def expC_arithmetic_intensity(mix_label: str = "Workload mix 3",
                              bandwidths=(8, 16, 32, 64, 128, 256, 512)
                              ) -> List[Dict]:
    print("\n=== Exp C: speedup vs arithmetic intensity (DRAM BW sweep) ===")
    mix = mix_by_label(mix_label)
    out: List[Dict] = []

    for bw in bandwidths:
        rows_t = build_table(mix, dram_bw=bw, batch=1)
        wl = write_table(rows_t, WLDIR / f"ai_bw{bw}.txt")
        summ = table_summary(rows_t, dram_bw=bw)
        bw_rows = []
        for sched in SCHEDULERS:
            res = run_sim(wl, sched, RAW / f"expC_bw{bw}_s{sched}.json",
                          dram_bw=bw)
            if res is None:
                continue
            bw_rows.append(_record(res, sched, workload_mix=mix_label,
                                   dram_bw=bw, batch=1,
                                   mem_compute_ratio=summ["mem_compute_ratio"]))
        bw_rows = _add_speedup(_valid(bw_rows))
        out.extend(bw_rows)
        aimt = next((r for r in bw_rows if r["sched_select"] == 11), None)
        if aimt:
            print(f"  BW={bw:>4d} B/cyc  mem/compute={summ['mem_compute_ratio']:5.2f}  "
                  f"AI-MT speedup={aimt['speedup_vs_fifo']:.3f}  "
                  f"overlap={aimt['overlap_pct']:5.1f}%")
    return out


# ---------------------------------------------------------------------------
# Experiment D -- batch sweep (BATCH-DNN / ++ vs AI-MT)
# ---------------------------------------------------------------------------
def expD_batch_sweep(mix_label: str = "Workload mix 3",
                     batches=(1, 2, 4, 8, 16),
                     dram_bw: int = 64,
                     # 128 MiB, deliberately generous.  At B=16 a single
                     # AI-MT layer needs 54 MiB resident (footprints scale
                     # with B because it cannot batch), which does not fit the
                     # 44 MiB default -- AI-MT would simply stall and be
                     # rejected, and the chart would show a capacity limit
                     # rather than the weight-amortisation effect this
                     # experiment is about.  Exp E covers the tight-capacity
                     # regime on purpose.
                     capacity: int = 128 * 1024 * 1024) -> List[Dict]:
    print("\n=== Exp D: batch sweep (weight-reload amortisation) ===")
    mix = mix_by_label(mix_label)
    out: List[Dict] = []

    for B in batches:
        b_rows = []
        for sched in SCHEDULERS:
            # See the module docstring: non-batching schedulers pay B weight
            # reloads (footprints scaled, batch=1); batching schedulers pay one
            # (footprints unscaled, batch=B).
            if sched in BATCHING:
                rows_t = build_table(mix, dram_bw=dram_bw, batch=B)
                tag = f"batched_b{B}"
            else:
                rows_t = build_table(mix, dram_bw=dram_bw, batch=1,
                                     ai_scale=float(B))
                for r in rows_t:
                    r["compute_cycles"] *= B
                tag = f"serial_b{B}"
            wl = write_table(rows_t, WLDIR / f"{tag}.txt")

            res = run_sim(wl, sched, RAW / f"expD_b{B}_s{sched}.json",
                          dram_bw=dram_bw, capacity=capacity)
            if res is None:
                continue
            b_rows.append(_record(res, sched, workload_mix=mix_label,
                                  dram_bw=dram_bw, batch=B))
        b_rows = _add_speedup(_valid(b_rows))
        out.extend(b_rows)
        for r in b_rows:
            if r["sched_select"] in (11, 12, 13):
                print(f"  B={B:>2d} {r['scheduler']:<12s} "
                      f"{r['total_cycles']:>11,d} cyc  "
                      f"bytes={r['bytes_moved']/1e6:8.2f} MB  "
                      f"speedup={r['speedup_vs_fifo']:.3f}")
    return out


# ---------------------------------------------------------------------------
# Experiment E -- on-chip capacity sweep (re-elaborates per point)
# ---------------------------------------------------------------------------
def expE_capacity_sweep(mix_label: str = "Workload mix 3",
                        # Starts at 16 MiB: at batch 4 a single AI-MT layer
                        # already needs 13.6 MiB resident, so below this point
                        # NO scheduler can make progress and the comparison is
                        # meaningless rather than interesting.
                        capacities=(16*1024*1024, 24*1024*1024, 32*1024*1024,
                                    46137344, 64*1024*1024, 128*1024*1024),
                        batch: int = 4,
                        dram_bw: int = 64) -> List[Dict]:
    print("\n=== Exp E: on-chip capacity sweep ===")
    mix = mix_by_label(mix_label)
    out: List[Dict] = []

    for cap in capacities:
        c_rows = []
        for sched in SCHEDULERS:
            if sched in BATCHING:
                rows_t = build_table(mix, dram_bw=dram_bw, batch=batch)
                tag = f"cap_batched_b{batch}"
            else:
                rows_t = build_table(mix, dram_bw=dram_bw, batch=1,
                                     ai_scale=float(batch))
                for r in rows_t:
                    r["compute_cycles"] *= batch
                tag = f"cap_serial_b{batch}"
            wl = write_table(rows_t, WLDIR / f"{tag}.txt")

            res = run_sim(wl, sched, RAW / f"expE_cap{cap}_s{sched}.json",
                          dram_bw=dram_bw, capacity=cap)
            if res is None:
                continue
            c_rows.append(_record(res, sched, workload_mix=mix_label,
                                  dram_bw=dram_bw, batch=batch,
                                  capacity_bytes=cap,
                                  capacity_mb=cap / (1024 * 1024)))
        # Unlike the other experiments this one KEEPS the failed runs, flagged.
        # "Did not complete below X MB" is the finding here, so dropping those
        # rows would erase the result instead of reporting it.
        _add_speedup([r for r in c_rows if not r["incomplete"]])
        for r in c_rows:
            if r["incomplete"] or r["timed_out"]:
                r["speedup_vs_fifo"] = float("nan")
        out.extend(c_rows)
        print(f"  capacity={cap/(1024*1024):5.1f} MB: "
              + "  ".join(
                  f"{r['scheduler']}="
                  + ("DEADLOCK" if r["incomplete"] else f"{r['total_cycles']:,}")
                  for r in c_rows if r["sched_select"] in (11, 12, 13)))
    return out


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", default="all",
                    choices=["all", "A", "C", "D", "E"])
    ap.add_argument("--dram-bw", type=int, default=64)
    args = ap.parse_args()

    RESULTS.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    WLDIR.mkdir(parents=True, exist_ok=True)

    ensure_built()

    import pandas as pd

    if args.exp in ("all", "A"):
        rows = expA_scheduler_comparison(dram_bw=args.dram_bw)
        pd.DataFrame(rows).to_csv(RESULTS / "expA_scheduler_comparison.csv",
                                  index=False)

    if args.exp in ("all", "C"):
        rows = expC_arithmetic_intensity()
        pd.DataFrame(rows).to_csv(RESULTS / "expC_arithmetic_intensity.csv",
                                  index=False)

    if args.exp in ("all", "D"):
        rows = expD_batch_sweep()
        pd.DataFrame(rows).to_csv(RESULTS / "expD_batch_sweep.csv", index=False)

    if args.exp in ("all", "E"):
        rows = expE_capacity_sweep()
        pd.DataFrame(rows).to_csv(RESULTS / "expE_capacity_sweep.csv",
                                  index=False)

    print(f"\nCSVs written to {RESULTS}")


if __name__ == "__main__":
    main()
