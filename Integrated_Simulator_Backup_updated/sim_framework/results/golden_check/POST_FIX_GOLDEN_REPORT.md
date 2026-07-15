# Post-Fix Golden-Reference Report — RTL findings F1–F8 resolved

**Date:** 2026-07-15 · **Branch:** `fix/rtl-findings` (7 commits on top of `main`)
**Method:** identical to the baseline report — Verilator 5.050 + cocotb 2.0.1,
TF 2.21 goldens, tolerance 5% of full scale, every number measured from a real
simulation. Baseline reference: `FULL_SIMULATOR_GOLDEN_REPORT.md` (re-run and
reproduced exactly before any fix was applied).

## Final regression: 19/19 configurations PASS

All errors are unchanged from baseline (pure Q14 quantization) — the fixes
changed *which configurations can compute* and *how fast*, never the values
of anything that already passed.

## Before / after by finding

| Finding | Fix (commit) | Evidence before | Evidence after |
|---|---|---|---|
| **F1** `pe_enable/pe_clear <= '{default:1'bX}` on packed arrays enabled only column 0 | `'1`/`'0` at 14 sites in OS+WS tops (`821114c`) | WS 8×2/8×8 all-zero (100% err); all-cols probe 8/48 exact | WS 8×2 PASS 0.013%; probe cols enabled (arith exposed F8) |
| **F8** *(new)* PE accumulator folded in `psum_in` → prefix-sum corruption in every column/row off the boundary | product/psum split in all three PEs (`5dddd52`, part of `e6f4597`, `20abccc`) | all-cols probe 8/48 → 30/48 (diagonal cut = F5) | probe **48/48 integer-exact** |
| **F5** OS `pe_enable` dropped while the last diagonal wavefront was in flight | drain window (H+W+4) before WRITEBACK (`fc7e3dd`) | natural schedule dropped last row's final MAC (tiny_00 ch7, 36/36 pixels matched drop-last model) | natural schedule passes; probe 48/48; **workaround removed** |
| **F2** WS output (rightmost column) structurally zero for width > 1 | WS drain window (W+6) + WS-PE psum split (`e6f4597`) | WS 8×2: 100% / 8×8: 100% | WS 8×2 **PASS 0.013%**, 8×8 **PASS 0.013%**, mnist 8×8 **PASS 0.009%** |
| **F3** IS: one MAC per pass (3-cycle enable window; stationary register not reloadable) | reload during streaming + enable across the weight loop + DRAIN state + IS-PE psum/gating split (`20abccc`) | tiny_00: 7,776 invocations / 1,337,472 cycles, TB summed tuples | tiny_00: **6 invocations / 1,122 cycles**, full conv in hardware (≈1,190× fewer cycles) |
| **F4** IS final input-load window ignored data responses | `idx_valid` extended through DONE in `input_fetcher_is` (`20abccc`) | probe: t_load=26 never latched (26/27) | probe: **27/27 latch reactively**; predictive-serve **workaround removed** |
| **F6** DNN-aware scheduler select decoded `select[1:0]` (off by 11) | `2'(select - 5'd11)` in `unified_scheduler_wrapper` (`0527937`) | AI-MT unusable at 11; ran at 12/13/14 | canonical **11/12/13** work; test compensation **removed** |
| **F7** scheduler queues multi-driven (same-edge enqueue lost); AI-MT balance never admitted a first MT with real `mem_cycles` | single-owner queue updates w/ enqueue/pop flags (AI-MT: mt/ct/sct; BatchDNN: mt; BatchDNN++: mt incl. expedite arbitration) + `compute_cycle_ctr==0` bootstrap (`cd53743`) | required 10-cycle write spacing + `st_mem_cycles=0` | back-to-back writes, `mem_cycles=50`: all 5 schedulers PASS; both **workarounds removed** |

## Full post-fix results (all real Verilator runs, 5%FS tolerance)

| Configuration | Verdict | Max err %FS | Invocations (was) | RTL cycles (was) | Assembly now |
|---|---|---|---|---|---|
| tiny_cnn L0 · OS 8×8 | PASS | 0.013 | 6 (36) | 1,710 (9,504) | hardware, full array |
| tiny_cnn L1 · OS 8×8 | PASS | 0.017 | 1 (1) | 2,634 (2,613) | hardware |
| mnist L0 · OS 8×8 | PASS | 0.009 | 104 (676) | 12,792 (68,952) | hardware, full array |
| mnist L1 · OS 8×8 | PASS | 0.019 | 44 (242) | 30,360 (161,898) | hardware, full array |
| mnist L2 · OS 8×8 | PASS | 0.050 | 2 (2) | 34,932 (34,890) | hardware |
| tiny L0 · OS ROW/COLUMN | PASS ×2 | 0.013 | 6 | 1,710 | bit-identical to CHANNEL |
| tiny L0 · OS PAGED | PASS | 0.013 | 6 | 1,704 | identical outputs |
| tiny L0 · IS 8×8 | PASS | 0.013 | 6 (7,776) | 1,122 (1,337,472) | **hardware full conv** (was 1 MAC/pass) |
| mnist L0 · IS 8×8 | PASS | 0.009 | 104 (—) | 8,216 (—) | new capability |
| tiny L0 · WS 8×1 | PASS | 0.013 | 234 (864) | 8,424 (24,192) | per-channel windows in HW |
| tiny L0 · WS 8×2 | **PASS (was FAIL)** | 0.013 | 234 | 8,658 | diagonal tiles in HW |
| tiny L0 · WS 8×8 | **PASS (was FAIL)** | 0.013 | 234 | 10,062 | diagonal tiles in HW |
| mnist L0 · WS 8×8 | PASS | 0.009 | 858 (—) | 36,894 (—) | new capability |
| multi ×5 schedulers | PASS ×5 | ≤0.017 | 3 tasks each | ~3,353 | canonical selects, no workarounds |

## Workarounds removed from the harness

1. OS "stream 2 cycles early" (F5) — natural schedule everywhere, incl. multi-DNN.
2. IS "serve final tuple predictively one window early" (F4) — reactive now.
3. IS testbench tuple-summing (F3) — the hardware accumulates the full conv.
4. Multi-DNN select compensation 12/13/14 (F6) — canonical 11/12/13.
5. Multi-DNN 10-cycle table-write spacing and `st_mem_cycles=0` (F7).

## Not fully fixable within scope (stated plainly)

- **WS per-channel invocation**: `ws_input_ch` is an architectural config
  input — one input channel per invocation, accumulators cleared in IDLE
  between passes. The TB still sums C per-channel partials for C>1 layers.
  Removing this needs an in-RTL channel loop (WS FSM redesign).
- **`sched_table` in the DNN-aware schedulers** is still written from two
  blocks (load entries vs. done-flags) — disjoint fields/timing in practice,
  flagged for cleanup.
- **Harness timing coupling**: the golden harness drives the `ext_*` ports
  with cycle-accurate schedules derived from the fetcher pipelines. A
  handshake (ready/valid) on those ports would remove that coupling; that is
  an interface redesign, not a bug fix.

## Estimated vs actual cycles (regenerated CSV)

`estimated_vs_actual_cycles.csv` (20 rows). Layer-total agreement improved
roughly 5× across the board (e.g. tiny_00 OS 0.51% → 2.81%, IS 0.01% → 6.1%,
mnist_02 5.6%, multi ~15.6%) because the invocation counts collapsed —
but agreement remains structurally low. The Python model assumes one MAC per
PE per cycle with perfect streaming; the RTL input fetchers issue **one
column-address per cycle** (an ARRAY_WIDTH× slower input stream) plus weight
preload and the new drain windows. Closing the remaining gap is a fetcher
bandwidth redesign (parallel column issue), not a correctness matter.

## Reproduction

Same commands as the baseline report §9; all runs on branch
`fix/rtl-findings`. Commits: `821114c` (F1), `5dddd52` (F8), `fc7e3dd` (F5),
`e6f4597` (F2), `20abccc` (F3+F4), `0527937` (F6), `cd53743` (F7).
