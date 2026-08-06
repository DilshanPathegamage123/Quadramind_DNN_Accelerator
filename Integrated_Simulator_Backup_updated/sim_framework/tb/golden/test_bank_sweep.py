"""Bank-conflict sweep exerciser (Member 2 golden check, step 1 plumbing demo).

Drives the DUT's external scratchpad read ports (spad_dbg_*) with fixed,
interpretable access patterns for a 200-cycle window each, and reads the
REAL hardware conflict counters (scratchpad_ram arbitration) before/after.
The DUT FSM is never started: this measures the memory side only.

Patterns (addresses per port p = 0..3, held for the window):
  same_addr   : all ports read 0            -> same bank for any NUM_BANKS>1
  consecutive : port p reads p              -> distinct banks when NUM_BANKS>=4
  stride4     : port p reads 4*p            -> all one bank at NUM_BANKS<=4,
                pairs at 8, conflict-free at 16
  stride8     : port p reads 8*p            -> pairs at NUM_BANKS<=8 (mod 16:
                0,8,0,8), conflict-free only when 4*8 distinct mod NUM_BANKS
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

import test_golden_single as g

WINDOW = 200
N_PORTS = 4

PATTERNS = {
    "same_addr":   [0, 0, 0, 0],
    "consecutive": [0, 1, 2, 3],
    "stride4":     [0, 4, 8, 12],
    "stride8":     [0, 8, 16, 24],
}


@cocotb.test()
async def bank_sweep(dut):
    p = g._read_cfg()
    cfg = p["cfg"]
    H, W = p["array_h"], p["array_w"]

    cocotb.start_soon(Clock(dut.clk, 5.0, unit="ns").start())
    g._set_layer_ports(dut, cfg, g.LAYOUTS[p["layout"]])
    g._zero_data_ports(dut, H, W)
    dut.start.value = 0
    await g._reset(dut)

    out = {"num_banks_build": int(os.environ.get("SWEEP_NUM_BANKS", "-1")),
           "window_cycles": WINDOW, "patterns": {}}

    for name, addrs in PATTERNS.items():
        c0 = int(dut.stats_bank_conflicts.value)
        s0 = int(dut.stats_bank_conflict_stall_cycles.value)
        served = 0
        for i in range(N_PORTS):
            dut.spad_dbg_rd_addr[i].value = addrs[i]
        dut.spad_dbg_rd_en.value = (1 << N_PORTS) - 1
        for _ in range(WINDOW):
            await RisingEdge(dut.clk)
            served += bin(int(dut.spad_dbg_rd_valid.value)).count("1")
        dut.spad_dbg_rd_en.value = 0
        for _ in range(4):
            await RisingEdge(dut.clk)
        out["patterns"][name] = {
            "conflict_cycles": int(dut.stats_bank_conflicts.value) - c0,
            "stall_port_cycles": int(dut.stats_bank_conflict_stall_cycles.value) - s0,
            "reads_served": served,
        }

    Path(os.environ["GOLDEN_RESULT_JSON"]).write_text(json.dumps(out))
    dut._log.info("bank sweep complete")
