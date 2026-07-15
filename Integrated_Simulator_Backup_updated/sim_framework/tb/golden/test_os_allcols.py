"""OS all-columns probe (post-F1): serve input data to ALL array columns in
one invocation and compare every PE column against the exact integer
convolution. Purpose: measure whether the OS array can compute multiple
output pixels per pass now that all columns are enabled, or whether the
psum_in coupling in the PE accumulate path corrupts columns >= 1."""
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
async def os_allcols(dut):
    p = g._read_cfg()
    cfg = p["cfg"]
    H, W = p["array_h"], p["array_w"]
    xq = g._quant(np.load(p["layer_dir"] / "input.npy"), p["frac_x"])
    wq = g._quant(np.load(p["layer_dir"] / "weights.npy"), p["frac_w"])
    K = cfg["weight_k"]
    C, KH, KW = cfg["weight_c"], cfg["weight_kh"], cfg["weight_kw"]
    wq_stream = wq.transpose(3, 2, 0, 1).reshape(K, C * KH * KW)
    flat_in = g._flat_input(xq, p["layout"])
    n_tuples = C * KH * KW
    in_base = cfg["input_base_addr"]

    cocotb.start_soon(Clock(dut.clk, 5.0, unit="ns").start())
    g._set_layer_ports(dut, cfg, g.LAYOUTS[p["layout"]])
    g._zero_data_ports(dut, H, W)
    dut.start.value = 0
    dut.tile_row.value = 0
    dut.tile_col_start.value = 0
    dut.tile_ch_start.value = 0
    await g._reset(dut)
    await g._pulse_start(dut)

    events: dict[int, list] = {}
    results = {}
    n = 0                      # tuple counter, advanced on col-0 observations
    cyc = 0
    timeout = n_tuples * (W + 1) + 800
    while cyc < timeout:
        await RisingEdge(dut.clk)
        cyc += 1

        iav = int(dut.ext_input_addr_valid_w.value)
        if iav:
            for c in range(W):
                if (iav >> c) & 1:
                    addr = int(dut.ext_input_addr_w[c].value)
                    off = addr - in_base
                    val = int(flat_in[off]) if 0 <= off < flat_in.size else 0
                    tup = n if c == 0 else n - 1  # col c observed c cycles later
                    if c == 0:
                        # weight schedule identical to the production harness
                        if n < n_tuples:
                            if n == 0:
                                for r in range(H):
                                    events.setdefault(cyc + r, []).append(
                                        ("w", r, int(wq_stream[min(r, K-1)][0])))
                            else:
                                for r in range(2, H):
                                    events.setdefault(cyc + r - 2, []).append(
                                        ("w", r, int(wq_stream[min(r, K-1)][n])))
                            if n + 1 < n_tuples:
                                for r in range(min(2, H)):
                                    events.setdefault(cyc + W - 2 + r, []).append(
                                        ("w", r, int(wq_stream[min(r, K-1)][n+1])))
                        tup0 = n
                        n += 1
                    # serve: tuple 0 at obs+3 (weight lead), others at obs+1
                    is_first = (c == 0 and tup0 == 0) or (c > 0 and n - 1 == 0)
                    delay = 3 if is_first else 1
                    events.setdefault(cyc + delay, []).append(("x", c, val))

        oav = int(dut.ext_output_addr_valid_2d.value)
        if oav:
            for r in range(H):
                for c in range(W):
                    if (oav >> (r * W + c)) & 1:
                        results[(r, c)] = g._tosigned(
                            int(dut.ext_output_data_2d[r][c].value))

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
            break

    # exact integer reference: out(r, c) = pixel (oh=0, ow=c), channel r
    x0 = xq[0]
    report = {}
    n_exact = 0
    for (r, c), got in sorted(results.items()):
        if r >= K or c >= cfg["output_width"]:
            continue
        patch = x0[0:KH, c:c+KW, :]
        exact = int(np.sum(patch.transpose(2, 0, 1).ravel()
                    * wq_stream[r][: C*KH*KW]))
        ok = (got == exact)
        n_exact += ok
        report[f"r{r}c{c}"] = {"rtl": got, "exact": exact, "match": bool(ok)}
    out = {"n_cells": len(report), "n_exact": n_exact, "cells": report}
    Path(os.environ["GOLDEN_RESULT_JSON"]).write_text(json.dumps(out, indent=1))
    dut._log.info(f"allcols probe: {n_exact}/{len(report)} integer-exact")
