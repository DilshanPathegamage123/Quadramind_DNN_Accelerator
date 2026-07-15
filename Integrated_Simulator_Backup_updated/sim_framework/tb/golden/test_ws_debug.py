"""Single WS pass with per-cycle tracing to find why accumulate never fires."""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

import test_golden_single as g


@cocotb.test()
async def ws_debug(dut):
    p = g._read_cfg()
    cfg = p["cfg"]
    H, W = p["array_h"], p["array_w"]
    xq = g._quant(np.load(p["layer_dir"] / "input.npy"), p["frac_x"])
    wq = g._quant(np.load(p["layer_dir"] / "weights.npy"), p["frac_w"])
    flat_in = g._flat_input(xq, p["layout"])
    KW = cfg["weight_kw"]

    cocotb.start_soon(Clock(dut.clk, 5.0, unit="ns").start())
    g._set_layer_ports(dut, cfg, g.LAYOUTS[p["layout"]])
    g._zero_data_ports(dut, H, W)
    dut.start.value = 0
    dut.tile_row.value = 0
    dut.tile_col_start.value = 0
    dut.tile_ch_start.value = 0
    await g._reset(dut)

    ws = dut.u_array.g_ws.u_ws
    xq_dbg = xq
    dut.ws_input_ch.value = 0
    await g._pulse_start(dut)

    events = {}
    scheduled = False
    wbit = W - 1
    KH = cfg["weight_kh"]
    for cyc in range(1, 80):
        await RisingEdge(dut.clk)

        st   = int(ws.state.value)
        iav  = int(dut.ext_input_addr_valid_h.value)
        pen  = int(ws.pe_enable.value)
        pe   = ws.gen_pe_rows[0].gen_pe_cols[W-1].pe_inst
        wreg = g._tosigned(int(pe.weight_reg.value))
        acc  = g._tosigned(int(pe.accumulator.value), 48)
        avin = int(pe.activation_valid_in.value)
        ain  = g._tosigned(int(pe.activation_in.value))
        psv  = int(pe.psum_valid_in.value)
        psin = g._tosigned(int(pe.psum_in.value), 48)
        oav  = int(dut.ext_output_addr_valid_1d.value)
        odata = g._tosigned(int(dut.ext_output_data_1d[0].value))

        note = ""
        if not scheduled and st == 3:      # COMPUTE - anchored schedule
            for i in range(KH * KW):
                kh_i, kw_i = divmod(i, KW)
                wv = int(wq[kh_i, kw_i, 0, 0])
                xv = int(xq_dbg[0, 0 + kh_i, 0 + kw_i, 0])
                events.setdefault(cyc + i, []).append(("w", wv))
                events.setdefault(cyc + i + 2, []).append(("x", xv))
            scheduled = True
            note = "ANCHOR"

        wvalid2d = 0
        dut.ext_input_data_valid_h.value = 0
        for ev in events.pop(cyc, []):
            if ev[0] == "w":
                dut.ext_weight_data_2d[0][W - 1].value = ev[1] & 0xFFFFFFFF
                wvalid2d |= (1 << wbit)
                note += f" drv_w={ev[1]}"
            else:
                dut.ext_input_data_h[0].value = ev[1] & 0xFFFFFFFF
                dut.ext_input_data_valid_h.value = 1
                note += f" drv_x={ev[1]}"
        dut.ext_weight_data_valid_2d.value = wvalid2d

        dut._log.info(
            f"c{cyc:03d} st={st} iav={iav:02x} pen={pen:04x} wreg={wreg} "
            f"ain={ain} avin={avin} psin={psin} psv={psv} acc={acc} "
            f"oav={oav} od={odata} {note}")
        if int(dut.done.value) == 1:
            dut._log.info(f"DONE at {cyc}")
            break
