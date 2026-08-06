# Member 2 Memory-Management Golden Report — STAMP / PAGED / banks / stalls

**Date:** 2026-07-17 · **Branch:** `golden-check/member2-memory-mgmt` (on top of
the layout+casting branches) · **Method:** Verilator 5.050 + cocotb 2.0.1,
TF 2.21 goldens, 5%-of-full-scale tolerance. Every number is measured from a
real Verilator run unless explicitly labelled **derived**.

## 1. The gap, verified before any change

Member 2's hardware is real; the golden runs exercised it empty. Trace
evidence (pre-change):

| Feature | In RTL? | Reached top ports? | Exercised in golden runs? | Recorded? |
|---|---|---|---|---|
| STAMP delta-op engine (LOAD/MOVE/KEEP, real AXI) | REAL (`stamp_based_memory_controller`) | phase + loads/moves/keeps stats: yes | **no** — 0 delta ops, metadata never written | absent |
| PAGED page table + hit/miss | REAL (per-port `page_table`) | hits/misses: yes | **no** — PT never written, no port traffic | absent |
| Scratchpad banking (`NUM_BANKS`) | REAL (`scratchpad_ram` banked arbitration) | **no** — tops hard-defaulted 4 | no (zero traffic) | `b4` filename label only |
| Bank-conflict / stall counters | REAL (cycle-accurate) | **no** — dangling at `u_mem` | no | absent |
| Bank/stall estimates | — | — | — | model-only (`software_ref.estimate_bank_conflicts`) |

Consequences before the fix: STAMP vs PAGED differed by exactly one skipped
zero-op phase handshake per invocation (5,808 vs 5,802 cycles on tiny L0);
`--num-banks` never reached Verilator; no bank/stall field existed in any
result JSON.

## 2. Changes made (commits `6042962`, `ebf428e`, plus the PT-write fix)

1. **Plumbing (RTL, additive):** `NUM_BANKS` parameter on both tops →
   `mem_backend_wrap`; bank-stat outputs (`stats_bank_conflicts`,
   `stats_bank_conflict_stall_cycles`) exposed as top ports; new external
   `spad_dbg_*` read ports (default 0 = legacy idle wiring) so the memory
   side can be exercised. `run_golden.py` passes `-GNUM_BANKS`; every golden
   JSON now records bank + backend stats.
2. **Real work from the TB (`test_scheme_divergence.py`):** per OS tile,
   the host programs the engines as designed — STAMP: LOAD/KEEP delta ops in
   the metadata table (contiguous runs, host reuse tracking), executed by the
   hardware engine during the stamp phase with real AXI bursts; PAGED:
   demand replay of the tile footprint through the page-table translation
   (misses measured on unmapped pages), then host `pt_write` of faulted
   pages. Post-tile 4-port footprint replays exercise the banked arbitration
   with real DNN address patterns. Compute, `ext_*` data, and correctness
   collection are identical to the golden harness.
3. **PAGED PT-write fix (RTL, 1 gate):** the per-port page-table write was
   gated `p == 0` **and** required `rd_addr[0]` to hold the target VPN — the
   in-file comment intends the host to load every port's table, but the gate
   made ports 1–3 permanently miss. Writes now broadcast to all port tables
   (`paged_memory_backend.sv`). The divergence experiment was re-run against
   this corrected baseline.

**Not changed:** Member 1's arrays/fetchers/layout/casting RTL, the core
golden harness logic, Member 3's schedulers.

## 3. num_banks is a real hardware knob now (measured)

Synthetic 4-port patterns, 200-cycle windows, cells = conflict_cycles /
stall_port_cycles (`test_bank_sweep.py`):

| pattern (port p reads…) | b=1 | b=2 | b=4 | b=8 | b=16 |
|---|---|---|---|---|---|
| same_addr (0) | 0/0 | 200/600 | 200/600 | 200/600 | 200/600 |
| consecutive (p) | 0/0 | 200/400 | 0/0 | 0/0 | 0/0 |
| stride4 (4p) | 0/0 | 200/600 | 200/600 | 200/400 | 0/0 |
| stride8 (8p) | 0/0 | 200/600 | 200/600 | 200/600 | 200/400 |

Every cell matches interleaved-banking theory (`bank = addr mod NUM_BANKS`,
lower port wins). With **real traffic** (tiny L0 STAMP run, 4-port replay of
real tile footprints, whole layer):

| NUM_BANKS | 2 | 4 | 8 | 16 |
|---|---|---|---|---|
| conflicts / stall port-cycles | **438 / 876** | 2 / 4 | 2 / 4 | **0 / 0** |

All four configurations PASS at 0.013 %FS. (mnist at b=4: 101/202.)

## 4. STAMP vs PAGED — the divergence experiment (measured)

Whole layer, OS 8×8, CHANNEL_MAJOR; PAGED numbers are **post PT-write fix**
(correctly working 4-port baseline):

| | tiny STAMP | tiny PAGED | mnist STAMP | mnist PAGED |
|---|---|---|---|---|
| correctness | PASS 0.013% | PASS 0.013% | PASS 0.009% | PASS 0.009% |
| delta ops: LOAD / KEEP | 19 / 22 | — | 113 / 414 | — |
| page hits / misses | — | 1,470 / 294 | — | 10,506 / 102 |
| **backend off-chip bytes** | **1,640 (measured)** | **8,192 (derived)** | **3,448 (measured)** | **8,192 (derived)** |
| total AXI AR / beats | 157 / 2,246 | 138 / 1,836 | 945 / 11,470 | 832 / 10,608 |
| bank conflicts / stalls | 2 / 4 | 84 / 240 | 101 / 202 | 232 / 488 |
| cycles compute / program / replay | 6,316 / 41 / 456 | 5,802 / 2 / 456 | 38,440 / 527 / 2,912 | 36,608 / 2 / 2,912 |

**The plain answer: yes, STAMP and PAGED now genuinely differ in hardware,
and STAMP fetches less off-chip data — 5.0× less on tiny (1,640 B vs
8,192 B) and 2.4× less on mnist (3,448 B vs 8,192 B) — against the corrected
PAGED baseline.** STAMP's delta mechanism captured 76.8 % (tiny) and
**91.9 %** (mnist) of word-touches as on-chip reuse (KEEP), fetching only the
new halo rows/columns per tile. The small test layers were sufficient to
show the divergence; no larger case was needed.

Cross-checks that anchor the numbers in hardware:
- `stats_bytes_loaded` (HW counter) = exactly 4 × the host-computed new-word
  count (410 / 862 words) on both layers.
- Total AXI beats = the layout-prefetcher background (identical in both
  schemes: 1,836 / 10,608) **plus exactly** the delta-load beats (410 / 862)
  in the STAMP runs; the PAGED backend issues zero AXI (its DRAM port is
  tied off in RTL by design).
- PAGED hits + misses = exactly the replayed footprint touches
  (1,764 / 10,608).

### Honesty labels (do not drop these when quoting)

- **(a) Asymmetric off-chip metric:** STAMP bytes are *measured* on the real
  AXI port; PAGED bytes are *derived* = measured page faults (2) × 4 KB page
  — the paged backend has no DRAM path in RTL, so the page-fetch cost is
  implied, and the PAGED cycle counts exclude that implied fetch time while
  STAMP's compute cycles *include* its real delta-load time (+514 cycles on
  tiny). The volume comparison is real; the cycle comparison is asymmetric
  in PAGED's favour.
- **(b) v1-wiring limit:** all conflicts/stalls/hits/misses are memory-side
  events from engine activity and replayed footprints; they cannot yet
  back-pressure compute because the array reads via `ext_*`, not through the
  scratchpad. Full compute-coupling is future work.
- **(c) Replay = modelled consumers:** the 4-port replays stand in for the
  array's reads (which the v1 wiring doesn't route through the scratchpad);
  the addresses are the real tile footprints, the arbitration is real RTL.

### Why the two schemes' conflict counts differ

STAMP replays compacted scratchpad slots (bump-allocated, dense, stride-1
across ports → almost conflict-free at 4 banks); PAGED replays translated
`paddr`s that preserve page-relative offsets (strided rows → 84–232 conflict
events). That is a genuine consequence of each scheme's placement policy,
not an artifact.

## 5. Findings for Member 2 (RTL)

1. **PT-write gate (FIXED here):** `p == 0` + `rd_addr[0]`-VPN-match gate
   made ports 1–3 permanently miss. Fix applied: broadcast PT writes.
2. **Address-unit inconsistency (open, documented):** the stamp datapath is
   byte-addressed (dst `>>2` before the scratchpad); the paged datapath
   passes `paddr` low bits to the word-addressed scratchpad with no shift.
   The divergence experiment therefore runs PAGED word-addressed with
   `PAGE_SIZE_BITS=10` (1,024 words = 4 KB pages) for self-consistency.
   Proposal: pick one unit (bytes) and add the shift in the paged path.
3. **Paged eviction/replacement:** none exists (v1) — pages map once and
   stay; fine at these footprints (≪ scratchpad), matters for larger nets.

## 6. Regression safety

Full 19/19 golden regression re-run after **each** change (plumbing, TB
work, PT-write fix): all PASS every time, Member 1 errors/cycles and Member
3 scheduler results byte-identical (tiny OS 5,808 cyc / 0.013 %; WS 8×8
153,738; mnist OS 36,712 / 0.009 %; all five schedulers `all_pass`). The
PT-write broadcast cannot affect legacy runs (`pt_write_en` is never
asserted there) — confirmed by measurement, not just argument.

Raw evidence: `results/golden_check/raw/bank_sweep_b*.json`,
`raw/divergence_{tiny,mnist}_cnn_layer_00_{STAMP,PAGED}_b*.json` (each
includes the full `out_fixed` tensor and a `verdict` block).
