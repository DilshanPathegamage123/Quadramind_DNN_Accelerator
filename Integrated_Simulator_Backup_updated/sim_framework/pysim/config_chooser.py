"""Analytical configuration chooser: stationary x layout x casting.

Scores all 27 combinations of stationary scheme (OS/WS/IS) x memory layout
(ROW/COLUMN/CHANNEL_MAJOR) x casting scheme (MULTICAST/UNICAST/HYBRID) for a
workload on a fixed array + memory provision, ranks them by a user goal, and
returns the best combination plus the full ranked table.  Pure analytical --
no RTL is run per query.

Reused validated formulas (imported, not copied):
  - pysim.software_ref.estimate_cycles            (cycle RANK score -- the
      estimator ranks configurations; it does not predict absolute cycles,
      as documented in results/golden_check/GOLDEN_CHECK_SUMMARY.md sec.7)
  - scripts.run_full_eval.compute_layout_factor   (per-tensor layout penalty:
      OS->output, IS->input, WS->weight)
  - scripts.run_full_eval.DRAM_PJ_PER_BYTE / COMPUTE_PJ_PER_MAC
      (energy = offchip_bytes * 560 pJ/B + macs * 0.5 pJ * (dw/8),
       same formula as run_full_eval.sim_layer)
  - the scratchpad-fit penalty formula from run_full_eval.run_hardware_sweep
      (min_working_set vs capacity; 1 + 0.3*log2(ws/bytes + 1) when over)

Casting traffic uses the STRUCTURAL prefetcher-walk model rather than
run_full_eval._casting_traffic: it reproduces the measured RTL casting beats
exactly (tiny L0 1,836/11,664/20,736 and mnist L0 10,608/67,392/119,808 --
CASTING_FIX_REPORT.md sec.5), and its per-tile terms are the formulas stated
in that report's sec.8:
    weights  (multicast) = valid_rows * C*KH*KW      per tile
    inputs   (multicast) = C*KH*(W+KW-1)             per tile (halo dedup)
    weights  (unicast)   = multicast * W             (row-broadcast consumers)
    inputs   (unicast)   = C*KH*KW * W * H           (one read per consuming PE)
    hybrid               = weights multicast + inputs unicast
Cross-checked at other array widths against the measured WS 8x1/8x2/8x8 runs
(input-halo term scales exactly as C*KH*(W+KW-1); weight term W-invariant).

Known model-vs-hardware divergence (documented, do not hide): the analytical
layout factor varies traffic VOLUME by layout, while the measured RTL moves an
identical beat volume in every layout and instead changes AR-request count and
cycles (coalescing).  Layout ordering agrees (CHANNEL_MAJOR best for OS);
the per-layout traffic deltas are model values, not measured ones.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from pysim.sim_config import LayerConfig
from pysim.software_ref import estimate_cycles

DATAFLOWS = ["OS", "WS", "IS"]
LAYOUTS = ["ROW_MAJOR", "COLUMN_MAJOR", "CHANNEL_MAJOR"]
CASTINGS = ["MULTICAST", "UNICAST", "HYBRID"]
GOALS = ["offchip", "latency", "energy", "weighted"]

_LAYOUT_ABBR = {"ROW_MAJOR": "RM", "COLUMN_MAJOR": "CM", "CHANNEL_MAJOR": "ChM"}


def _layout_penalty(dataflow: str, layout: str, layer: LayerConfig) -> float:
    """Per-tensor layout penalty, re-based from compute_layout_factor.

    compute_layout_factor returns a factor f over the whole base traffic
    (wt+it+ot) with the penalty applied to one tensor:
        f = (tot - aff + aff*(1+pen)) / tot   =>   pen = (f-1)*tot/aff
    Extracting pen lets us apply it to the casting-adjusted tensor instead of
    the base one, so layout and casting compose without double counting.
    """
    from scripts.run_full_eval import compute_layout_factor
    wt = float(layer.weight_k * layer.weight_c * layer.weight_kh * layer.weight_kw)
    it = float(layer.input_channels * layer.input_height * layer.input_width)
    ot = float(layer.weight_k * layer.output_height * layer.output_width)
    tot = wt + it + ot
    aff = {"OS": ot, "IS": it, "WS": wt}[dataflow]
    if tot == 0 or aff == 0:
        return 0.0
    f = compute_layout_factor(dataflow, layout, layer)
    return (f - 1.0) * tot / aff


def _cast_tile(wt_mc: float, it_mc: float, it_uc: float, array_w: int,
               casting: str) -> tuple[float, float]:
    """Apply the casting replication semantics to one tile/invocation."""
    if casting == "MULTICAST":
        return wt_mc, it_mc
    if casting == "UNICAST":
        return wt_mc * array_w, it_uc
    if casting == "HYBRID":
        return wt_mc, it_uc
    raise ValueError(casting)


def prefetch_traffic(layer: LayerConfig, array_h: int, array_w: int,
                     casting: str, dataflow: str = "OS") -> Dict[str, float]:
    """Whole-layer prefetch traffic (elements == AXI beats) per the structural
    prefetcher walk, now dataflow-aware.

    OS/IS run the tile walk ceil(K/H) x OH x ceil(OW/W) (measured identical:
    1,836 beats / 6 invocations on tiny L0 and 10,608 / 104 on mnist L0 for
    both dataflows).  WS runs one prefetcher walk per harness invocation over
    the diagonal tiling of the (output-row, channel) grid -- the loop
    structure of _harness_ws in tb/golden/test_golden_single.py:
        for d in [-(OH-1), K): for oh0 blocks (step H): for ow: for c_in
    with per-invocation weights = valid_rows*n and input halo
    C*KH*(W+KW-1).  Zero fitted constants; validated EXACTLY against all
    four measured WS runs (tiny 8x1/8x2/8x8: 43,254 / 45,360 / 57,996
    beats, 234 invocations; mnist 8x8: 80,964 beats, 858 invocations).
    Casting factors apply per invocation as in the tile walk (measured WS
    runs are MULTICAST; unicast/hybrid replication is the 8x8-confirmed
    prefetcher semantics)."""
    K, C = layer.weight_k, layer.weight_c
    KH, KW = layer.weight_kh, layer.weight_kw
    OH, OW = layer.output_height, layer.output_width
    n = C * KH * KW
    it_mc = C * KH * (array_w + KW - 1)          # input halo, deduped
    it_uc = n * array_w * array_h                # 1 read per consuming PE

    wt_elems = 0.0
    it_elems = 0.0
    n_inv = 0
    if dataflow == "WS":
        for d in range(-(OH - 1), K):
            oh_lo, oh_hi = max(0, -d), min(OH, K - d)
            if oh_hi <= oh_lo:
                continue
            for oh0 in range(oh_lo, oh_hi, array_h):
                valid_rows = min(array_h, K - (oh0 + d))
                wt_t, it_t = _cast_tile(valid_rows * n, it_mc, it_uc,
                                        array_w, casting)
                wt_elems += wt_t * OW * C
                it_elems += it_t * OW * C
                n_inv += OW * C
    else:                                        # OS and IS: tile walk
        tiles_per_rowblock = OH * math.ceil(OW / array_w)
        for ch_start in range(0, K, array_h):
            valid_rows = min(array_h, K - ch_start)
            wt_t, it_t = _cast_tile(valid_rows * n, it_mc, it_uc,
                                    array_w, casting)
            wt_elems += wt_t * tiles_per_rowblock
            it_elems += it_t * tiles_per_rowblock
            n_inv += tiles_per_rowblock
    return {"weight_elems": wt_elems, "input_elems": it_elems,
            "beats": wt_elems + it_elems, "tiles": n_inv}


def _mem_fit_penalty(layer: LayerConfig, mem_bytes: int, dw: int) -> float:
    """Scratchpad-fit traffic penalty (formula from
    run_full_eval.run_hardware_sweep, expressed with capacity in bytes)."""
    wt = layer.weight_k * layer.weight_c * layer.weight_kh * layer.weight_kw
    it = layer.input_channels * layer.input_height * layer.input_width
    ot = layer.output_channels * layer.output_height * layer.output_width
    spad_words = mem_bytes // (dw // 8)
    min_working_set = (min(wt, spad_words // 2) + min(it, spad_words // 2)
                       + min(ot, spad_words // 4)) * (dw // 8)
    if min_working_set <= mem_bytes:
        return 1.0
    return 1.0 + 0.3 * math.log2(min_working_set / mem_bytes + 1)


@dataclass
class ConfigScore:
    dataflow: str
    layout: str
    casting: str
    offchip_elements: float      # primary ranking metric (model)
    offchip_bytes: float
    latency_rank: float          # RANK score, not a cycle prediction
    energy_pJ: float
    macs: float
    prefetch_beats: float        # casting-affected, structural (RTL-anchored)
    weighted: float = float("nan")

    @property
    def label(self) -> str:
        return f"{self.dataflow}-{_LAYOUT_ABBR[self.layout]}-{self.casting[:2]}"


def score_config(layers: List[LayerConfig], array_h: int, array_w: int,
                 mem_bytes: int, dataflow: str, layout: str, casting: str,
                 data_width: int = 16) -> ConfigScore:
    """Score one (dataflow, layout, casting) combination over all layers.

    offchip_elements: weight/input prefetch elements per the structural
      casting walk + output writeback, with the layout penalty applied to the
      dataflow-affected tensor and the memory-fit penalty on the total.
    latency_rank: sum(estimate_cycles * layout_factor) + prefetch beats
      (each beat occupies the single AXI read-data port for one cycle).
      Ordering-only, per the documented estimator fidelity.
    energy_pJ: offchip bytes * DRAM_PJ_PER_BYTE + macs * COMPUTE_PJ_PER_MAC
      * (dw/8) -- same formula as run_full_eval.sim_layer.
    """
    from scripts.run_full_eval import (DRAM_PJ_PER_BYTE, COMPUTE_PJ_PER_MAC,
                                       compute_layout_factor)
    dw = data_width
    offchip = 0.0
    latency = 0.0
    macs = 0.0
    beats_total = 0.0
    for layer in layers:
        pf = prefetch_traffic(layer, array_h, array_w, casting, dataflow)
        wt, it = pf["weight_elems"], pf["input_elems"]
        ot = float(layer.weight_k * layer.output_height * layer.output_width)
        pen = _layout_penalty(dataflow, layout, layer)
        if dataflow == "OS":
            ot *= (1.0 + pen)
        elif dataflow == "IS":
            it *= (1.0 + pen)
        elif dataflow == "WS":
            wt *= (1.0 + pen)
        layer_elems = (wt + it + ot) * _mem_fit_penalty(layer, mem_bytes, dw)
        offchip += layer_elems
        f_layout = compute_layout_factor(dataflow, layout, layer)
        latency += (estimate_cycles(layer, dataflow, array_h, array_w)
                    * f_layout) + pf["beats"]
        macs += (layer.weight_k * layer.weight_c * layer.weight_kh
                 * layer.weight_kw * layer.output_height * layer.output_width)
        beats_total += pf["beats"]
    offchip_bytes = offchip * (dw // 8)
    energy = (offchip_bytes * DRAM_PJ_PER_BYTE
              + macs * COMPUTE_PJ_PER_MAC * (dw / 8.0))
    return ConfigScore(dataflow, layout, casting, offchip, offchip_bytes,
                       latency, energy, macs, beats_total)


def goal_value(score: ConfigScore, goal: str) -> float:
    """The metric a given goal ranks on."""
    return {"offchip": score.offchip_elements, "latency": score.latency_rank,
            "energy": score.energy_pJ, "weighted": score.weighted}[goal]


def ties_at_best(ranked: List[ConfigScore], goal: str) -> List[ConfigScore]:
    """All configurations exactly tied with the winner on the goal metric."""
    best = goal_value(ranked[0], goal)
    return [s for s in ranked if goal_value(s, goal) == best]


def rank_configs(layers: List[LayerConfig], array_h: int, array_w: int,
                 mem_bytes: int, goal: str = "offchip",
                 weights: Optional[Dict[str, float]] = None,
                 data_width: int = 16) -> List[ConfigScore]:
    """Exhaustively score all 27 combinations and return them ranked (best
    first) by `goal`: offchip | latency | energy | weighted.

    Tie-break rule (deliberate, documented): configurations exactly tied on
    the goal metric are ordered by latency rank, then energy — never by
    enumeration order.  Exact ties are real model behaviour ({OS-ChM, WS-CM,
    IS-RM} score identically on off-chip traffic at equal casting); use
    ties_at_best() to surface them to the user.
    """
    if goal not in GOALS:
        raise ValueError(f"goal must be one of {GOALS}, got {goal!r}")
    scores = [score_config(layers, array_h, array_w, mem_bytes, df, ly, ca,
                           data_width)
              for df in DATAFLOWS for ly in LAYOUTS for ca in CASTINGS]

    # weighted: normalise each metric by its best (min) so best == 1.0,
    # then take the weighted sum.
    w = {"offchip": 1.0, "latency": 1.0, "energy": 1.0}
    if weights:
        w.update(weights)
    mins = {k: min(getattr(s, a) for s in scores)
            for k, a in [("offchip", "offchip_elements"),
                         ("latency", "latency_rank"),
                         ("energy", "energy_pJ")]}
    for s in scores:
        s.weighted = (w["offchip"] * s.offchip_elements / mins["offchip"]
                      + w["latency"] * s.latency_rank / mins["latency"]
                      + w["energy"] * s.energy_pJ / mins["energy"])

    return sorted(scores, key=lambda s: (goal_value(s, goal),
                                         s.latency_rank, s.energy_pJ))


def choose(layers: List[LayerConfig], array_h: int, array_w: int,
           mem_bytes: int, goal: str = "offchip",
           weights: Optional[Dict[str, float]] = None,
           data_width: int = 16) -> tuple[ConfigScore, List[ConfigScore], float]:
    """Return (best, ranked_table, elapsed_seconds)."""
    t0 = time.perf_counter()
    ranked = rank_configs(layers, array_h, array_w, mem_bytes, goal, weights,
                          data_width)
    return ranked[0], ranked, time.perf_counter() - t0
