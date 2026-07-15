"""Multi-DNN golden test: run a mix of DNN tasks through multi_dnn_top under
a selectable scheduler and verify each DNN still produces its TF-golden
output (the scheduler must only change ordering, not results).

Env (set by run_golden_multi.py):
    GOLDEN_SCHED       FIFO | AIMT | BATCHDNN_PP
    GOLDEN_RESULT_JSON output path
    GOLDEN_FRAMEWORK   framework root (for models/)
    GOLDEN_ARRAY_H/W, GOLDEN_FRAC_X/W as usual

The task mix (one output-pixel invocation each, OS dataflow, column 0):
    task/dnn 0: tiny_cnn layer_00 pixel (0,0)  channels 0..7
    task/dnn 1: mnist_cnn layer_00 pixel (1,1) channels 0..7 (ReLU on compare)
    task/dnn 2: tiny_cnn layer_01 pixel (0,0)  channels 0..3
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

# Canonical select codes (F6 fixed in RTL: the unified wrapper now decodes
# select-11 for the DNN-aware family, so the documented codes work).
SCHED_SEL = {"FIFO": 0, "LIFO": 1, "AIMT": 11, "BATCHDNN": 12,
             "BATCHDNN_PP": 13}


def _quant(a, fb):
    q = np.round(a.astype(np.float64) * (1 << fb)).astype(np.int64)
    return np.clip(q, -(1 << 31), (1 << 31) - 1)


def _flat_channel_major(xq):
    return np.ascontiguousarray(xq[0].transpose(2, 0, 1)).ravel()


def _tosigned(v, bits=32):
    v &= (1 << bits) - 1
    return v - (1 << bits) if v & (1 << (bits - 1)) else v


def _decode_sched_out(v: int) -> dict:
    # struct packed {valid; is_dnn_aware; [7:0] id; [3:0] dnn; is_ct; [15:0] burst}
    return {
        "valid":     (v >> 30) & 1,
        "dnn_aware": (v >> 29) & 1,
        "id":        (v >> 21) & 0xFF,
        "dnn":       (v >> 17) & 0xF,
        "is_ct":     (v >> 16) & 1,
    }


def _load_task(framework: Path, layer_rel: str, pixel, fx, fw):
    ld = framework / layer_rel
    cfg = json.loads((ld / "config.json").read_text())
    xq = _quant(np.load(ld / "input.npy"), fx)
    wq = _quant(np.load(ld / "weights.npy"), fw)
    K = cfg["weight_k"]
    C, KH, KW = cfg["weight_c"], cfg["weight_kh"], cfg["weight_kw"]
    wq_stream = wq.transpose(3, 2, 0, 1).reshape(K, C * KH * KW)
    expected = np.load(ld / "expected.npy").astype(np.float64)
    return {
        "layer": layer_rel, "cfg": cfg, "pixel": pixel,
        "flat_in": _flat_channel_major(xq),
        "wq_stream": wq_stream,
        "n_tuples": C * KH * KW,
        "expected": expected,
        "captured": {},          # ch -> fixed value
        "cycles": 0,
        "dispatches": 0,
    }


@cocotb.test()
async def golden_multi(dut):
    framework = Path(os.environ["GOLDEN_FRAMEWORK"])
    sched = os.environ.get("GOLDEN_SCHED", "FIFO")
    H = int(os.environ.get("GOLDEN_ARRAY_H", "8"))
    W = int(os.environ.get("GOLDEN_ARRAY_W", "8"))
    fx = int(os.environ.get("GOLDEN_FRAC_X", "14"))
    fw = int(os.environ.get("GOLDEN_FRAC_W", "14"))
    result_path = Path(os.environ["GOLDEN_RESULT_JSON"])

    tasks = [
        _load_task(framework, "models/tiny_cnn/layer_00", (0, 0), fx, fw),
        _load_task(framework, "models/mnist_cnn/layer_00", (1, 1), fx, fw),
        _load_task(framework, "models/tiny_cnn/layer_01", (0, 0), fx, fw),
    ]

    cocotb.start_soon(Clock(dut.clk, 5.0, unit="ns").start())

    # ---- static input defaults ----
    dut.scheduler_select.value = SCHED_SEL[sched]
    dut.task_valid.value = 0
    dut.task_id.value = 0
    dut.burst_time.value = 0
    dut.task_priority.value = 0
    dut.deadline.value = 0
    dut.task_tick.value = 0
    dut.st_write_en.value = 0
    dut.st_layer_idx.value = 0
    dut.st_dnn_id.value = 0
    dut.st_prev_layer.value = 0
    dut.st_mem_cycles.value = 0
    dut.st_compute_cycles.value = 0
    dut.st_weight_fp.value = 0
    dut.st_ifmap_fp.value = 0
    dut.st_ofmap_fp.value = 0
    dut.st_batch.value = 0
    dut.st_total_layers.value = 0
    dut.axi_arready.value = 1
    dut.axi_rdata.value = 0
    dut.axi_rvalid.value = 0
    dut.axi_rlast.value = 0
    dut.ext_input_data_valid_w.value = 0
    dut.ext_input_data_valid_h.value = 0
    dut.ext_weight_data_valid_1d.value = 0
    dut.ext_weight_data_valid_2d.value = 0
    for i in range(W):
        dut.ext_input_data_w[i].value = 0
    for i in range(H):
        dut.ext_input_data_h[i].value = 0
        dut.ext_weight_data_1d[i].value = 0
    dut.cfg_mem_layout.value = 0
    dut.cfg_tile_row.value = 0
    dut.cfg_tile_col_start.value = 0
    dut.cfg_tile_ch_start.value = 0
    dut.cfg_ws_input_ch.value = 0
    dut.cfg_ws_kernel_row.value = 0
    dut.cfg_ws_kernel_col_start.value = 0

    dut.rst_n.value = 0
    for _ in range(5):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # ---- submit workload ----
    if SCHED_SEL[sched] <= 10:
        # basic/advanced family: FIFO task queue
        for tid, t in enumerate(tasks):
            dut.task_valid.value = 1
            dut.task_id.value = tid
            dut.burst_time.value = 10 * (tid + 1)
            dut.task_priority.value = tid
            dut.deadline.value = 1000 * (tid + 1)
            await RisingEdge(dut.clk)
        dut.task_valid.value = 0
    else:
        # DNN-aware family: scheduling table, one root layer per DNN.
        # Post-F7 the queue registers are single-owner and the balance
        # check bootstraps, so rows are written back-to-back with real
        # (nonzero) mem_cycles; the main loop below serves dispatches that
        # may begin while later rows are still being written.
        async def _load_table():
            for tid, t in enumerate(tasks):
                dut.st_write_en.value = 1
                dut.st_layer_idx.value = tid
                dut.st_dnn_id.value = tid
                dut.st_prev_layer.value = 0xFF
                dut.st_mem_cycles.value = 50
                dut.st_compute_cycles.value = 300
                dut.st_weight_fp.value = 1024
                dut.st_ifmap_fp.value = 1024
                dut.st_ofmap_fp.value = 1024
                dut.st_batch.value = 1
                dut.st_total_layers.value = len(tasks)
                await RisingEdge(dut.clk)
            dut.st_write_en.value = 0

        cocotb.start_soon(_load_table())

    # ---- dispatch + serve loop ----
    order = []
    current = None
    events: dict[int, list] = {}
    n = 0
    run_start = 0
    completions = 0
    needed = len(tasks)
    cyc = 0
    TIMEOUT = 200_000
    idle_after_all_dispatch = 0

    probe = bool(os.environ.get("GOLDEN_MULTI_PROBE"))
    aimt = None
    if probe:
        aimt = (dut.u_sched.u_dnn.u_batchpp if sched == "BATCHDNN_PP"
                else dut.u_sched.u_dnn.u_aimt)

    while cyc < TIMEOUT:
        await RisingEdge(dut.clk)
        cyc += 1

        if probe and cyc < 3000 and cyc % 1 == 0:
            mtv = int(aimt.mt_valid.value)
            ctv = int(aimt.ct_valid.value)
            mta = int(aimt.mt_active.value)
            cta = int(aimt.ct_active.value)
            mcq = int(aimt.mt_cq_cnt.value)
            ccq = int(aimt.ct_cq_cnt.value)
            sct = int(aimt.sct_cnt.value)
            ctr = int(aimt.compute_cycle_ctr.value)
            mad = int(dut.u_sched.mem_access_done.value)
            cd  = int(dut.u_sched.compute_done.value)
            if (mtv, ctv, mta, cta, mcq, ccq, sct, mad, cd) != getattr(
                    golden_multi, "_last", None):
                golden_multi._last = (mtv, ctv, mta, cta, mcq, ccq, sct, mad, cd)
                dut._log.info(
                    f"c{cyc:05d} mtv={mtv} ctv={ctv} mta={mta} cta={cta} "
                    f"mtcq={mcq} ctcq={ccq} sct={sct} ctr={ctr} "
                    f"mad={mad} cd={cd}")

        if current is None:
            so = _decode_sched_out(int(dut.sched_out_dbg.value))
            if so["valid"]:
                tid = so["dnn"] if so["dnn_aware"] else so["id"]
                if tid < len(tasks):
                    current = tasks[tid]
                    current["dispatches"] += 1
                    order.append({"task": tid, "cycle": cyc,
                                  "is_ct": so["is_ct"] if so["dnn_aware"] else None})
                    cfg = current["cfg"]
                    oh, ow = current["pixel"]
                    dut.cfg_mem_layout.value       = 0
                    dut.cfg_input_channels.value   = cfg["input_channels"]
                    dut.cfg_input_height.value     = cfg["input_height"]
                    dut.cfg_input_width.value      = cfg["input_width"]
                    dut.cfg_weight_k.value         = cfg["weight_k"]
                    dut.cfg_weight_c.value         = cfg["weight_c"]
                    dut.cfg_weight_kh.value        = cfg["weight_kh"]
                    dut.cfg_weight_kw.value        = cfg["weight_kw"]
                    dut.cfg_output_channels.value  = cfg["output_channels"]
                    dut.cfg_output_height.value    = cfg["output_height"]
                    dut.cfg_output_width.value     = cfg["output_width"]
                    dut.cfg_input_base_addr.value  = cfg["input_base_addr"]
                    dut.cfg_weight_base_addr.value = cfg["weight_base_addr"]
                    dut.cfg_output_base_addr.value = cfg["output_base_addr"]
                    dut.cfg_tile_row.value         = oh
                    dut.cfg_tile_col_start.value   = ow
                    dut.cfg_tile_ch_start.value    = 0
                    events = {}
                    n = 0
                    run_start = cyc

        # ---- OS column-0 serving (same schedule as single-DNN harness) ----
        if current is not None:
            t = current
            iav = int(dut.ext_input_addr_valid_w.value)
            if iav & 1:
                addr = int(dut.ext_input_addr_w[0].value)
                off = addr - t["cfg"]["input_base_addr"]
                val = int(t["flat_in"][off]) if 0 <= off < t["flat_in"].size else 0
                wqs = t["wq_stream"]
                K = t["cfg"]["weight_k"]
                # natural schedule (F5 fixed in RTL)
                if n < t["n_tuples"]:
                    for r in range(H):
                        events.setdefault(cyc + r, []).append(
                            ("w", r, int(wqs[min(r, K - 1)][n])))
                    events.setdefault(cyc + 3, []).append(("x", val))
                n += 1

            oav = int(dut.ext_output_addr_valid_2d.value)
            if oav:
                for r in range(H):
                    if (oav >> (r * W)) & 1 and r < t["cfg"]["weight_k"]:
                        t["captured"][r] = _tosigned(
                            int(dut.ext_output_data_2d[r][0].value))

            wvalid = 0
            dut.ext_input_data_valid_w.value = 0
            for ev in events.pop(cyc, []):
                if ev[0] == "w":
                    _, r, wv = ev
                    dut.ext_weight_data_1d[r].value = wv & 0xFFFFFFFF
                    wvalid |= (1 << r)
                else:
                    _, xv = ev
                    dut.ext_input_data_w[0].value = xv & 0xFFFFFFFF
                    dut.ext_input_data_valid_w.value = 1
            dut.ext_weight_data_valid_1d.value = wvalid

            if int(dut.task_complete_pulse.value) == 1:
                t["cycles"] += cyc - run_start
                completions += 1
                current = None

        # every task must produce at least one full result (DNN-aware
        # schedulers may dispatch a task more than once: MT + CT)
        if completions >= needed and all(t["captured"] for t in tasks):
            if all(t["dispatches"] > 0 for t in tasks):
                idle_after_all_dispatch += 1
                if idle_after_all_dispatch > 300:
                    break

    # ---- compare against golden ----
    per_task = []
    all_pass = True
    for tid, t in enumerate(tasks):
        oh, ow = t["pixel"]
        K = t["cfg"]["weight_k"]
        exp = t["expected"][0, oh, ow, :min(K, H)]
        fs = float(np.abs(t["expected"]).max())
        act = np.array([t["captured"].get(r, 0) for r in range(min(K, H))],
                       dtype=np.float64) / (1 << (fx + fw))
        if "mnist" in t["layer"]:
            act = np.maximum(act, 0.0)
        err = np.abs(act - exp)
        ok = bool((err <= 0.05 * fs).all()) and len(t["captured"]) > 0
        all_pass &= ok
        per_task.append({
            "task": tid, "layer": t["layer"], "pixel": list(t["pixel"]),
            "channels_checked": int(min(K, H)),
            "captured": len(t["captured"]),
            "dispatches": t["dispatches"],
            "cycles": t["cycles"],
            "max_err_pct_fs": float(err.max() / fs * 100.0),
            "passed": ok,
        })

    out = {
        "scheduler": sched,
        "completions": completions,
        "dispatch_order": order,
        "tasks": per_task,
        "total_cycles": cyc,
        "all_pass": bool(all_pass),
    }
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(out, indent=2))
    assert completions >= needed, \
        f"only {completions}/{needed} tasks completed (order={order})"
    assert all_pass, f"golden mismatch: {per_task}"
