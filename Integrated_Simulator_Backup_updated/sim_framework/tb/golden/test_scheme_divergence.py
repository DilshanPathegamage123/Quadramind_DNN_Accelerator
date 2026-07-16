"""STAMP-vs-PAGED divergence experiment (Member 2 golden check, step 2).

Runs the full OS tile sequence of a layer (same tiles, same compute, same
correctness collection as the golden harness) while the host programs the
memory-management engines AS DESIGNED, per tile:

STAMP (MEMORY=STAMP build):
  - The host tracks which DRAM words are already resident in the scratchpad
    and programs the delta-op metadata table before each tile:
      LOAD (op 2) for contiguous runs of NEW words  -> real AXI bursts via
        axi_read_adapter, written into the scratchpad by the engine,
      KEEP (op 0) for contiguous runs of REUSED words -> counted, no fetch.
    The engine executes during the tile's stamp phase (S_MEM).
  - After the tile, the tile footprint's scratchpad slots are replayed on
    all 4 external ports (4 concurrent readers, like array columns) so the
    banked arbitration sees real DNN access patterns -> measured conflicts.

PAGED (MEMORY=PAGED build):
  - Per tile, the tile footprint's DRAM byte addresses are replayed on
    port 0 (translation hardware): accesses to unmapped pages MISS
    (measured), mapped pages HIT (measured). After the pass the host maps
    the newly-faulted pages via pt_write.
  - The per-port page_table write was originally gated `p == 0` (plus an
    rd_addr[0] VPN match), so only port 0 could ever hit; that gate is now
    fixed (writes broadcast to all port tables) and the replay uses all 4
    ports, symmetric with the STAMP replay.

Everything recorded comes from hardware counters or the AXI responder;
host-side derivations (e.g. implied page-fetch bytes) are labelled in the
runner. Footprints use exactly the layout_prefetcher's CHANNEL_MAJOR
multicast walk formulas. Compute correctness is collected identically to
the golden harness and verified by the runner.
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

PAGE_BITS = 10   # PAGED runs are word-addressed; 2**10 words = 4 KB pages
N_PORTS = 4
MAX_OPS = 256


def _tile_footprint_words(cfg, ch_start, oh, ow0, H, W):
    """Unique DRAM word addresses (CHANNEL_MAJOR) the tile touches - the
    same element set the prefetcher's multicast walk fetches."""
    K = cfg["weight_k"]
    C, KH, KW = cfg["weight_c"], cfg["weight_kh"], cfg["weight_kw"]
    IH, IW = cfg["input_height"], cfg["input_width"]
    wbase, ibase = cfg["weight_base_addr"], cfg["input_base_addr"]
    n = C * KH * KW
    words = []
    for r in range(H):
        och = ch_start + r
        if och < K:
            words.extend(range(wbase + och * n, wbase + (och + 1) * n))
    for ch in range(C):
        for kh in range(KH):
            ih = oh + kh
            base = ibase + ch * (IH * IW) + ih * IW
            words.extend(base + ow0 + j for j in range(W + KW - 1))
    return sorted(set(words))


def _runs(words):
    """Group a sorted word list into (start, length) contiguous runs."""
    runs = []
    for w in words:
        if runs and w == runs[-1][0] + runs[-1][1]:
            runs[-1][1] += 1
        else:
            runs.append([w, 1])
    return runs


async def _program_stamp(dut, ops):
    assert len(ops) <= MAX_OPS, f"{len(ops)} delta ops > table depth"
    for i, (op, src, dst, size) in enumerate(ops):
        dut.metadata_wr_addr.value = i
        dut.metadata_wr_data.value = (op << 112) | (src << 64) | (dst << 32) | size
        dut.metadata_wr_en.value = 1
        await RisingEdge(dut.clk)
    dut.metadata_wr_en.value = 0
    dut.num_delta_ops_in.value = len(ops)
    dut.phase_base_addr_in.value = 0
    return len(ops)


async def _replay(dut, addrs, n_ports):
    """Drive addresses through the external scratchpad ports, one batch per
    cycle. Returns (cycles, served) - served counted from rd_valid."""
    served = 0
    cycles = 0
    for i in range(0, len(addrs), n_ports):
        batch = addrs[i:i + n_ports]
        for p, a in enumerate(batch):
            dut.spad_dbg_rd_addr[p].value = a
        dut.spad_dbg_rd_en.value = (1 << len(batch)) - 1
        await RisingEdge(dut.clk)
        cycles += 1
        served += bin(int(dut.spad_dbg_rd_valid.value)).count("1")
    dut.spad_dbg_rd_en.value = 0
    for _ in range(2):
        await RisingEdge(dut.clk)
        served += bin(int(dut.spad_dbg_rd_valid.value)).count("1")
    return cycles + 2, served


async def _map_page(dut, vpn, ppn):
    """PT write (post-fix: broadcasts to every port's page table)."""
    dut.pt_write_vpn.value = vpn
    dut.pt_write_ppn.value = ppn
    dut.pt_write_valid.value = 1
    dut.pt_write_en.value = 1
    await RisingEdge(dut.clk)
    dut.pt_write_en.value = 0
    dut.pt_write_valid.value = 0
    return 1


@cocotb.test()
async def scheme_divergence(dut):
    p = g._read_cfg()
    cfg = p["cfg"]
    H, W = p["array_h"], p["array_w"]
    scheme = p["memory"]          # STAMP or PAGED (build must match)

    x = np.load(p["layer_dir"] / "input.npy")
    w = np.load(p["layer_dir"] / "weights.npy")
    xq = g._quant(x, p["frac_x"])
    wq = g._quant(w, p["frac_w"])
    K = cfg["weight_k"]
    C, KH, KW = cfg["weight_c"], cfg["weight_kh"], cfg["weight_kw"]
    OH, OW = cfg["output_height"], cfg["output_width"]
    wq_stream = wq.transpose(3, 2, 0, 1).reshape(K, C * KH * KW)
    flat_in = g._flat_input(xq, "CHANNEL_MAJOR")

    cocotb.start_soon(Clock(dut.clk, 5.0, unit="ns").start())
    g._set_layer_ports(dut, cfg, g.LAYOUTS["CHANNEL_MAJOR"])
    g._zero_data_ports(dut, H, W)
    dut.start.value = 0
    await g._reset(dut)
    axi_stats = {"ar": 0, "beats": 0, "trace": []}
    cocotb.start_soon(g._axi_responder(dut, axi_stats))

    n_tuples = C * KH * KW
    base_timeout = n_tuples * (W + 1) + 800 + 3 * n_tuples * (H + W) + 600

    out_fixed = np.zeros((OH, OW, K), dtype=np.int64)
    got = np.zeros((OH, OW, K), dtype=bool)

    resident = {}          # DRAM word -> spad word slot (STAMP host model)
    spad_ptr = 0
    mapped = {}            # vpn -> ppn (PAGED host model)
    tot = {"tiles": 0, "compute_cycles": 0, "program_cycles": 0,
           "replay_cycles": 0, "replay_served": 0,
           "new_words": 0, "reused_words": 0, "load_ops": 0, "keep_ops": 0}

    for ch_start in range(0, K, H):
        wq_rows = [wq_stream[min(ch_start + r, K - 1)] for r in range(H)]
        ctx = {"H": H, "W": W, "cfg": cfg, "flat_in": flat_in,
               "wq_rows": wq_rows, "n_tuples": n_tuples}
        for oh in range(OH):
            for ow0 in range(0, OW, W):
                words = _tile_footprint_words(cfg, ch_start, oh, ow0, H, W)
                new = [a for a in words if a not in resident]
                reused = len(words) - len(new)
                tot["new_words"] += len(new)
                tot["reused_words"] += reused
                timeout = base_timeout + 6 * len(new) + 40 * MAX_OPS

                if scheme == "STAMP":
                    ops = []
                    for start, ln in _runs(new):
                        dst = spad_ptr
                        for k in range(ln):
                            resident[start + k] = dst + k
                        spad_ptr += ln
                        ops.append((2, start * 4, dst * 4, ln * 4))
                    for start, ln in _runs([a for a in words if a in resident
                                            and a not in new]):
                        ops.append((0, start * 4, resident[start] * 4, ln * 4))
                    tot["load_ops"] += sum(1 for o in ops if o[0] == 2)
                    tot["keep_ops"] += sum(1 for o in ops if o[0] == 0)
                    tot["program_cycles"] += await _program_stamp(dut, ops)
                else:
                    dut.num_delta_ops_in.value = 0
                    # demand pass: replay BEFORE mapping so new pages miss
                    # (post PT-write fix: all 4 ports, like the STAMP replay).
                    # Word-addressed vaddrs: the paged datapath applies no
                    # byte->word shift (unlike the stamp path), so word units
                    # keep the scratchpad bank stride comparable; with
                    # PAGE_SIZE_BITS=10 a page is 1,024 words = 4 KB.
                    cyc, srv = await _replay(dut, list(words), N_PORTS)
                    tot["replay_cycles"] += cyc
                    tot["replay_served"] += srv
                    for a in words:
                        vpn = a >> PAGE_BITS
                        if vpn not in mapped:
                            mapped[vpn] = len(mapped)
                            tot["program_cycles"] += await _map_page(
                                dut, vpn, mapped[vpn])
                        resident[a] = True

                res, cyc = await g._run_os_tile(dut, ctx, ch_start, oh, ow0,
                                                timeout)
                tot["compute_cycles"] += cyc
                tot["tiles"] += 1
                for (r, c), val in res.items():
                    if ch_start + r < K and ow0 + c < OW:
                        out_fixed[oh, ow0 + c, ch_start + r] = val
                        got[oh, ow0 + c, ch_start + r] = True
                for _ in range(4):
                    await RisingEdge(dut.clk)

                if scheme == "STAMP":
                    slots = sorted(resident[a] for a in words)
                    cyc, srv = await _replay(dut, slots, N_PORTS)
                    tot["replay_cycles"] += cyc
                    tot["replay_served"] += srv

    out = {
        "scheme": scheme, "layer": str(p["layer_dir"]),
        "num_banks_build": int(os.environ.get("SWEEP_NUM_BANKS", "4")),
        "totals": tot,
        "unique_pages_mapped": len(mapped),
        "axi_ar_requests": axi_stats["ar"],
        "axi_beats": axi_stats["beats"],
        "stats_loads_or_hits": int(dut.stats_loads_or_hits.value),
        "stats_moves_or_misses": int(dut.stats_moves_or_misses.value),
        "stats_keeps": int(dut.stats_keeps.value),
        "stats_bytes_loaded": int(dut.stats_bytes_loaded.value),
        "stats_bytes_moved": int(dut.stats_bytes_moved.value),
        "stats_bank_conflicts": int(dut.stats_bank_conflicts.value),
        "stats_bank_conflict_stall_cycles":
            int(dut.stats_bank_conflict_stall_cycles.value),
        "coverage": float(got.mean()),
        "out_fixed": out_fixed.reshape(1, OH, OW, K).tolist(),
    }
    Path(os.environ["GOLDEN_RESULT_JSON"]).write_text(json.dumps(out))
    assert got.all(), f"missing outputs: coverage={got.mean():.3f}"
