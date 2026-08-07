"""Cycle-accurate software reference for the stamp-based memory controller.

Why this exists
---------------
`rtl/memory/stamp_based_memory_controller.sv` is the hardware that consumes the
delta-op stream emitted by `stamp_compiler.py`.  Until now the only way to check
that the compiler and the controller agreed was to open Vivado and eyeball the
Tcl console.  That made every compiler change unverifiable on a machine without
an RTL simulator, and it is what let the checked-in `delta_ops.hex` drift out of
sync with the compiler for several revisions.

This module re-implements the controller's FSM in Python at cycle granularity so
that:

  * the op stream can be replayed and its statistics checked in pytest,
  * the compiler's own accounting (bytes loaded / moved / kept) can be
    cross-validated against what the hardware would actually count,
  * the cycle cost of a phase can be predicted and compared against the RTL
    `stats_compute_cycles` when a simulator *is* available.

The FSM below mirrors the RTL state-for-state.  Keep the two in sync: the
opcode map here and `OPCODE` in `stamp_compiler.py` and the `OP_*` localparams
in the controller are one contract in three places.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence

# Opcode map -- must match OPCODE in stamp_compiler.py and the OP_* localparams
# in stamp_based_memory_controller.sv.
OP_KEEP = 0
OP_MOVE = 1
OP_LOAD = 2
OP_ALLOC = 3
OP_ZERO = 4

OPCODE_NAMES = {
    OP_KEEP: "keep",
    OP_MOVE: "move",
    OP_LOAD: "load",
    OP_ALLOC: "alloc",
    OP_ZERO: "zero",
}
NAME_TO_OPCODE = {v: k for k, v in OPCODE_NAMES.items()}

# Matches MAX_AXI_BURST_WORDS in the RTL: AXI4 ARLEN is 8 bits, so a single
# read burst carries at most 256 beats and longer loads are split.
MAX_AXI_BURST_WORDS = 256


@dataclass
class StampControllerStats:
    """Mirror of the controller's stats_* output ports."""

    loads: int = 0
    moves: int = 0
    keeps: int = 0
    allocs: int = 0
    zeros: int = 0
    bad_ops: int = 0
    bytes_loaded: int = 0
    bytes_moved: int = 0
    bytes_zeroed: int = 0

    # Not an RTL port: total cycles the controller was busy, summed over phases.
    cycles: int = 0
    # Number of AXI read bursts issued (one per LOAD, plus one per 256-word split).
    axi_bursts: int = 0

    def as_dict(self) -> Dict[str, int]:
        return {
            "stats_loads": self.loads,
            "stats_moves": self.moves,
            "stats_keeps": self.keeps,
            "stats_allocs": self.allocs,
            "stats_zeros": self.zeros,
            "stats_bad_ops": self.bad_ops,
            "stats_bytes_loaded": self.bytes_loaded,
            "stats_bytes_moved": self.bytes_moved,
            "stats_bytes_zeroed": self.bytes_zeroed,
            "cycles": self.cycles,
            "axi_bursts": self.axi_bursts,
        }


@dataclass
class ScratchpadModel:
    """Word-addressed scratchpad, only as much as the controller itself touches."""

    depth_words: int = 4096
    words: Dict[int, int] = field(default_factory=dict)

    def read(self, byte_addr: int) -> int:
        return self.words.get((byte_addr >> 2) % self.depth_words, 0)

    def write(self, byte_addr: int, value: int) -> None:
        self.words[(byte_addr >> 2) % self.depth_words] = value


def _op_fields(op) -> tuple:
    """Accept either a dict (from stamp_metadata.json) or an object."""
    if isinstance(op, dict):
        raw = op.get("op_type")
        opcode = NAME_TO_OPCODE.get(raw, raw) if isinstance(raw, str) else raw
        return opcode, int(op.get("src_addr", -1)), int(op.get("dst_addr", -1)), int(op.get("size", 0))
    raw = getattr(op, "op_type")
    opcode = NAME_TO_OPCODE.get(raw, raw) if isinstance(raw, str) else raw
    return opcode, int(op.src_addr), int(op.dst_addr), int(op.size)


def run_phase(ops: Sequence,
              stats: StampControllerStats | None = None,
              spad: ScratchpadModel | None = None,
              data_width_bits: int = 32,
              dram=None) -> StampControllerStats:
    """Replay one phase's delta ops through the controller FSM model.

    Args:
        ops:   the phase's delta operations (dicts or DeltaOperation objects).
        stats: accumulate into this instead of a fresh counter set, so a whole
               multi-phase run can be totalled the way the RTL counters are
               (they are only cleared on reset, not per phase).
        spad:  optional scratchpad model, so MOVE/LOAD/ZERO data movement can
               be checked and not just counted.
        dram:  optional callable(byte_addr) -> word, used as the DRAM response
               for LOAD ops when a scratchpad model is supplied.

    Returns the (possibly shared) stats object.
    """
    if stats is None:
        stats = StampControllerStats()
    bpw = data_width_bits // 8

    # IDLE -> FETCH_META takes the cycle in which phase_start is sampled.
    stats.cycles += 1

    for op in ops:
        opcode, src_addr, dst_addr, size = _op_fields(op)

        # FETCH_META: one cycle to decode every op, whatever its type.
        stats.cycles += 1
        words = size // bpw

        if opcode == OP_KEEP:
            stats.keeps += 1

        elif opcode == OP_ALLOC:
            stats.allocs += 1

        elif opcode == OP_MOVE:
            stats.moves += 1
            stats.bytes_moved += size
            # MOVE_READ + MOVE_WRITE per word.
            stats.cycles += 2 * words
            if spad is not None:
                for i in range(words):
                    spad.write(dst_addr + i * bpw, spad.read(src_addr + i * bpw))

        elif opcode == OP_LOAD:
            stats.loads += 1
            stats.bytes_loaded += size
            if words:
                # One LOAD_REQ cycle per burst, one LOAD_RECV cycle per beat.
                bursts = -(-words // MAX_AXI_BURST_WORDS)  # ceil
                stats.axi_bursts += bursts
                stats.cycles += bursts + words
            if spad is not None and dram is not None:
                for i in range(words):
                    spad.write(dst_addr + i * bpw, dram(src_addr + i * bpw))

        elif opcode == OP_ZERO:
            stats.zeros += 1
            stats.bytes_zeroed += size
            # ZERO_WRITE: one scratchpad write per word, no DRAM traffic.
            stats.cycles += words
            if spad is not None:
                for i in range(words):
                    spad.write(dst_addr + i * bpw, 0)

        else:
            # Opcode the hardware does not implement -> compiler/RTL mismatch.
            stats.bad_ops += 1

    # Final FETCH_META that sees op_idx >= op_end, then PHASE_DONE.
    stats.cycles += 2
    return stats


def run_stream(deltas: Iterable[Sequence],
               data_width_bits: int = 32) -> StampControllerStats:
    """Replay every phase of a delta stream, accumulating counters as the RTL does."""
    stats = StampControllerStats()
    for ops in deltas:
        run_phase(ops, stats=stats, data_width_bits=data_width_bits)
    return stats


def run_metadata(metadata: Dict) -> StampControllerStats:
    """Replay a whole `stamp_metadata.json` payload."""
    bits = int(metadata.get("data_width", 4)) * 8
    return run_stream((d["operations"] for d in metadata.get("deltas", [])),
                      data_width_bits=bits)


def naive_baseline_bytes(metadata: Dict) -> int:
    """Off-chip bytes a tag-based scheme would read: every input+weight tile, every phase.

    This is the comparison point for the stamp scheme's delta fetching. Output
    tiles are excluded because they are never a DRAM *read* under either scheme,
    so counting them would inflate the apparent saving.
    """
    return sum(
        t["size"]
        for stamp in metadata.get("stamps", [])
        for t in stamp["tiles"]
        if t["tile_type"] != "output"
    )


def compare_with_compiler(metadata: Dict) -> Dict[str, Dict[str, int]]:
    """Cross-check the compiler's own accounting against the FSM model.

    Returns {metric: {"compiler": x, "controller": y, "delta": y - x}}. All
    deltas must be zero; a non-zero entry means the compiler's bookkeeping and
    what the hardware would actually count have diverged.
    """
    ctrl = run_metadata(metadata)

    comp = {"loads": 0, "moves": 0, "keeps": 0, "allocs": 0, "zeros": 0,
            "load_bytes": 0, "move_bytes": 0, "keep_bytes": 0, "zero_bytes": 0}
    for d in metadata.get("deltas", []):
        s = d.get("stats", {})
        for k in comp:
            comp[k] += s.get(k, 0)

    pairs = [
        ("loads", comp["loads"], ctrl.loads),
        ("moves", comp["moves"], ctrl.moves),
        ("keeps", comp["keeps"], ctrl.keeps),
        ("allocs", comp["allocs"], ctrl.allocs),
        ("zeros", comp["zeros"], ctrl.zeros),
        ("bytes_loaded", comp["load_bytes"], ctrl.bytes_loaded),
        ("bytes_moved", comp["move_bytes"], ctrl.bytes_moved),
        ("bytes_zeroed", comp["zero_bytes"], ctrl.bytes_zeroed),
    ]
    return {name: {"compiler": c, "controller": r, "delta": r - c}
            for name, c, r in pairs}
