"""Pure-Python software reference for the systolic-array simulator.

Why this exists: the unified RTL framework requires Verilator+cocotb to run
the actual hardware simulation. Where those tools are not present, this
reference computes the bit-accurate (Qm.n) conv2d output the hardware should
produce, plus an analytical cycle estimate per (dataflow, array) combo.
Tests that only need the *functional* output can use this; tests that exercise
real RTL paths still need Verilator.

The cycle estimates are upper-bound conservative -- they match the FSM
state sequence of each per-flavor top:
    OS:  fill + (K * out_h * out_w / array_w) + drain + writeback
    IS:  load_inputs + ch*kh*kw * stream + drain + writeback
    WS:  load_weights + K * out_h * out_w + drain + writeback

Bank conflict estimation (software_ref only):
    Uses the birthday-problem probability for random accesses as a lower bound.
    Structured DNN access patterns (poor loop order + layout mismatch) produce
    higher conflict rates than this estimate.  Use the RTL simulation for
    cycle-exact conflict counts (stats_bank_conflicts,
    stats_bank_conflict_stall_cycles exported by mem_backend_wrap).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

import numpy as np

from .quantize import calibrate_per_tensor, float_to_fixed, fixed_to_float
from .sim_config import LayerConfig, SimConfig


@dataclass
class SoftRefResult:
    output: np.ndarray         # float NHWC
    output_fixed: np.ndarray   # quantized (signed integer dtype)
    output_frac_bits: int
    cycles: int
    bytes_loaded: int
    stats: dict


def conv2d_fixed_point(x: np.ndarray, w: np.ndarray,
                       total_bits: int, frac_bits_x: int, frac_bits_w: int,
                       accum_bits: int = 48) -> tuple[np.ndarray, int]:
    """Q m.n conv: quantize x,w, do MAC in 64-bit, requantize back to total_bits.

    Returns (fixed_output, output_frac_bits). The output frac_bits is
    frac_bits_x + frac_bits_w (the natural growth from multiplication).
    """
    xq = float_to_fixed(x, total_bits, frac_bits_x).astype(np.int64)
    wq = float_to_fixed(w, total_bits, frac_bits_w).astype(np.int64)
    # x: (N, H, W, C_in)  w: (kH, kW, C_in, C_out)
    N, H, W, Cin = xq.shape
    kH, kW, _, Cout = wq.shape
    out_H, out_W = H - kH + 1, W - kW + 1
    out = np.zeros((N, out_H, out_W, Cout), dtype=np.int64)
    for n in range(N):
        for kr in range(kH):
            for kc in range(kW):
                for ci in range(Cin):
                    # broadcast multiply-accumulate
                    out += (
                        xq[n:n+1, kr:kr+out_H, kc:kc+out_W, ci:ci+1]
                        * wq[kr, kc, ci, :][np.newaxis, np.newaxis, np.newaxis, :]
                    )
    # Saturate to accum_bits then requantize back to total_bits @ (frac_x+frac_w)
    out_frac_bits = frac_bits_x + frac_bits_w
    # Down-shift to match total_bits range
    int_max = (1 << (total_bits - 1)) - 1
    int_min = -(1 << (total_bits - 1))
    out = np.clip(out, int_min, int_max)
    if total_bits <= 32:
        out = out.astype(np.int32)
    else:
        out = out.astype(np.int64)
    return out, out_frac_bits


def estimate_bank_conflicts(cycles: int, n_ports: int,
                            num_banks: int) -> tuple[int, int]:
    """Birthday-problem estimate of bank conflict events and stall port-cycles.

    Models N_PORTS simultaneous read requests each going to one of NUM_BANKS
    banks with uniform probability (random-access assumption).  Structured DNN
    access patterns deviate from this; the RTL simulation gives exact figures.

    Returns:
        (conflict_cycles, stall_port_cycles)
        conflict_cycles      -- estimated cycles where ≥1 port is stalled
        stall_port_cycles    -- sum of stalled-port counts over all conflict cycles
                               (equals stats_bank_conflict_stall_cycles in RTL)
    """
    if num_banks <= 1 or n_ports <= 1:
        return 0, 0

    # P(all N ports land in distinct banks) -- birthday-problem complement
    p_clean = 1.0
    for k in range(n_ports):
        p_clean *= max(0.0, (num_banks - k) / num_banks)
    p_any_conflict = 1.0 - p_clean

    # Fraction of cycles where all ports are actively reading (conservative 70%)
    active_cycles = int(cycles * 0.70)
    conflict_cycles = int(active_cycles * p_any_conflict)

    # E[stalled ports per conflict cycle] = n - E[distinct banks hit]
    # E[distinct banks] = num_banks * (1 - (1 - 1/num_banks)^n_ports)
    e_distinct = num_banks * (1.0 - (1.0 - 1.0 / num_banks) ** n_ports)
    avg_stalled = max(0.0, n_ports - e_distinct)
    stall_port_cycles = int(conflict_cycles * avg_stalled)

    return conflict_cycles, stall_port_cycles


def estimate_cycles(layer: LayerConfig, dataflow: str,
                    array_h: int, array_w: int) -> int:
    K, C = layer.weight_k, layer.weight_c
    kH, kW = layer.weight_kh, layer.weight_kw
    oh, ow = layer.output_height, layer.output_width
    if dataflow == "OS":
        macs_per_pe = math.ceil(oh * ow / (array_h * array_w))
        return 5 + array_h + array_w + macs_per_pe * (C * kH * kW)
    if dataflow == "IS":
        return 5 + (oh * ow) + C * kH * kW * math.ceil(K / array_h)
    if dataflow == "WS":
        loads = math.ceil(K / array_h) * math.ceil(C * kH * kW / array_w)
        return 5 + loads + oh * ow * C
    raise ValueError(dataflow)


def run_software_ref(cfg: SimConfig) -> SoftRefResult:
    """Compute the bit-accurate output for cfg.layers[0] (first layer only)."""
    if not cfg.layers:
        raise ValueError("SimConfig has no layers")
    layer = cfg.layers[0]
    rng = np.random.default_rng(cfg.seed)
    x = rng.standard_normal((1, layer.input_height, layer.input_width,
                             layer.input_channels)).astype(np.float32)
    w = rng.standard_normal((layer.weight_kh, layer.weight_kw,
                             layer.weight_c, layer.weight_k)).astype(np.float32)
    fb_x = calibrate_per_tensor(x, cfg.fp_total_bits)
    fb_w = calibrate_per_tensor(w, cfg.fp_total_bits)
    out_fixed, out_frac = conv2d_fixed_point(
        x, w, cfg.fp_total_bits, fb_x, fb_w, cfg.accum_width,
    )
    out_float = fixed_to_float(out_fixed, out_frac)
    cycles = estimate_cycles(layer, cfg.dataflow, cfg.array_height, cfg.array_width)
    bytes_loaded = (
        layer.input_channels * layer.input_height * layer.input_width
        + layer.weight_k * layer.weight_c * layer.weight_kh * layer.weight_kw
    ) * (cfg.data_width // 8)

    bc_cycles, bc_stall_port_cycles = estimate_bank_conflicts(
        cycles, cfg.n_mem_ports, cfg.num_banks,
    )

    return SoftRefResult(
        output=out_float,
        output_fixed=out_fixed,
        output_frac_bits=out_frac,
        cycles=cycles,
        bytes_loaded=bytes_loaded,
        stats={
            "weight_reuse":    float(layer.output_height * layer.output_width),
            "input_reuse":     float(layer.weight_k),
            "weight_traffic":  float(layer.weight_k * layer.weight_c *
                                     layer.weight_kh * layer.weight_kw),
            "input_traffic":   float(layer.input_channels * layer.input_height *
                                     layer.input_width),
            "output_traffic":  float(layer.output_channels * layer.output_height *
                                     layer.output_width),
            "bytes_loaded":    bytes_loaded,
            # Bank conflict estimates (analytical; RTL gives exact values)
            "num_banks":                      cfg.num_banks,
            "bank_conflict_cycles_est":       bc_cycles,
            "bank_conflict_stall_ports_est":  bc_stall_port_cycles,
            "backend":                        "software_ref",
        },
    )
