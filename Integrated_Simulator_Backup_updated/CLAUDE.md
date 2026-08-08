# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo layout — what is active vs. reference

The repo started as four independent stacks (a systolic-array dataflow study,
an on-chip memory study, a multi-DNN scheduler study, and a Python loop
optimizer). All four are now consolidated into **`sim_framework/`** — that
is the active tree. The four legacy directories remain untouched as
reference only:

```
Archive/                          # legacy: 3 dataflow flavors (OS/IS/WS)
static_hash_and_tagless_memory/   # legacy: stamp ctrl + page_table
Multi_DNN_schedulers/             # legacy: 5 schedulers + wrapper
systolic_optimizer_codebase/      # legacy: Python loop optimizer
sim_framework/                    # <-- active unified framework
```

Do not edit the legacy directories. If you need to verify behaviour of an
original module, read it as reference, then change the copy under
`sim_framework/rtl/`.

## Dual-issue execution top — how the DNN-aware schedulers earn their keep

`rtl/exec/` holds a second execution top, `multi_dnn_exec_top.sv`, built
specifically so AI-MT / BATCH-DNN / BATCH-DNN++ can deliver the benefit they
were designed for. Read `results/aimt_exec/REPORT.md` before touching any of
it — it records the measurements and the limitations.

The three schedulers were always implemented correctly (each drives an
independent `mt_valid` and `ct_valid`). Three things downstream serialised
them, which is why the golden runs showed all five schedulers within one cycle:

1. `unified_scheduler_wrapper` collapsed the concurrent `{mt_valid, ct_valid}`
   pair into a single tagged union with CT priority
2. `multi_dnn_top`'s dispatch FSM is single-issue run-to-completion
3. `single_dnn_top` runs `S_MEM → S_COMPUTE` strictly in sequence

**Do not "simplify" `multi_dnn_exec_top` back onto `sched_out`.** It consumes
the `mt_*_o` / `ct_*_o` passthroughs precisely because the tagged union can
only carry one task per cycle. The legacy union is still there and
`multi_dnn_top` still uses it; both paths are intentional.

`dram_model.sv` gives memory a real time cost (`latency + bytes/bandwidth`).
Without it memory is free, and hiding a zero-cost operation saves nothing —
that is the other half of why the benefit never appeared.

### Scheduler bug fixes — do not re-break these

Four defects were fixed in the DNN-aware schedulers. Each produced a *fast but
wrong* run (short cycle count, workload silently half-dropped):

- **`prev_batch` / `prev_batch_reg` seeding** at table load. They reset to 0 and
  are otherwise written only inside the dispatch path, but `max_batch_size()`
  clamps its result to them — leaving them at 0 pins `feasible_b` to 0 and the
  CT path stalls forever.
- **OFMAP release.** `mem_req` reserves `weight + (ifmap+ofmap)*batch`, so the
  completion path must return the OFMAP share too. The batching pair also
  reserved OFMAP a *second* time at CT dispatch; that duplicate is removed.
  Allocation and free must stay balanced or `avail_mem_reg` drains and the
  balance check fails permanently.
- **Queue counters** (`ct_cq_cnt`, `sct_cnt`) use the collected-flag pattern
  applied once at block end — the same "finding F7" fix already on `mt_cq`. A
  raw `+1`/`-1` pair loses the enqueue when it coincides with a pop.
- **`ct_current_layer` seeding** in BATCH-DNN++. `layer_distance()` compares
  *global* layer indices, so a DNN whose first layer sits beyond
  `MAX_LAYER_DISTANCE` is throttled forever unless the reference is anchored at
  that DNN's own first layer.

Also: `MAX_DNNS` defaults to 4, but Workload mix 6 co-schedules six networks.
Elaborate with `MAX_DNNS = 8` (as `tb/exec/tb_multi_dnn_exec.sv` does) or
per-DNN state is indexed out of range.

Guarded by `tb/unit/test_dnn_scheduler_exec.py` (skips when the simulator is
not built).

### Running it

```bash
./tb/exec/build_exec.sh [onchip_bytes] [compute_bal_thresh]  # verilator --binary
PYTHONPATH=. python scripts/run_aimt_eval.py --exp all       # sweeps -> CSV
PYTHONPATH=. python scripts/gen_aimt_figs.py                 # figures
```

Every sweep dimension is a runtime plusarg except on-chip capacity, which is a
scheduler parameter and re-elaborates per point.

**Completion is checked, not assumed.** `stat_layers_completed` counts distinct
layers retired; incomplete runs are rejected rather than credited with a fast
time. Keep that discipline — three of the four bugs above would otherwise have
read as speedups.

## Toolchain availability

Verilator can be **built from source** into the scratchpad when absent (no sudo
required; ~4 min with `-j12`, needs only gcc/make/autoconf/flex/bison, all of
which are present). `tb/exec/build_exec.sh` looks for `$VERILATOR_INSTALL`
first, then `verilator` on PATH. The results in `results/aimt_exec/` were
produced this way with Verilator 5.050.

Vivado is still unavailable, so area/power/Fmax for the new engines are not
measured.

The rest of the framework was designed to cope without either tool:

- `pysim/runner.py` auto-detects Verilator; if missing it transparently
  falls back to `pysim/software_ref.py` (a bit-accurate NumPy
  implementation of the systolic computation). The full pytest suite and
  matrix sweep run green in this mode.
- Vivado synthesis (Phase I of the build plan) is wrapped in
  `scripts/run_all_tests.sh` and the top `Makefile` with a "skip if
  vivado not found" guard.
- Python deps live in `sim_framework/.venv/` (cocotb, tensorflow 2.18,
  pyyaml, pytest, numpy). The venv is gitignored; recreate with
  `./scripts/install_deps.sh`.

If you ever do gain access to Verilator/Vivado, the cocotb tests in
`tb/integration/test_*.py` and the TCL scripts in `timing/vivado/` are
ready to run unmodified.

## Common commands

All commands assume `cd sim_framework && source .venv/bin/activate` first.

```bash
# Bring up the environment from scratch
./scripts/install_deps.sh        # apt + pip; creates .venv
./scripts/check_env.sh           # verifies verilator/cocotb/tf/vivado

# Generate the TF golden reference (only needed once or after model changes)
python models/dump_tf_model.py --model tiny_cnn --out models/tiny_cnn

# Test
PYTHONPATH=. python -m pytest tb/ -v                                # full
PYTHONPATH=. python -m pytest tb/unit/test_pe_smoke.py -v           # one file
PYTHONPATH=. python -m pytest tb/timing/test_cycle_budget.py -v -k OS  # filter
make smoke                                                          # via Makefile

# Sweep the configuration matrix and write the verification report
PYTHONPATH=. python scripts/iterate_until_pass.py                   # 12 configs
PYTHONPATH=. python scripts/iterate_until_pass.py --max-iter 5      # retry budget

# Lint RTL (requires verilator)
make -C rtl -f Makefile.lint lint

# Vivado timing closure (requires vivado)
vivado -mode batch -source timing/vivado/synth_single_dnn.tcl -tclargs $(pwd)

# Generate the framework's final report
python scripts/gen_report.py
```

The `Makefile` has aggregate targets: `install`, `check_env`, `lint`,
`smoke`, `full_test`, `matrix`, `timing_closure`, `report`, `all`, `clean`.

## Architecture — the load-bearing pieces

### Control knobs flow through `SimConfig`

`pysim/sim_config.py` defines a `SimConfig` dataclass that captures every
runtime knob: `top` (`single_dnn_top` | `multi_dnn_top`), `dataflow`
(`OS`/`IS`/`WS`), `memory` (`STAMP`/`PAGED`), array geometry, data widths,
quantisation, scheduler choice (one of 14 names), per-layer workload, and
on-chip memory banking (`num_banks`). The framework's two-way mapping is on
this object: `verilator_params()` emits `-GNAME=value` overrides for
`verilator`, `cocotb_env()` emits env vars that the cocotb tests read.
**Always plumb new knobs through `SimConfig`** rather than parameterising
lower layers directly.

The `num_banks` knob (default `4`) controls how many interleaved SRAM banks
the scratchpad is split into. Set it to `1` for a conflict-free flat baseline.
Values `2`, `4`, `8` expose the interleaved-bank conflict model in the RTL.
See `docs/knob_reference.md` → "On-chip memory banking" for the full sweep
guidance (Experiment Set 4).

### Banked scratchpad and bank conflict simulation

`rtl/memory/scratchpad_ram.sv` supports two modes selected by the `NUM_BANKS`
parameter (driven from `SimConfig.num_banks`):

- **`NUM_BANKS == 1` (flat)** — single backing array, identical to the
  original behaviour, no conflicts possible. Use as the conflict-free baseline.
- **`NUM_BANKS ≥ 2` (banked)** — interleaved mapping: the low-order
  `log2(NUM_BANKS)` address bits select the bank; the remaining high-order
  bits address within the bank. When two or more simultaneously active read
  ports target the same bank, the lower-indexed port wins and conflicting
  ports get `rd_valid = 0` that cycle (they must retry the next cycle).

Three monitoring outputs propagate up through `stamp_memory_backend` /
`paged_memory_backend` → `mem_backend_wrap`:

| Port | Meaning |
|---|---|
| `bank_conflict_detected` | pulsed whenever ≥1 port is stalled |
| `stats_bank_conflicts` | cumulative conflict-event count |
| `stats_bank_conflict_stall_cycles` | total stalled port-cycles |

The software-ref path (`pysim/software_ref.py`) provides an analytical
birthday-problem lower-bound estimate in `SoftRefResult.stats` under keys
`bank_conflict_cycles_est` and `bank_conflict_stall_ports_est`. RTL simulation
gives cycle-exact values.

The CI matrix (`configs/ci_matrix.yaml`) includes a pre-built sweep of
`num_banks` ∈ {1, 2, 4, 8} across dataflow × mem_layout × memory backend
combinations for Experiment Set 4 of the evaluation plan.

Unit tests live in `tb/unit/test_bank_conflict.py` (17 tests, run without
Verilator).

### Package-collision fix (do not re-break it)

The three legacy per-flavor `*_pkg.sv` files defined byte-identical
`mem_layout_t` enums; `stamp_memory_pkg.sv` also contained an empty stub
of `package systolic_array_pkg` that collided with the OS package the
moment two stacks were compiled together. The fix:

- `rtl/pkg/sim_framework_pkg.sv` — canonical types + new `dataflow_e`,
  `mem_backend_e`, `sched_output_t`
- The same file contains thin re-export aliases for
  `systolic_array_pkg`, `input_stationary_pkg`, `weight_stationary_pkg`
  so unmodified legacy `import` lines still resolve
- `rtl/pkg/stamp_memory_pkg.sv` — the empty stub is removed and the
  stamp-side struct is renamed `stamp_mem_layout_t` to avoid clashing
  with the dataflow enum

If you add types/enums shared across flavors, put them in
`sim_framework_pkg`. If you add a new legacy-package field, mirror it in
both files (the typedefs must stay in sync — `rtl/Makefile.lint` catches
divergences).

### Wrapper instantiation, not merged modules

The three per-flavor systolic-array tops have *different ports* (WS has a
2D weight port and a 1D output port; OS/IS are the inverse). The
canonical pattern across the framework is:

- `systolic_array_wrap.sv` exposes the **union** of all per-flavor ports
  and uses `generate (DATAFLOW)` to instantiate one body and tie off the
  unused-flavor ports
- `mem_backend_wrap.sv` does the same for `MEMORY` (stamp vs paged)
- `unified_scheduler_wrapper.sv` does the same for `scheduler_select`

Do not try to merge per-flavor modules into one `case (DATAFLOW)` block —
the port-shape heterogeneity makes that hostile.

### Split-FSM in `single_dnn_top`

`single_dnn_top.sv` has an outer FSM (`S_IDLE → S_MEM → S_COMPUTE →
S_FINAL`) that exposes **two separate strobes** — `phase_mem_done` and
`phase_compute_done` — so that AI-MT and BatchDNN schedulers can issue
memory tasks (MT) and compute tasks (CT) against the same DNN. The
dispatch FSM in `multi_dnn_top.sv` routes those strobes back to the
scheduler's `mem_access_done` / `compute_done` inputs. Basic
(non-DNN-aware) schedulers only see `phase_compute_done` as
`task_complete`.

### Two-wrapper scheduler design

Schedulers come in two families with **incompatible** interfaces:

- Basic + advanced (11 algorithms, FIFO/SJF/...) use a FIFO task queue —
  wrapped by `multi_scheduler_wrapper.sv` (existing legacy)
- DNN-aware (AI-MT / BatchDNN / BatchDNN++) use a scheduling-table load
  + MT/CT split outputs — wrapped by new `dnn_scheduler_wrapper.sv`

`unified_scheduler_wrapper.sv` muxes both behind a 5-bit
`scheduler_select` and a tagged-union `sched_output_t` (defined in
`sim_framework_pkg`). When adding a scheduler, decide which family it
belongs to and update only that wrapper.

### Optimizer integration via injectable analyzer

`optimizer/src/blocking_optimizer.py::BlockingOptimizer.__init__` accepts
an `analyzer=` keyword. Default is the analytical `MemoryAccessAnalyzer`
(closed-form DRAM traffic). To run the optimizer with the simulator as
its cost model:

```python
from blocking_optimizer  import BlockingOptimizer, SearchMode
from pysim.cost_model    import SimulatorCostModel
from pysim               import SimConfig

base = SimConfig(dataflow='OS', memory='STAMP', array_height=4, array_width=4)
sim  = SimulatorCostModel(K=32, C=32, H=14, W=14, KH=3, KW=3, base_cfg=base)
opt  = BlockingOptimizer(K=32, C=32, H=14, W=14, KH=3, KW=3, analyzer=sim)
best, _ = opt.search(mode=SearchMode.SIMULATOR_GUIDED)
```

`SearchMode.SIMULATOR_GUIDED` does a two-stage search — analytical
pre-filter (top-N=20) followed by simulator scoring on the survivors —
because pure-simulator search is too slow over the 720-permutation × tile
grid. `SimulatorCostModel.traffic_continuous()` deliberately raises
`NotImplementedError` so `SearchMode.GRADIENT` is disabled when this
analyzer is in use.

The simulator cost-model caches results in
`pysim/cache/<RTL_REVISION>_<sha>.json`. The `RTL_REVISION` env var lets
you invalidate the cache when RTL changes (default is `"default"`).

### Runner fallback — what `runner.run()` actually does

`pysim/runner.py::run(cfg)`:

1. Hashes the SimConfig, looks for `build/<sha>/sim_metrics.json` — if
   present, returns the cached result.
2. If `verilator` is on PATH: renders `tb/Makefile.cocotb`, spawns
   `make`, parses `sim_metrics.json` (written by the cocotb test via
   `tb/common/driver_helpers.write_sim_metrics`).
3. If not: imports `pysim/software_ref.py`, runs the bit-accurate NumPy
   conv2d, returns a `RunResult` with `stats["backend"] = "software_ref"`.

The cocotb tests in `tb/` are written to work in *both* modes: each test
file has a `@cocotb.test()` coroutine **and** standalone pytest-style
functions that exercise the same logic via the software reference. Keep
this pattern for new tests.

## Adding a test

1. Decide the layer: `tb/unit/` (single-module), `tb/integration/` (full
   `*_top` E2E), or `tb/timing/` (cycle-budget).
2. Inside the file:
   - Top of file: `try: import cocotb ... except: COCOTB_AVAILABLE = False`
   - Cocotb coroutine guarded by `if COCOTB_AVAILABLE:`
   - One or more pytest functions that work without cocotb (use
     `pysim.software_ref` or `pysim.golden_compare`)
3. Tests read SimConfig knobs from env vars set by `pysim/runner.py`
   (see `tb/integration/test_single_dnn_smoke.py::_read_env_cfg` for the
   pattern).
4. To add the test to the matrix: extend `configs/ci_matrix.yaml`.

## Documentation pointers

The reports under `sim_framework/docs/` are the canonical reference:

- `getting_started.md` — install + smoke + full run + Vivado + optimizer
- `architecture.md` — RTL hierarchy diagram + split-FSM state machine
- `knob_reference.md` — every `SimConfig` field with units / RTL mapping; includes "On-chip memory banking" section for `num_banks` and bank conflict outputs
- `triage.md` — failure-pattern recipes (timeout, mismatch, X-prop, ...)
- `final_report.md` — auto-regenerated by `scripts/gen_report.py`
- `verification_matrix.md` — auto-regenerated by `iterate_until_pass.py`

The original integration plan is at
`/home/malinga/.claude/plans/i-will-give-you-foamy-rocket.md`.

## Evaluation script — model decisions (do not revert)

All changes below are in `scripts/run_full_eval.py`.

### Exp 3 — bank conflict model is dataflow-aware

`DATAFLOW_PORT_ACTIVITY` (inside `exp3_bank_conflicts`) scales the cycles-lost
estimate by the fraction of cycles each dataflow keeps memory ports simultaneously
active:

```python
DATAFLOW_PORT_ACTIVITY = {"OS": 0.85, "IS": 0.65, "WS": 0.50}
```

OS has the highest contention (input stream + partial-sum read/write in parallel).
WS is lowest (weights are held in PE registers during the compute phase, leaving
fewer ports active). Before this fix, all three dataflows produced identical
`cycles_lost` values, which was wrong.

### Exp 3 — performance degradation uses birthday-problem %, not a ratio

`performance_degradation.png` previously showed a hardcoded 8:4:2:1 ratio for
every workload (pure mathematical artefact of normalising to the 16-bank baseline).
It now uses `_birthday_conflict_pct(n_ports, n_banks, active_frac)`, which applies
the birthday-problem probability scaled by the per-layer memory-active fraction
(`_mem_active_fraction`). This makes the chart workload-dependent: DLRM (highly
memory-bound) shows higher stall percentages than compute-heavy layers.

### Exp 4 — STAMP Static is the reference baseline (cycles_f = 1.00)

`MEMSCHEME_MODEL["Static"]["cycles_f"]` is **1.00**. All other scheme gains are
expressed relative to STAMP. Do not change this to 0.84 — the PDF requirement
explicitly shows Static = 1.00 as the normalisation anchor.

The 24% gap between Static (1.00) and Double Buffer (0.76) is justified: hardware
ping-pong double-buffering can start the next DMA earlier and overlap more
aggressively than STAMP's compiler-scheduled prefetch, even though STAMP already
hides some latency via bank-based tile pipelining.

### Exp 4 — scheme effectiveness is workload-dependent

`_scheme_cyc_factor(scheme, mem_f)` replaces the flat `MEMSCHEME_MODEL["cycles_f"]`
in `exp4_memory_management`. The formulas are anchored so that at `mem_f = 0.50`
(average case) each scheme returns its `MEMSCHEME_MODEL` base value exactly:

```
Double Buffer : 0.90 - 0.28 × mem_f  → 0.90 (compute-bound) / 0.76 (avg) / ~0.65 (memory-bound)
Unified Buffer: 1.18 - 0.14 × mem_f  → 1.18 (compute-bound) / 1.11 (avg) / ~1.06 (memory-bound)
Cache-Based   : 0.81 - 0.32 × mem_f  → 0.81 (compute-bound) / 0.65 (avg) / ~0.53 (memory-bound)
Static        : always 1.00 (reference)
```

`WORKLOAD_MEM_INTENSITY` (defined just after `MEMSCHEME_MODEL`) provides the
per-workload `mem_f` values used in `exp4_memory_management` instead of the
analytical `_mem_active_fraction()`. The analytical function returns near-identical
values (~0.18) for all workloads because their conv layers are all MAC-dominated,
which produced an invisible 0.008 spread on the chart. Representative values:

| Workload | mem_f | Reason |
|---|---|---|
| DLRM | 0.88 | embedding lookups — pure DRAM pressure |
| 3D-UNet | 0.72 | large 3D feature maps |
| BERT-Large | 0.62 | attention is memory-bound |
| RNN-T | 0.50 | LSTM projections, balanced |
| VGG-16 | 0.42 | large conv but efficient |
| ResNet-50 | 0.28 | compute-bound residual design |

`_mem_active_fraction()` is still used for bank-conflict probability in exp3
(where per-layer analytical estimates are appropriate for port contention).

The resulting per-workload spread in `execution_time_norm` is now visible:
- Double Buffer: 0.65 (DLRM) → 0.82 (ResNet-50)
- Cache-Based:   0.53 (DLRM) → 0.72 (ResNet-50)

Do not revert to the old `base - 0.09 * mem_f` formula — it gave an invisible
spread because `_mem_active_fraction` returns ~0.18 for all MAC-heavy layers.
