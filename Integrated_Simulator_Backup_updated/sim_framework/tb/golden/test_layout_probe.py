"""Read-only layout probe (root-cause evidence, no RTL changes).

Runs the SAME OS tile (tiny_cnn L0, oh=0, ow0=0, ch0) once per memory
layout and records, from the real Verilator simulation:
  - the full sequence of input addresses issued on ext_input_addr_w[*]
  - the weight addresses issued on ext_weight_addr_1d[0]
  - the output addresses on ext_output_addr_2d
  - every AXI off-chip read request (axi_arvalid/axi_arvalid_addr)
  - the cycle count to done
Dumps one JSON with all three layouts for side-by-side comparison.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

import test_golden_single as g


async def _probe_one(dut, p, cfg, layout_name, wq_stream, H, W):
    xq = g._quant(np.load(p["layer_dir"] / "input.npy"), p["frac_x"])
    flat_in = g._flat_input(xq, layout_name)
    in_base = cfg["input_base_addr"]
    n_tuples = cfg["weight_c"] * cfg["weight_kh"] * cfg["weight_kw"]
    timeout = n_tuples * (W + 1) + 800 + 3 * n_tuples * (H + W) + 600
    if p.get("casting", "MULTICAST") != "MULTICAST":
        timeout += 12 * n_tuples * H * W + 2000

    dut.mem_layout.value = g.LAYOUTS[layout_name]
    dut.tile_row.value = 0
    dut.tile_col_start.value = 0
    dut.tile_ch_start.value = 0
    await g._pulse_start(dut)

    rec = {"input_addrs": [], "weight_addrs": [], "output_addrs": [],
           "axi_reads": [], "cycles": 0}
    events: dict[int, list] = {}
    n = 0
    cyc = 0
    while cyc < timeout:
        await RisingEdge(dut.clk)
        cyc += 1

        # --- record AXI off-chip requests (the DRAM path) ---
        if int(dut.axi_arvalid.value):
            rec["axi_reads"].append(
                [cyc, int(dut.axi_arvalid_addr.value), int(dut.axi_arlen.value)])

        # --- record + serve array-port input requests ---
        iav = int(dut.ext_input_addr_valid_w.value)
        if iav:
            for c in range(W):
                if (iav >> c) & 1:
                    addr = int(dut.ext_input_addr_w[c].value)
                    rec["input_addrs"].append([cyc, c, addr])
                    off = addr - in_base
                    val = int(flat_in[off]) if 0 <= off < flat_in.size else 0
                    if c == 0:
                        if n < n_tuples:
                            for r in range(H):
                                events.setdefault(cyc + r, []).append(
                                    ("w", r, int(wq_stream[r][n])))
                        n += 1
                    events.setdefault(cyc + 2, []).append(("x", c, val))

        wav = int(dut.ext_weight_addr_valid_1d.value)
        if wav & 1:
            rec["weight_addrs"].append([cyc, int(dut.ext_weight_addr_1d[0].value)])

        oav = int(dut.ext_output_addr_valid_2d.value)
        if oav:
            for r in range(H):
                for c in range(W):
                    if (oav >> (r * W + c)) & 1:
                        rec["output_addrs"].append(
                            [r, c, int(dut.ext_output_addr_2d[r][c].value)])

        wvalid = 0
        ivalid = 0
        for ev in events.pop(cyc, []):
            if ev[0] == "w":
                _, r, wv = ev
                dut.ext_weight_data_1d[r].value = wv & 0xFFFFFFFF
                wvalid |= (1 << r)
            else:
                _, c, xv = ev
                dut.ext_input_data_w[c].value = xv & 0xFFFFFFFF
                ivalid |= (1 << c)
        dut.ext_weight_data_valid_1d.value = wvalid
        dut.ext_input_data_valid_w.value = ivalid

        if int(dut.done.value) == 1:
            rec["cycles"] = cyc
            return rec
    raise TimeoutError(f"layout probe {layout_name}: no done in {timeout}")


@cocotb.test()
async def layout_probe(dut):
    p = g._read_cfg()
    cfg = p["cfg"]
    H, W = p["array_h"], p["array_w"]
    wq = g._quant(np.load(p["layer_dir"] / "weights.npy"), p["frac_w"])
    K = cfg["weight_k"]
    C, KH, KW = cfg["weight_c"], cfg["weight_kh"], cfg["weight_kw"]
    wq_stream = wq.transpose(3, 2, 0, 1).reshape(K, C * KH * KW)

    cocotb.start_soon(Clock(dut.clk, 5.0, unit="ns").start())
    g._set_layer_ports(dut, cfg, 0)
    g._zero_data_ports(dut, H, W)
    dut.start.value = 0
    await g._reset(dut)
    cocotb.start_soon(g._axi_responder(dut))

    out = {}
    for layout in ["ROW_MAJOR", "COLUMN_MAJOR", "CHANNEL_MAJOR"]:
        out[layout] = await _probe_one(dut, p, cfg, layout, wq_stream, H, W)
        for _ in range(6):
            await RisingEdge(dut.clk)

    Path(os.environ["GOLDEN_RESULT_JSON"]).write_text(json.dumps(out))
    dut._log.info("layout probe complete")
