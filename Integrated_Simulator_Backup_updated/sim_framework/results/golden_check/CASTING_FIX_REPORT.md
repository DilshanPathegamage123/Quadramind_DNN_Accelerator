# Casting-Scheme Fix Report — unicast / multicast / hybrid now change real off-chip traffic

**Date:** 2026-07-16 · **Branch:** `fix_casting_schemes` (on top of the layout-fix
branch `fix/rtl-findings-layout-fix`, commit `b2e7d6f`) · **Method:** Verilator
5.050 + cocotb 2.0.1, TF 2.21 goldens, 5%-of-full-scale tolerance. Every number
below is measured from a real simulation unless explicitly labelled otherwise.

## 1. Trace (verified before any code change)

Casting did not exist anywhere: `SimConfig` had no field, and the only
"cast"/"broadcast" hits in `rtl/` are SystemVerilog type-casts and WS comments.
The on-chip hardware is, however, already **multicast-shaped**, which is what a
casting knob can price on the off-chip side:

- **Weights are row-broadcast to all W columns.** One fetched `weight_data[r]`
  is written into `pe_weight[r][c]` for every column `c` in the same cycle
  (`systolic_array_os.sv`, "Connect weights from fetcher" block). One weight
  fetch physically serves **W = 8 PEs**.
- **Inputs ripple down all H rows of a column.** `input_data[c]` enters row 0
  and each PE forwards it via `activation_out → pe_activation[row+1][col]`.
  One input fetch serves **H = 8 PEs**.
- **Window overlap across columns:** the input fetcher computes
  `w = col_start + col + kw`, so adjacent columns request the same element at
  shifted kw — previously fetched redundantly once per column.

**Honest baseline finding:** the pre-change `layout_prefetcher` issued 1 read
per weight *element* (implicit dedup across the W sharing columns) plus 1 read
per input *(tuple, col)* request (overlap duplicates kept). Measured 432
beats/tile on tiny L0 — an accidental partial-dedup that matches **none** of
the three casting schemes. There is therefore no scheme whose traffic equals
the old numbers; the default (MULTICAST) legitimately shifts baseline cycles.

## 2. The change

New knob plumbed exactly like `mem_layout`:

| Stage | Change |
|---|---|
| `pysim/sim_config.py` | `casting: MULTICAST \| UNICAST \| HYBRID` (default MULTICAST) → `SIM_CASTING` |
| `rtl/pkg/sim_framework_pkg.sv` | `casting_t` enum; `CAST_MULTICAST = 0` so an undriven port defaults to baseline |
| `rtl/tops/single_dnn_top.sv` | runtime input port `casting_scheme`, wired only to the prefetcher |
| `rtl/tops/multi_dnn_top.sv` | `cfg_casting_scheme` pass-through to `single_dnn_top` |
| `rtl/memory/layout_prefetcher.sv` | issue policy per scheme (below) — the only behavioural change |
| `tb/golden/*` | `GOLDEN_CASTING` env → port; `--casting` flag on `run_golden.py`; timeout pad for unicast/hybrid runs |

Scheme semantics (consumer = PE):

- **MULTICAST** — one read per unique value. Weights: 1 read/element. Inputs:
  the per-column window walk is replaced by a dedup walk over the tile's
  unique halo footprint (`kw` pinned at 0, `col` sweeps `0..W+KW−2`), so
  window-overlap duplicates are fetched once.
- **UNICAST** — one read per consuming PE. Each weight element re-issued
  **×W** (row-broadcast consumers); each input `(tuple,col)` request re-issued
  **×H** (column-ripple consumers). Replica counters `w_rep`/`i_rep` sit
  innermost in the walk.
- **HYBRID** — weights multicast (widely-shared operand), inputs unicast.

**PE math, fetchers, and the `ext_*` compute-data path are untouched** — the
array still receives identical data, so outputs cannot change by construction
(and are shown identical below). The payload caveat from the layout fix still
applies: prefetched read data is consumed, not forwarded to the array; the
AXI traffic (addresses, bursts, handshakes, timing) is real RTL behaviour on
the real port.

## 3. The critical check: unicast replicas are distinct AXI transactions

The burst coalescer extends a run only when `cur_addr == run_last + 1`, so an
address **equal** to the previous one can never merge. Proven from the raw AR
trace (tiny L0, one OS tile, CHANNEL_MAJOR, UNICAST — measured):

```
first 12 ARs (addr, arlen): (65536,0) ×7, (65536,1), (65537,0) ×4 ...
input addr 0 trace (cycle, addr, arlen):
  (8001,0,0) (8006,0,0) (8011,0,0) (8016,0,0) (8021,0,0) (8026,0,0) (8031,0,0) (8037,0,1)
```

Each weight/input replica is its own AR handshake at a distinct cycle.
**One boundary effect, stated plainly:** the 8th replica of element *N* and
the 1st replica of element *N+1* are consecutive addresses, so they legally
share one 2-beat burst (the `(addr,1)` entries above). Reads-per-consumer is
exactly preserved — every value is transferred once per consuming PE
(8 beats per element; tile total 3,456 = 8 × 432 beats measured) — but the AR
*transaction* count is slightly below 8× the element count (3,052 vs 3,456 on
this tile, 88% single-beat). Coalescing does **not** collapse unicast toward
multicast: unicast still moves 11.3× the multicast data volume.

## 4. Correctness — unchanged across schemes (measured, 5%FS tolerance)

| Run (OS 8×8, STAMP, CHANNEL_MAJOR) | MULTICAST | UNICAST | HYBRID |
|---|---|---|---|
| tiny L0 | PASS 0.013% (288/288) | PASS 0.013% (288/288) | PASS 0.013% (288/288) |
| mnist L0 (relu) | PASS 0.009% (5408/5408) | PASS 0.009% (5408/5408) | PASS 0.009% (5408/5408) |

Fixed-point output tensors compared elementwise across schemes:
**bit-identical** in all cases (numpy array equality on `out_fixed`).

## 5. Traffic — measured whole-layer AXI numbers (all invocations)

| Layer · scheme | AR requests | beats | cycles |
|---|---|---|---|
| tiny L0 · MULTICAST | **138** | **1,836** | **5,808** |
| tiny L0 · HYBRID | **9,318** | **11,664** | **53,004** |
| tiny L0 · UNICAST | **18,312** | **20,736** | **98,130** |
| mnist L0 · MULTICAST | **832** | **10,608** | **36,712** |
| mnist L0 · HYBRID | **53,872** | **67,392** | **309,400** |
| mnist L0 · UNICAST | **105,872** | **119,808** | **570,232** |

All three schemes are **pairwise distinct on both workloads**, with multicast
fewest on every metric, unicast most, hybrid strictly between — the expected
two-sided result. (Old accidental-mix baseline for reference: tiny 2,592
beats/7,644 cycles; mnist 14,976 beats/47,320 cycles.)

**Prediction vs measured.** Per-tile beats, tiny L0: predicted 306 / 1,944 /
3,456 (MULTICAST/HYBRID/UNICAST) — measured **exactly** 306 / 1,944 / 3,456
(whole-layer ÷ 6 invocations). mnist L0: the step-1 note predicted 260 /
1,800 / 3,200 per tile using a wrong shape assumption (5×5 kernel, C=1);
mnist L0 is actually a **3×3** conv (28×28×1 → 26×26×8, so 72 weight elements,
72 input requests, 30 unique input elements per tile). With the correct shape
the same formulas give 102 / 648 / 1,152 per tile, and the measured values are
**exactly** 102 / 648 / 1,152 (whole-layer ÷ 104 invocations). The discrepancy
was an input-parameter error in the prediction, not a model or RTL mismatch.

## 6. Casting × layout — both knobs live together (measured, single tile, tiny L0)

| casting · layout | ARs | beats | avg burst | cycles |
|---|---|---|---|---|
| MULTICAST · CHANNEL | 23 | 306 | 13.30 | 968 |
| MULTICAST · ROW | 299 | 306 | 1.02 | 1,796 |
| MULTICAST · COLUMN | 299 | 306 | 1.02 | 1,796 |
| UNICAST · CHANNEL | 3,052 | 3,456 | 1.13 | 16,355 |
| UNICAST · ROW | 3,449 | 3,456 | 1.00 | 17,546 |
| UNICAST · COLUMN | 3,449 | 3,456 | 1.00 | 17,546 |
| HYBRID · CHANNEL | 1,553 | 1,944 | 1.25 | 8,834 |
| HYBRID · ROW | 1,937 | 1,944 | 1.00 | 9,986 |
| HYBRID · COLUMN | 1,937 | 1,944 | 1.00 | 9,986 |

Within every casting scheme the layout burst-structure difference survives
(CHANNEL coalesces, strided layouts degrade to single beats); within every
layout the three castings differ. tiny ROW ≡ COLUMN remains, for the reason
documented in LAYOUT_FIX_REPORT.md §5 (both strides defeat coalescing;
address sequences still differ).

## 7. Full 19/19 golden regression (default casting = MULTICAST)

All 19 cases re-run after the change — **19/19 PASS**, every error identical
to the pre-change values. Cycle counts shifted as pre-announced (MULTICAST
dedups the input halo, so memory phases got *shorter* than the accidental-mix
baseline).

| Case | verdict | max err (%FS) | cycles (was → now) |
|---|---|---|---|
| tiny L0 OS CHANNEL STAMP 8×8 | PASS | 0.013 | 7,644 → 5,808 |
| tiny L0 OS ROW STAMP 8×8 | PASS | 0.013 | 14,556 → 10,776 |
| tiny L0 OS COLUMN STAMP 8×8 | PASS | 0.013 | 14,556 → 10,776 |
| tiny L0 OS CHANNEL PAGED 8×8 | PASS | 0.013 | 5,802 |
| tiny L0 IS CHANNEL STAMP 8×8 | PASS | 0.013 | 5,220 |
| tiny L0 WS CHANNEL STAMP 8×1 | PASS | 0.013 | 122,616 |
| tiny L0 WS CHANNEL STAMP 8×2 | PASS | 0.013 | 127,062 |
| tiny L0 WS CHANNEL STAMP 8×8 | PASS | 0.013 | 225,342 → 153,738 |
| tiny L1 OS CHANNEL STAMP 8×8 | PASS | 0.017 | 11,780 |
| mnist L0 OS CHANNEL STAMP 8×8 | PASS | 0.009 | 47,320 → 36,712 |
| mnist L0 IS CHANNEL STAMP 8×8 | PASS | 0.009 | 32,136 |
| mnist L0 WS CHANNEL STAMP 8×8 | PASS | 0.009 | 226,434 |
| mnist L1 OS CHANNEL STAMP 8×8 | PASS | 0.019 | 110,176 |
| mnist L2 OS CHANNEL STAMP 8×8 | PASS | 0.050 | 162,470 |
| multi FIFO 8×8 (3 tasks) | PASS (all_pass) | — | 13,821 → 13,412 |
| multi LIFO 8×8 (3 tasks) | PASS (all_pass) | — | 13,412 |
| multi AIMT 8×8 (3 tasks) | PASS (all_pass) | — | 13,413 |
| multi BATCHDNN 8×8 (3 tasks) | PASS (all_pass) | — | 13,413 |
| multi BATCHDNN_PP 8×8 (3 tasks) | PASS (all_pass) | — | 13,413 |

## 9. Two-sided conclusion

(a) **Correctness preserved:** all three casting schemes match the TensorFlow
golden within 5% with **bit-identical fixed-point outputs** across schemes;
the full 19/19 regression is green with errors unchanged.
(b) **Behaviour now differs:** unicast, multicast, and hybrid issue genuinely
different, real off-chip traffic — pairwise distinct AR counts, beat counts,
and cycles on both workloads, with multicast fewest (tiny L0: 1,836 vs 11,664
vs 20,736 beats; mnist L0: 10,608 vs 67,392 vs 119,808 beats), and the
unicast replicas proven to be distinct AXI transactions from the raw AR trace.

## 8. Assumptions and labels

- **Measured:** every AR/beat/cycle/error number above comes from real
  Verilator runs on the real AXI port (behavioural TB responder, 1 read
  accepted per AR, `arlen+1` beats streamed).
- **Analysis parameters (not measured):** the per-tile beat *formulas* in §5
  (weights = valid_rows × C·KH·KW; inputs = C·KH·KW×W unicast-requests or
  C×KH×(W+KW−1) unique) — stated to explain the measured values, which they
  match exactly once the correct layer shapes are used.
- **Payload caveat (carried from the layout fix):** prefetched data is not
  forwarded into the array; compute data still arrives via `ext_*`. Casting
  therefore changes real off-chip traffic and memory-phase timing, never
  computed values.
- The unicast timeout pad in the TB (`12·n_tuples·H·W + 2000`) is a test
  ceiling, not a performance claim.
