# Memory-Layout Fix Report — layout now changes real off-chip traffic

**Date:** 2026-07-15 · **Branch:** `fix/rtl-findings-layout-fix` (commit `8c01c3e`,
on top of the F1–F8 branch) · **Method:** Verilator 5.050 + cocotb 2.0.1, TF 2.21
goldens, 5%-of-full-scale tolerance. Every number below is measured from a real
simulation unless explicitly labelled an analysis parameter.

## 1. Root cause (probe-verified before any change)

The layout knob was *not* ignored where expected. Tracing
`SimConfig.mem_layout` → `SIM_LAYOUT` → `mem_layout` port →
`systolic_array_wrap` → fetchers → address generators showed the three
layouts already emit **different address sequences** on the array's memory
ports (measured: first col-0 input addresses ROW `0,3,6,24,…`, COLUMN
`0,24,48,3,…`, CHANNEL `0,1,2,8,…`; weight and output addresses also differ
pairwise). Two collapse points made all *measured behaviour* identical anyway:

1. **The off-chip path carried zero traffic.** `single_dnn_top` ties the
   memory backend's data plane off (`be_rd_en='0`, the "v1 wiring") and the
   array reads from the testbench's flat behavioural memory via the `ext_*`
   ports. The AXI/DRAM port issued **0 reads under every layout** (measured),
   and `grep layout rtl/memory/` is empty — the off-chip side was layout-blind.
2. **Request order and rate are layout-invariant.** The fetcher loops iterate
   `ch→kh→kw→col` at one request/cycle regardless of layout; the TB memory
   answers any address with fixed latency → identical cycles (285/tile) and
   bit-identical outputs.

Baseline probe (one identical OS tile, tiny_cnn L0):

| before fix | ROW | COLUMN | CHANNEL |
|---|---|---|---|
| cycles | 285 | 285 | 285 |
| off-chip (AXI) reads | 0 | 0 | 0 |

## 2. The change

New **`rtl/memory/layout_prefetcher.sv`**: during the memory phase it walks
the layer's weight tile (r→c→kh→kw) and input tile (ch→kh→kw→col) through the
**same layout-dependent offset formulas the fetchers use**, coalesces
consecutive addresses into AXI bursts (up to 16 beats), and issues **real AXI
read requests** with full AR/R handshakes. `single_dnn_top` sequences
`S_MEM` as *stamp phase → prefetch → compute*, shares the AXI port through a
fixed-priority mux, and asserts `phase_mem_done` when the prefetch completes
(so DNN-aware schedulers see the real, layout-dependent memory-phase length).
The PE arrays, fetchers' compute behaviour, and the `ext_*` data path are
untouched. The testbench gained a behavioural AXI responder (accepts AR,
streams `arlen+1` beats) and AR-trace recording.

**Payload caveat (agreed upfront, do not overclaim):** the prefetched read
data is consumed by the prefetcher but **not forwarded into the array** — the
compute data still arrives via the `ext_*` ports. The AXI traffic
(addresses, bursts, handshakes, timing) is real RTL behaviour on the real
port; making the array consume DRAM data through the scratchpad (removing
the v1 wiring) is a separate, larger integration step.

## 3. Correctness — unchanged (measured, 5%FS tolerance)

| Run | before fix | after fix |
|---|---|---|
| tiny L0 · CHANNEL | PASS 0.013% | PASS **0.013%** |
| tiny L0 · ROW | PASS 0.013% | PASS **0.013%** |
| tiny L0 · COLUMN | PASS 0.013% | PASS **0.013%** |
| mnist L0 · CHANNEL | PASS 0.009% | PASS **0.009%** |
| mnist L0 · ROW | PASS 0.009% | PASS **0.009%** |
| mnist L0 · COLUMN | PASS 0.009% | PASS **0.009%** |

Full regression: **19/19 PASS**, every error identical to the pre-fix values.
Cycle counts across the suite now include the layout-dependent memory phase
(e.g. WS re-prefetches its window per invocation: tiny WS 8×8 10,062 →
225,342 cycles; multi-DNN mix 3,354 → 13,821 — all still PASS).

## 4. Traffic — now genuinely differs per layout (measured)

Whole-layer runs (all invocations), from the real AXI port:

| Layer · layout | AR requests | beats | cycles | before fix |
|---|---|---|---|---|
| tiny L0 · CHANNEL | **246** | 2,592 | **7,644** | 0 ARs · 1,710 cyc |
| tiny L0 · ROW | **2,550** | 2,592 | **14,556** | 0 ARs · 1,710 cyc |
| tiny L0 · COLUMN | **2,550** | 2,592 | **14,556** | 0 ARs · 1,710 cyc |
| mnist L0 · CHANNEL | **1,456** | 14,976 | **47,320** | 0 ARs · 12,792 cyc |
| mnist L0 · ROW | **1,456** | 14,976 | **47,320** | 0 ARs · 12,792 cyc |
| mnist L0 · COLUMN | **14,248** | 14,976 | **85,696** | 0 ARs · 12,792 cyc |

Single-tile probe (burst structure + first bursts):

| tile · layout | ARs | avg burst | first bursts (addr,len) |
|---|---|---|---|
| tiny · CHANNEL | 41 | 10.54 | (65536,15)(65552,15)… |
| tiny · ROW | 425 | 1.02 | (65536,0)(65539,0)(65542,0)… |
| tiny · COLUMN | 425 | 1.02 | (65536,0)(65545,0)(65554,0)… |
| mnist · CHANNEL | 14 | 10.29 | contiguous 16-beat bursts |
| mnist · ROW | 14 | 10.29 | identical to CHANNEL (see §5) |
| mnist · COLUMN | 137 | 1.05 | single-beat, w-major stride |

"DRAM rows touched" at a **256-words/row assumption (analysis parameter, not
a measurement)**: 2 rows for every layout on these tiles — the per-tile
address footprint (~432 words) is too small to spread across 256-word rows;
the addresses themselves (measured) are what differ. On larger tensors the
row-touch counts would diverge; we do not report extrapolated numbers.

## 5. Pairs that legitimately remain identical — stated plainly

- **tiny L0: ROW vs COLUMN** — same AR count/cycles because *both* strides
  (C=3 for row-major, H·C=24 / KH·C=9 for column-major) defeat burst
  coalescing entirely: every element becomes a single-beat burst, so the
  burst structure is identical. The **address sequences are measured
  different** (`+3` steps vs `+9/+24` steps) — with a bank/row-sensitive
  DRAM model the two would cost differently; with a flat-latency responder
  they cost the same.
- **mnist L0: ROW vs CHANNEL** — mathematically inherent: with C=1 input
  channels, row-major `(h,w,c)` and channel-major `(c,h,w)` describe the
  *same* linear storage order, so identical traffic is the correct outcome,
  not a bug.

## 6. Two-sided conclusion

(a) **Correctness preserved:** all three layouts match the TensorFlow golden
within 5% (measured errors identical to pre-fix, 19/19 regression green).
(b) **Behaviour now differs:** the layouts issue different, real off-chip
address/burst sequences with different AR counts and cycle costs
(CHANNEL ≈ 10× fewer AR requests and ~2× fewer memory-phase cycles than the
strided layouts on these workloads), whereas before the fix the off-chip
port was silent (0 reads) and cycles were identical under every layout.

Follow-on ideas (not implemented): a bank/row-aware AXI responder to
differentiate equal-burst-structure layouts by latency, and the full
DRAM→scratchpad→array data-plane integration.
