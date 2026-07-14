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
    dut.ws_input_ch.value = 0
    await g._pulse_start(dut)

    events = {}
    i = 0
    wbit = W - 1
    in_base = cfg["input_base_addr"]
    for cyc in range(1, 80):
        await RisingEdge(dut.clk)

        st   = int(ws.state.value)
        iav  = int(dut.ext_input_addr_valid_h.value)
        wfd  = int(ws.weight_fetch_done.value)
        ifd  = int(ws.input_fetch_done.value)
        pen  = int(ws.pe_enable.value)
        wreg = g._tosigned(int(ws.gen_pe_rows[0].gen_pe_cols[W-1].pe_inst.weight_reg.value))
        acc  = g._tosigned(int(ws.gen_pe_rows[0].gen_pe_cols[W-1].pe_inst.accumulator.value), 48)
        avin = int(ws.gen_pe_rows[0].gen_pe_cols[W-1].pe_inst.activation_valid_in.value)
        psv  = int(ws.gen_pe_rows[0].gen_pe_cols[W-1].pe_inst.psum_valid_in.value)
        oav  = int(dut.ext_output_addr_valid_1d.value)
        odata = g._tosigned(int(dut.ext_output_data_1d[0].value))

        wvalid2d = 0
        note = ""
        if iav & 1:
            addr = int(dut.ext_input_addr_h[0].value)
            off = addr - in_base
            v = int(flat_in[off]) if 0 <= off < flat_in.size else 0
            kh_i, kw_i = divmod(i, KW)
            wv = int(wq[kh_i, kw_i, 0, 0]) if kh_i < cfg["weight_kh"] else 0
            dut.ext_weight_data_2d[0][W - 1].value = wv & 0xFFFFFFFF
            wvalid2d |= (1 << wbit)
            events.setdefault(cyc + max(1, 3 - W), []).append(("x", v))
            note = f"obs#{i} addr={addr} x={v} w={wv}"
            i += 1
        dut.ext_weight_data_valid_2d.value = wvalid2d

        dut.ext_input_data_valid_h.value = 0
        for ev in events.pop(cyc, []):
            _, xv = ev
            dut.ext_input_data_h[0].value = xv & 0xFFFFFFFF
            dut.ext_input_data_valid_h.value = 1
            note += " serve_x"

        dut._log.info(
            f"c{cyc:03d} st={st} iav={iav:02x} wfd={wfd} ifd={ifd} "
            f"pen={pen:x} wreg={wreg} acc={acc} avin={avin} psv={psv} "
            f"oav={oav} od={odata} {note}")
        if int(dut.done.value) == 1:
            dut._log.info(f"DONE at {cyc}")
            break
