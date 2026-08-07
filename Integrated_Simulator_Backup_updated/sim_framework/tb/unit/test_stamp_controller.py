"""Unit tests for the stamp-based memory controller and its op stream.

These run without Verilator/Vivado by exercising `pysim.stamp_ref`, the
cycle-accurate software model of `stamp_based_memory_controller.sv`.

Covers:
  - opcode contract between stamp_compiler.py, stamp_ref.py and the RTL
  - FSM cycle accounting for every op type
  - data movement correctness for MOVE / LOAD / ZERO
  - the compiler-vs-controller cross-check on the real generated metadata
  - the off-chip traffic reduction claim (stamp vs always-load baseline)

Cocotb RTL tests (guarded by COCOTB_AVAILABLE) drive the same scenarios at the
real DUT when a simulator is present.
"""
from __future__ import annotations

import json
from pathlib import Path

try:
    import cocotb
    from cocotb.triggers import RisingEdge
    COCOTB_AVAILABLE = True
except ImportError:
    COCOTB_AVAILABLE = False

import pytest

from pysim.stamp_ref import (
    MAX_AXI_BURST_WORDS,
    NAME_TO_OPCODE,
    OPCODE_NAMES,
    OP_ALLOC,
    OP_KEEP,
    OP_LOAD,
    OP_MOVE,
    OP_ZERO,
    ScratchpadModel,
    StampControllerStats,
    compare_with_compiler,
    naive_baseline_bytes,
    run_metadata,
    run_phase,
)

# The compiler and its generated metadata live in the standalone
# stamp-memory-management tree; sim_framework/ is two levels down from the repo
# root, so walk back up to reach it.
REPO_ROOT = Path(__file__).resolve().parents[3]
STAMP_DIR = REPO_ROOT / "static_hash_and_tagless_memory"
METADATA_PATH = STAMP_DIR / "stamp_metadata.json"
HEX_PATH = STAMP_DIR / "delta_ops.hex"


def _op(op_type, size, src=0, dst=0):
    return {"op_type": op_type, "src_addr": src, "dst_addr": dst, "size": size}


@pytest.fixture(scope="module")
def metadata():
    if not METADATA_PATH.exists():
        pytest.skip("stamp_metadata.json not generated; run stamp_compiler.py")
    with open(METADATA_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def rows():
    if not HEX_PATH.exists():
        pytest.skip("delta_ops.hex not generated; run stamp_compiler.py")
    with open(HEX_PATH) as f:
        return [line.strip() for line in f if line.strip()]


# ---------------------------------------------------------------------------
# Opcode contract
# ---------------------------------------------------------------------------

class TestOpcodeContract:
    """The opcode map is duplicated in three places; they must agree."""

    def test_opcode_values_are_stable(self):
        # These integers are baked into the RTL `case` statement. Changing one
        # without changing stamp_based_memory_controller.sv silently breaks
        # every phase the hardware runs.
        assert OP_KEEP == 0
        assert OP_MOVE == 1
        assert OP_LOAD == 2
        assert OP_ALLOC == 3
        assert OP_ZERO == 4

    def test_name_and_code_maps_are_inverses(self):
        for code, name in OPCODE_NAMES.items():
            assert NAME_TO_OPCODE[name] == code

    def test_compiler_opcode_map_matches(self):
        """stamp_compiler.OPCODE must equal the model's map."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "stamp_compiler", STAMP_DIR / "stamp_compiler.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert mod.OPCODE == NAME_TO_OPCODE, (
            "stamp_compiler.OPCODE has drifted from stamp_ref's opcode map"
        )

    def test_unknown_opcode_counted_as_bad(self):
        """An opcode the RTL cannot decode must be flagged, not silently skipped."""
        stats = run_phase([_op(99, 64)])
        assert stats.bad_ops == 1
        assert stats.loads == stats.moves == stats.keeps == 0


# ---------------------------------------------------------------------------
# FSM cycle accounting
# ---------------------------------------------------------------------------

class TestCycleAccounting:

    def test_empty_phase_costs_only_handshake(self):
        """IDLE->FETCH_META, FETCH_META sees op_idx>=op_end, PHASE_DONE."""
        assert run_phase([]).cycles == 3

    def test_keep_is_one_cycle(self):
        """KEEP moves no data: one FETCH_META decode cycle and nothing more."""
        base = run_phase([]).cycles
        assert run_phase([_op("keep", 4096)]).cycles == base + 1

    def test_alloc_is_one_cycle(self):
        """ALLOC only reserves a slot; compute fills it, so no transfer cycles."""
        base = run_phase([]).cycles
        assert run_phase([_op("alloc", 4096)]).cycles == base + 1

    def test_move_is_two_cycles_per_word(self):
        """MOVE_READ + MOVE_WRITE per word, plus the decode cycle."""
        base = run_phase([]).cycles
        stats = run_phase([_op("move", 64)])   # 64 B = 16 words
        assert stats.cycles == base + 1 + 2 * 16

    def test_zero_is_one_cycle_per_word(self):
        """ZERO_WRITE is write-only: half the cost of a MOVE of the same size."""
        base = run_phase([]).cycles
        stats = run_phase([_op("zero", 64)])
        assert stats.cycles == base + 1 + 16

    def test_load_is_one_cycle_per_word_plus_burst_setup(self):
        base = run_phase([]).cycles
        stats = run_phase([_op("load", 64)])
        assert stats.cycles == base + 1 + 1 + 16   # decode + LOAD_REQ + 16 beats
        assert stats.axi_bursts == 1

    def test_long_load_splits_into_axi_bursts(self):
        """AXI4 ARLEN is 8 bits, so >256 beats needs more than one burst."""
        words = MAX_AXI_BURST_WORDS * 2 + 5
        stats = run_phase([_op("load", words * 4)])
        assert stats.axi_bursts == 3

    def test_zero_length_op_does_not_hang(self):
        """A sub-word op must not underflow words_left and spin for 65k cycles."""
        base = run_phase([]).cycles
        for kind in ("move", "load", "zero"):
            stats = run_phase([_op(kind, 0)])
            assert stats.cycles == base + 1, f"{kind} with size 0 cost extra cycles"


# ---------------------------------------------------------------------------
# Data movement
# ---------------------------------------------------------------------------

class TestDataMovement:

    def test_move_copies_words(self):
        spad = ScratchpadModel()
        for i in range(4):
            spad.write(0x40 + 4 * i, 0xA000 + i)
        run_phase([_op("move", 16, src=0x40, dst=0x80)], spad=spad)
        for i in range(4):
            assert spad.read(0x80 + 4 * i) == 0xA000 + i

    def test_zero_fills_zeros(self):
        spad = ScratchpadModel()
        for i in range(4):
            spad.write(0x100 + 4 * i, 0xDEAD)
        run_phase([_op("zero", 16, dst=0x100)], spad=spad)
        for i in range(4):
            assert spad.read(0x100 + 4 * i) == 0

    def test_load_pulls_from_dram(self):
        spad = ScratchpadModel()
        run_phase([_op("load", 16, src=0x2000, dst=0x200)],
                  spad=spad, dram=lambda a: a)
        for i in range(4):
            assert spad.read(0x200 + 4 * i) == 0x2000 + 4 * i

    def test_alloc_writes_nothing(self):
        """Output slots are filled by the compute pipeline, not the controller."""
        spad = ScratchpadModel()
        run_phase([_op("alloc", 64, dst=0x300)], spad=spad)
        assert spad.words == {}

    def test_keep_writes_nothing(self):
        spad = ScratchpadModel()
        run_phase([_op("keep", 64, src=0x400, dst=0x400)], spad=spad)
        assert spad.words == {}


# ---------------------------------------------------------------------------
# Statistics accumulate across phases like the RTL counters do
# ---------------------------------------------------------------------------

class TestStatsAccumulation:

    def test_counters_accumulate_across_phases(self):
        """RTL stats_* clear only on reset, not per phase."""
        stats = StampControllerStats()
        run_phase([_op("load", 32)], stats=stats)
        run_phase([_op("load", 32)], stats=stats)
        assert stats.loads == 2
        assert stats.bytes_loaded == 64

    def test_byte_counters_track_op_sizes(self):
        stats = run_phase([_op("load", 100), _op("move", 200), _op("zero", 300)])
        assert stats.bytes_loaded == 100
        assert stats.bytes_moved == 200
        assert stats.bytes_zeroed == 300


# ---------------------------------------------------------------------------
# End-to-end against the real compiler output
# ---------------------------------------------------------------------------

class TestAgainstGeneratedMetadata:

    def test_compiler_and_controller_agree(self, metadata):
        """The compiler's bookkeeping must equal what the hardware would count."""
        report = compare_with_compiler(metadata)
        bad = {k: v for k, v in report.items() if v["delta"] != 0}
        assert not bad, f"compiler/controller accounting diverged: {bad}"

    def test_no_undecodable_opcodes(self, metadata):
        """Every op the compiler emits must be one the RTL implements."""
        assert run_metadata(metadata).bad_ops == 0

    def test_stamp_beats_naive_baseline(self, metadata):
        """The whole point of the scheme: fetch deltas, not whole tiles."""
        stats = run_metadata(metadata)
        naive = naive_baseline_bytes(metadata)
        assert stats.bytes_loaded < naive
        reduction = 1 - stats.bytes_loaded / naive
        assert reduction > 0.5, f"expected >50% off-chip reduction, got {reduction:.1%}"

    def test_padding_is_not_charged_as_dram_traffic(self, metadata):
        """Zero-padding halo is written on-chip; it must not count as a DRAM read."""
        stats = run_metadata(metadata)
        assert stats.bytes_zeroed > 0, "expected padding regions in a padded conv"
        # Zero-fill bytes must not be double-counted into the load total.
        total_ops = sum(len(d["operations"]) for d in metadata["deltas"])
        assert stats.zeros + stats.loads + stats.moves + stats.keeps + stats.allocs == total_ops

    def test_phase_table_covers_the_whole_stream(self, metadata):
        """phase_base_addr/num_delta_ops must walk every op exactly once."""
        table = metadata["phase_table"]
        expected_base = 0
        for entry, delta in zip(table, metadata["deltas"]):
            assert entry["base_index"] == expected_base
            assert entry["num_ops"] == len(delta["operations"])
            expected_base += entry["num_ops"]
        total_ops = sum(len(d["operations"]) for d in metadata["deltas"])
        assert expected_base == total_ops


class TestDeltaOpsHex:
    """The hex image the RTL testbench $readmemh's must match the metadata."""

    def test_one_line_per_operation(self, rows, metadata):
        total_ops = sum(len(d["operations"]) for d in metadata["deltas"])
        assert len(rows) == total_ops, (
            f"delta_ops.hex has {len(rows)} entries but the compiler emitted "
            f"{total_ops} ops -- the hex image is stale"
        )

    def test_all_words_are_128_bit(self, rows):
        for i, r in enumerate(rows):
            assert len(r) == 32, f"line {i}: expected 32 hex chars, got {len(r)}"
            int(r, 16)   # must parse

    def test_fields_decode_back_to_metadata(self, rows, metadata):
        """Unpack each word and check it against the JSON it came from."""
        flat = [op for d in metadata["deltas"] for op in d["operations"]]
        for row, op in zip(rows, flat):
            word = int(row, 16)
            opcode = (word >> 112) & 0xFF
            size = word & 0xFFFF_FFFF
            dst = (word >> 32) & 0xFFFF_FFFF
            assert opcode == NAME_TO_OPCODE[op["op_type"]]
            assert size == op["size"]
            assert dst == (op["dst_addr"] & 0xFFFF_FFFF)


# ---------------------------------------------------------------------------
# Cocotb RTL tests (require Verilator + cocotb)
# ---------------------------------------------------------------------------

if COCOTB_AVAILABLE:

    async def _reset(dut):
        dut.rst_n.value = 0
        dut.phase_start.value = 0
        dut.metadata_wr_en.value = 0
        for _ in range(3):
            await RisingEdge(dut.clk)
        dut.rst_n.value = 1
        await RisingEdge(dut.clk)

    async def _program(dut, slot, opcode, tile_id, src, dst, size):
        dut.metadata_wr_en.value = 1
        dut.metadata_wr_addr.value = slot
        dut.metadata_wr_data.value = (
            (opcode & 0xFF) << 112 | (tile_id & 0xFFFF) << 96
            | (src & 0xFFFF_FFFF) << 64 | (dst & 0xFFFF_FFFF) << 32
            | (size & 0xFFFF_FFFF)
        )
        await RisingEdge(dut.clk)
        dut.metadata_wr_en.value = 0
        await RisingEdge(dut.clk)

    async def _run_phase(dut, base, n_ops, timeout=20000):
        dut.phase_base_addr.value = base
        dut.num_delta_ops.value = n_ops
        dut.phase_start.value = 1
        await RisingEdge(dut.clk)
        dut.phase_start.value = 0
        for _ in range(timeout):
            await RisingEdge(dut.clk)
            if dut.phase_done.value == 1:
                return
        raise TimeoutError("phase_done never asserted")

    @cocotb.test()
    async def test_alloc_opcode_counted(dut):
        """OP_ALLOC (3) must increment stats_allocs, not stats_bad_ops."""
        await _reset(dut)
        await _program(dut, 0, OP_ALLOC, 0, 0, 0x100, 256)
        await _run_phase(dut, 0, 1)
        assert int(dut.stats_allocs.value) == 1
        assert int(dut.stats_bad_ops.value) == 0

    @cocotb.test()
    async def test_zero_opcode_writes_zeros(dut):
        """OP_ZERO (4) must zero the scratchpad range without any DRAM read."""
        await _reset(dut)
        await _program(dut, 0, OP_ZERO, 0, 0, 0x200, 16)
        await _run_phase(dut, 0, 1)
        assert int(dut.stats_zeros.value) == 1
        assert int(dut.stats_bytes_zeroed.value) == 16
        assert int(dut.stats_bytes_loaded.value) == 0

    @cocotb.test()
    async def test_phase_base_addr_selects_op_window(dut):
        """Two phases at different base indices must run different ops."""
        await _reset(dut)
        await _program(dut, 0, OP_KEEP, 0, 0, 0, 64)
        await _program(dut, 1, OP_ALLOC, 1, 0, 0, 64)
        await _run_phase(dut, 0, 1)
        assert int(dut.stats_keeps.value) == 1
        assert int(dut.stats_allocs.value) == 0
        await _run_phase(dut, 1, 1)
        assert int(dut.stats_keeps.value) == 1
        assert int(dut.stats_allocs.value) == 1

    @cocotb.test()
    async def test_unknown_opcode_flagged(dut):
        await _reset(dut)
        await _program(dut, 0, 0x7F, 0, 0, 0, 64)
        await _run_phase(dut, 0, 1)
        assert int(dut.stats_bad_ops.value) == 1
