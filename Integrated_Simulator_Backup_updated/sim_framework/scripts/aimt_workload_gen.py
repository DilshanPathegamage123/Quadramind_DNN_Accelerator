"""Scheduling-table generator for the dual-issue multi-DNN execution simulator.

Emits the plain-text workload file consumed by tb/exec/tb_multi_dnn_exec.sv.
One row per layer:

    <idx> <dnn_id> <prev> <mem_cycles> <compute_cycles> <wfp> <ifp> <ofp> <batch>

WHERE THE NUMBERS COME FROM
---------------------------
Layer shapes are the real MLPerf-derived LayerConfigs already in
scripts/workloads.py -- nothing here is invented.

    compute_cycles : software_ref.estimate_cycles(layer, dataflow, h, w)
                     -- the framework's existing analytical array model.
    weight_fp      : K * C * KH * KW * bytes           (loaded once per batch)
    ifmap_fp       : C * H * W * bytes                 (scales with batch)
    ofmap_fp       : K * OH * OW * bytes
    mem_cycles     : (weight_fp + ifmap_fp) / dram_bw
                     -- the COMPILER'S estimate, which is what AI-MT's balance
                     conditions reason over.  The actual memory time is
                     whatever dram_model takes; the two need not agree, and
                     that mismatch is realistic.

ARITHMETIC INTENSITY
--------------------
`ai_scale` rescales the memory side against the compute side without touching
layer shapes, so a mix can be swept from compute-bound to memory-bound. It
multiplies the footprints (and hence mem_cycles). ai_scale = 1.0 is the
workload as specified. This is the knob behind the falsifiable prediction:
overlap gains must grow as the mix becomes memory-bound and vanish when it is
compute-bound.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pysim.software_ref import estimate_cycles
from scripts.workloads import (CLOUD_WORKLOADS, EDGE_WORKLOADS,
                               SCHED_EVAL_MIXES)

NO_PRED = 255          # aimt_scheduler.sv: 8'hFF means "no predecessor"
MAX_LAYERS = 32        # must match tb_multi_dnn_exec.sv / MAX_LAYERS

_ALL_WORKLOADS = {wl["name"]: wl for wl in (EDGE_WORKLOADS + CLOUD_WORKLOADS)}


def workload_by_name(name: str) -> dict:
    return _ALL_WORKLOADS[name]


def all_mix_names() -> List[str]:
    return [m["label"] for m in SCHED_EVAL_MIXES]


def mix_by_label(label: str) -> dict:
    for m in SCHED_EVAL_MIXES:
        if m["label"] == label:
            return m
    raise KeyError(label)


def build_table(mix: dict,
                dataflow: str = "OS",
                array_h: int = 8,
                array_w: int = 8,
                bytes_per_elem: int = 2,
                dram_bw: int = 16,
                batch: int = 1,
                ai_scale: float = 1.0,
                max_layers: int = MAX_LAYERS) -> List[Dict]:
    """Build the per-layer scheduling table for one workload mix."""
    rows: List[Dict] = []
    idx = 0

    for dnn_id, wl_name in enumerate(mix["dnns"]):
        wl = _ALL_WORKLOADS.get(wl_name)
        if wl is None:
            continue
        prev_in_dnn = NO_PRED

        for layer in wl["layers"]:
            if idx >= max_layers:
                break

            K, C = layer.weight_k, layer.weight_c
            KH, KW = layer.weight_kh, layer.weight_kw
            H, W = layer.input_height, layer.input_width
            OH, OW = layer.output_height, layer.output_width

            compute_cycles = estimate_cycles(layer, dataflow, array_h, array_w)

            wfp = int(K * C * KH * KW * bytes_per_elem * ai_scale)
            ifp = int(C * H * W * bytes_per_elem * ai_scale)
            ofp = int(K * OH * OW * bytes_per_elem * ai_scale)

            # Compiler's memory-time estimate for a unit batch.
            mem_cycles = int((wfp + ifp) / max(dram_bw, 1))

            rows.append({
                "idx":            idx,
                "dnn_id":         dnn_id,
                "prev":           prev_in_dnn,
                "mem_cycles":     max(mem_cycles, 1),
                "compute_cycles": max(int(compute_cycles), 1),
                "wfp":            max(wfp, 1),
                "ifp":            max(ifp, 1),
                "ofp":            max(ofp, 1),
                "batch":          max(int(batch), 1),
                "_dnn":           wl_name,
                "_layer":         layer.name,
            })
            prev_in_dnn = idx
            idx += 1

    return rows


def write_table(rows: List[Dict], path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{len(rows)}"]
    for r in rows:
        lines.append(
            f"{r['idx']} {r['dnn_id']} {r['prev']} {r['mem_cycles']} "
            f"{r['compute_cycles']} {r['wfp']} {r['ifp']} {r['ofp']} {r['batch']}"
        )
    path.write_text("\n".join(lines) + "\n")
    return path


def table_summary(rows: List[Dict], dram_bw: int = 16) -> Dict:
    """Aggregate compute/memory demand -- used to report the mix's balance."""
    total_compute = sum(r["compute_cycles"] * r["batch"] for r in rows)
    total_bytes = sum(r["wfp"] + r["ifp"] * r["batch"] for r in rows)
    total_mem_cycles = total_bytes / max(dram_bw, 1)
    return {
        "n_layers":         len(rows),
        "n_dnns":           len({r["dnn_id"] for r in rows}),
        "total_compute":    total_compute,
        "total_bytes":      total_bytes,
        "total_mem_cycles": total_mem_cycles,
        # >1 means memory-bound: the DMA needs more time than the array.
        "mem_compute_ratio": total_mem_cycles / max(total_compute, 1),
    }


if __name__ == "__main__":
    for m in SCHED_EVAL_MIXES:
        rows = build_table(m)
        s = table_summary(rows)
        print(f"{m['label']:16s} layers={s['n_layers']:3d} dnns={s['n_dnns']} "
              f"compute={s['total_compute']:>10,d} "
              f"mem_cyc={s['total_mem_cycles']:>12,.0f} "
              f"mem/compute={s['mem_compute_ratio']:.2f}")
