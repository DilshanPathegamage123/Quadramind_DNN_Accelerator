#!/usr/bin/env python3
"""
Stamp-Based Memory Management Compiler for DNN Accelerators

This compiler implements static on-chip memory management for DNN accelerators:
1. Constructs input tiles for each execution phase
2. Maps tiles to on-chip memory statically
3. Determines deltas between consecutive memory stamps
4. Generates metadata for the hardware controller

Key Concepts:
- Phase: A set of input, weight, and output tiles that fit in the systolic array at one time
- Stamp: The layout of phase data in on-chip memory
- Delta: The difference between consecutive stamps (what needs to be loaded/moved)
"""

#This code builds a memory compiler for CNN accelerators:
# It does:
# 1. Tile convolution layer into phases
# 2. Allocate SRAM layout (stamp)
# 3. Compare consecutive layouts
# 4. Generate reuse commands
# 5. Save bandwidth

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set
from enum import Enum
import json


class TileType(Enum):
    INPUT = "input" #(images/activations)
    WEIGHT = "weight" #(FILTERS)
    OUTPUT = "output" #(results)
    INTERMEDIATE = "intermediate" #(partial sum)


# ---------------------------------------------------------------------------
# Hardware opcode map — MUST stay in sync with the `case` in
# stamp_based_memory_controller.sv.  The controller decodes
# metadata_wr_data[119:112] with exactly these values.
# ---------------------------------------------------------------------------
OPCODE = {
    "keep":  0,   # data already at the right on-chip address: no traffic
    "move":  1,   # on-chip relocation: scratchpad read -> scratchpad write
    "load":  2,   # off-chip DRAM burst -> scratchpad write
    "alloc": 3,   # output slot reserved; compute writes it, no memory traffic
    "zero":  4,   # zero-padding halo: scratchpad write of 0s, no DRAM read
}

# 128-bit metadata word layout consumed by the controller:
#   [127:120] reserved (0)
#   [119:112] op_type
#   [111:96]  tile_id
#   [95:64]   src_addr
#   [63:32]   dst_addr
#   [31:0]    size
METADATA_WORD_BITS = 128

#Represents one tile.
@dataclass
class Tile:
    """Represents a data tile in a DNN computation phase"""
    tile_id: int
    tile_type: TileType
    shape: Tuple[int, ...]  # (C, H, W) for activations, (K, C, Kh, Kw) for weights - (e.g., a 3x3 weight filter) 
    size_bytes: int
    phase_id: int
    reuse_count: int = 1  # How many times this tile is reused
    
     # These tell the memory controller where in the full tensor this tile lives.
    # Use -1 as sentinel "not set".
    src_h:   int = -1   # Top-left input row  (INPUT tiles)
    src_w:   int = -1   # Top-left input col  (INPUT tiles)
    src_oc:  int = -1   # First output channel (WEIGHT tiles)
    dst_oc:  int = -1   # First output channel (OUTPUT tiles)
    dst_h:   int = -1   # Top-left output row  (OUTPUT tiles)
    dst_w:   int = -1   # Top-left output col  (OUTPUT tiles)

    #Allows tiles to be compared in sets/dictionaries for exact data reuse.
    # __hash__ and __eq__ MUST agree on the same key, otherwise two tiles that
    # compare equal can land in different hash buckets and set/dict lookups
    # (get_tile_address, get_tiles) silently miss.  tile_id already encodes the
    # phase (phase_id * 1000 + slot), so (tile_id, tile_type) is unique on its
    # own and phase_id must NOT be part of the hash key.
    def __hash__(self):
        return hash((self.tile_id, self.tile_type))

    #Needed when detecting reuse
    def __eq__(self, other):
        if not isinstance(other, Tile):
            return NotImplemented
        return (self.tile_id == other.tile_id and
                self.tile_type == other.tile_type)


# This OnChipLocation class represents where a specific tile of data is stored in on-chip memory (SRAM)
@dataclass
class OnChipLocation:
    """Represents a location in on-chip memory"""
    start_addr: int
    end_addr: int
    tile: Tile # Reference to the actual Tile object being stored at this location
    
    @property
    def size(self):
        return self.end_addr - self.start_addr

#Represents entire SRAM state for one phase.
@dataclass
class MemoryStamp:
    """Represents the complete on-chip memory layout for one execution phase"""
    phase_id: int
    locations: List[OnChipLocation] = field(default_factory=list) #initializes an empty list for each instance
    total_size: int = 0 #Tracks the maximum address used (how much SRAM is occupied)
    
    #Places tile into SRAM.
    #Example: add_tile(tile, start_addr=0) will place the tile at the beginning of SRAM.
    def add_tile(self, tile: Tile, start_addr: int):
        """Add a tile to this stamp at the specified address"""
        location = OnChipLocation(
            start_addr=start_addr,
            end_addr=start_addr + tile.size_bytes,
            tile=tile
        )
        self.locations.append(location)
        self.total_size = max(self.total_size, location.end_addr)
    
    def get_tile_address(self, tile: Tile) -> int:
        """Get the on-chip address of a specific tile"""
        for loc in self.locations:
            if loc.tile == tile:
                return loc.start_addr
        return -1 # Tile not found in this stamp - Common error indicator for integer-returning functions
    
    #Returns all tiles inside stamp.
    def get_tiles(self) -> Set[Tile]:
        """Get all tiles in this stamp"""
        return {loc.tile for loc in self.locations}


@dataclass
class DeltaOperation:
    """Represents a single operation to transition between stamps"""
    # "load" (from DRAM), "move" (on-chip reuse, different address),
    # "keep" (on-chip reuse, same address), "alloc" (output tile: produced
    # by compute, never fetched from DRAM).
    op_type: str
    tile: Tile
    src_addr: int = -1  # "move"/"keep": on-chip source addr; "load": real DRAM byte addr; "alloc": unused (-1)
    dst_addr: int = -1  # Destination on-chip address
    size: int = 0 # Data size in bytes

    #Example: load input tile from DRAM to addr 0
    #Example: move tile from addr 0 to addr 1024
    #Example: keep tile at addr 0 (src_addr and dst_addr are the same)
    #Example: alloc output tile at addr 2048 (compute will write it, no DRAM read)
    
    def to_dict(self): # Convert to dictionary for JSON serialization
        #Python objects (like DeltaOperation) can't be directly saved to files - they need to be converted to a serializable format.
        return {
            "op_type": self.op_type,
            "tile_id": self.tile.tile_id,
            "tile_type": self.tile.tile_type.value,
            "src_addr": self.src_addr,
            "dst_addr": self.dst_addr,
            "size": self.size,
            "offset": self.dst_addr - self.src_addr if self.op_type == "move" else 0
        }

#Represents all operations from phase A → phase B
# represents the transition operations between two consecutive memory stamps
@dataclass
class StampDelta:
    """Represents the delta between two consecutive memory stamps"""
    from_phase: int
    to_phase: int
    operations: List[DeltaOperation] = field(default_factory=list)
    
    # Adds a single operation to the delta (e.g., load, move, keep)
    def add_operation(self, op: DeltaOperation):
        self.operations.append(op)
    
    def get_stats(self):
        """Get statistics about this delta"""
        def _n(kind):
            return sum(1 for op in self.operations if op.op_type == kind)

        def _b(kind):
            return sum(op.size for op in self.operations if op.op_type == kind)

        loads = _n("load")    # Must be fetched from off-chip DRAM (expensive)
        moves = _n("move")    # Reused within on-chip SRAM (cheap, different address)
        keeps = _n("keep")    # Reused in the same location (free)
        allocs = _n("alloc")  # Output slot; never read from DRAM
        zeros = _n("zero")    # Zero-padding halo; written on-chip, never read from DRAM

        load_bytes = _b("load")
        move_bytes = _b("move")
        keep_bytes = _b("keep")
        alloc_bytes = _b("alloc")
        zero_bytes = _b("zero")

        return {
            "loads": loads,
            "moves": moves,
            "keeps": keeps,
            "allocs": allocs,
            "zeros": zeros,
            "load_bytes": load_bytes,
            "move_bytes": move_bytes,
            "keep_bytes": keep_bytes,
            "alloc_bytes": alloc_bytes,
            "zero_bytes": zero_bytes,
            "total_ops": len(self.operations),  # Total operations in this delta
            # Bytes NOT re-fetched from off-chip DRAM thanks to on-chip reuse
            # (both "moved" and "kept" data avoid a DRAM read).  Zero-padding
            # is excluded: it was never off-chip data in either scheme, so
            # counting it would inflate the apparent saving.
            "bandwidth_saved": move_bytes + keep_bytes
        }

#Main Compiler - This is the brain. It has four main methods that run in sequence.
class StampCompiler:
    """
    Compiler that generates memory stamps and deltas for DNN execution
    """
    
    #Constructor
    def __init__(self, on_chip_size: int, data_width: int = 4,
                 input_base_addr: int = 0x0000_0000,
                 weight_base_addr: int = 0x1000_0000,
                 output_base_addr: int = 0x2000_0000):
        """
        Args:
            on_chip_size: Size of on-chip memory in bytes
            data_width: Width of each data element in bytes (default: 4 for fp32)
            input_base_addr/weight_base_addr/output_base_addr: off-chip DRAM
                base addresses for each tensor, assuming channel-major
                (C, H, W) / (OC, IC, KH, KW) layouts. Used to compute real
                "load" source addresses instead of a -1 placeholder.
        """
        #Example: 16KB SRAM ,fp32 = 4 bytes
        self.on_chip_size = on_chip_size
        self.data_width = data_width
        self.input_base_addr = input_base_addr
        self.weight_base_addr = weight_base_addr
        self.output_base_addr = output_base_addr
        self.phases: List[List[Tile]] = []
        self.stamps: List[MemoryStamp] = []
        self.deltas: List[StampDelta] = []

        # Full-tensor dimensions, recorded by create_conv_phases() and needed
        # to turn a tile's (src_h, src_w) / src_oc into a real off-chip byte
        # address. None until create_conv_phases() has run.
        self._ic = self._ih = self._iw = None
        self._kh = self._kw = None
        self._oh = self._ow = None
        self._bpe = data_width
        
    #Divides output space into rectangular tiles, then for each tile creates a phase 
    # a list of 3 Tile objects (input, weight, output) that the systolic array needs to compute that tile.    
    def create_conv_phases(self,
                          layer_config: Dict,
                          systolic_array_size: Tuple[int, int],
                          tile_strategy: str = "output_stationary"):
        """
        Create execution phases for a convolutional layer

        Args:
            layer_config: Dict with layer parameters
                - input_channels, input_height, input_width
                - output_channels, output_height, output_width
                - kernel_height, kernel_width
                - stride, padding
            systolic_array_size: (height, width) of systolic array
            tile_strategy: "output_stationary" (only supported value today)
        """
        # The tiling loop below is output-stationary by construction (it walks
        # the output space and derives the receptive field).  Accepting a WS/IS
        # value and silently producing an OS schedule would misreport which
        # dataflow the stamps belong to, so reject it explicitly.
        if tile_strategy != "output_stationary":
            raise NotImplementedError(
                f"tile_strategy={tile_strategy!r} is not implemented; "
                f"create_conv_phases() only generates output-stationary phases."
            )

        # =====================================================================
        # Step 1: Read layer dimensions
        # =====================================================================
        ic = layer_config['input_channels']   # Number of input feature map channels
        ih = layer_config['input_height']     # Spatial height of the input feature map
        iw = layer_config['input_width']      # Spatial width  of the input feature map
        oc = layer_config['output_channels']  # Number of output feature map channels
        oh = layer_config['output_height']    # Spatial height of the output feature map
        ow = layer_config['output_width']     # Spatial width  of the output feature map
        kh = layer_config['kernel_height']    # Convolution kernel (filter) height
        kw = layer_config['kernel_width']     # Convolution kernel (filter) width

        stride  = layer_config['stride']    # Step size the kernel moves each output position
        padding = layer_config['padding']   # Zero-padding added around the input border

        # Multiplying element counts by data_width gives sizes in *bits*, not bytes.
        # Hardware memory interfaces expect bytes, so we convert once here and use
        bytes_per_element = self.data_width

        # Stash full-tensor dims so compute_deltas() can derive real off-chip
        # byte addresses for LOAD ops (input/weight) instead of a -1 placeholder.
        self._ic, self._ih, self._iw = ic, ih, iw
        self._kh, self._kw = kh, kw
        self._oh, self._ow = oh, ow
        self._bpe = bytes_per_element

        array_h, array_w = systolic_array_size

        # =====================================================================
        # Step 2: Choose tile size — how much the array can process at once.
        # Because array can process only limited rows/cols at once.
        
        # We clamp each output dimension to the corresponding array dimension
        output_tile_h = min(array_h, oh)   # Rows of output one tile covers
        output_tile_w = min(array_w, ow)   # Columns of output one tile covers
        output_tile_c = min(array_w, oc)   # Output channels one tile covers
        # Note: output_tile_c uses array_w because the systolic array's column
        # dimension maps to output channels in the output-stationary dataflow.

        # =====================================================================
        # Step 3: Input tile size depends on output tile and kernel.
    
        # The general formula for how many input rows/cols are needed to produce
        # output_tile_h/w output rows/cols with a given stride and kernel size is:
        input_tile_h = (output_tile_h - 1) * stride + kh   # Input rows  needed (receptive field)
        input_tile_w = (output_tile_w - 1) * stride + kw   # Input cols  needed (receptive field)
        phase_id = 0

        # =====================================================================
        # Step 4: Loop Through All Tiles
        # Generate phases by tiling the output space.
        # Each Phase Creates 3 Tiles (input, weight, output).
      
        # Loop order: output channels → output height rows → output width cols
        # This is the standard output-stationary traversal order.
        # The innermost body runs once per (oc_tile, oh_tile, ow_tile) triplet
        # and produces exactly one phase.

        # --- Outer loop: tile along the output-channel axis ---
        for oc_start in range(0, oc, output_tile_c):
            oc_end  = min(oc_start + output_tile_c, oc)   # Clamp to actual channel count
            oc_tile = oc_end - oc_start                    # Actual channels in this tile (may be < output_tile_c at boundary)

            # --- Middle loop: tile along the output-height axis ---
            for oh_start in range(0, oh, output_tile_h):
                oh_end  = min(oh_start + output_tile_h, oh)   # Clamp to actual output height
                oh_tile = oh_end - oh_start                    # Actual output rows in this tile

                # --- Inner loop: tile along the output-width axis ---
                for ow_start in range(0, ow, output_tile_w):
                    ow_end  = min(ow_start + output_tile_w, ow)   # Clamp to actual output width
                    ow_tile = ow_end - ow_start                    # Actual output cols in this tile

                    # Above divides layer into many phases

                    phase_tiles = []

                    # gives each phase its own ID range (0–999, 1000–1999)
                    # preventing collisions across phases.
                    tile_id_counter = phase_id * 1000  # Unique tile IDs — multiplying by 1000
                    # gives each phase its own ID range. It avoids ID collisions between tiles in different phases:
                    #   Phase 0 tiles → IDs 0, 1, 2
                    #   Phase 1 tiles → IDs 1000, 1001, 1002  etc.

                    # ---------------------------------------------------------
                    # INPUT TILE
                    # Covers all input channels for the spatial region that the
                    # convolution kernel reads in order to produce this output tile.
                 
                    # We also store ih_start and iw_start in the Tile so that the
                    # memory controller knows which region of the input tensor to
                    # load from off-chip memory.  Without this the controller has
                    # no way to determine the correct source address.
                    # ---------------------------------------------------------
                    ih_start = oh_start * stride - padding   # Top-left row   of the input region (may be negative → pad with zeros)
                    iw_start = ow_start * stride - padding   # Top-left column of the input region

                    # All channels × spatial area × bytes per element
                    input_size = ic * input_tile_h * input_tile_w * bytes_per_element
                    # Example (stride=1, pad=0): 16 channels * 6 rows * 6 cols * 4 bytes = 2304 bytes

                    input_tile = Tile(
                        tile_id=tile_id_counter,
                        tile_type=TileType.INPUT,
                        shape=(ic, input_tile_h, input_tile_w),
                        size_bytes=input_size,
                        phase_id=phase_id,
                        src_h=ih_start,   # position stored so loader fetches the right region
                        src_w=iw_start,
                    )
                    phase_tiles.append(input_tile)
                    tile_id_counter += 1   # counter now points to weight slot

                    # ---------------------------------------------------------
                    # WEIGHT TILE
                    # Filter volume for this output-channel slice.
                    # Shape: (oc_tile, ic, kh, kw) — one filter per output channel,
                    # each filter covers all input channels and the full kernel window.
                    # Weights do not depend on the spatial position of the output tile,
                    # only on which output channels (oc_start…oc_end) are active.
                    # Filter volume for this output channel slice
                    weight_size = oc_tile * ic * kh * kw * bytes_per_element
                    # Example: 4 output channels * 16 input channels * 3*3 kernel * 4 bytes = 2304 bytes

                    weight_tile = Tile(
                        tile_id=tile_id_counter,
                        tile_type=TileType.WEIGHT,
                        shape=(oc_tile, ic, kh, kw),
                        size_bytes=weight_size,
                        phase_id=phase_id,
                        src_oc=oc_start,   # Which output-channel slice these weights belong to
                    )
                    phase_tiles.append(weight_tile)
                    tile_id_counter += 1   # counter now points to output slot

                    # ---------------------------------------------------------
                    # OUTPUT TILE
                    # Output activation volume produced by this phase.
                    # Shape: (oc_tile, oh_tile, ow_tile).
                    # oh_tile / ow_tile may be smaller than output_tile_h/w at
                    # the right/bottom boundary of the feature map.
                    # ---------------------------------------------------------
                    # Output activation volume
                    output_size = oc_tile * oh_tile * ow_tile * bytes_per_element
                    # Example: 4 output channels * 4 rows * 4 cols * 4 bytes = 256 bytes

                    output_tile = Tile(
                        tile_id=tile_id_counter,
                        tile_type=TileType.OUTPUT,
                        shape=(oc_tile, oh_tile, ow_tile),
                        size_bytes=output_size,
                        phase_id=phase_id,
                        dst_oc=oc_start,   # Where in the output tensor to write results
                        dst_h=oh_start,
                        dst_w=ow_start,
                    )
                    phase_tiles.append(output_tile)
                    tile_id_counter += 1   # Keep counter consistent (points past output slot)

                    # Commit this phase — all 3 tiles are now in phase_tiles
                    self.phases.append(phase_tiles)
                    phase_id += 1

        print(f"Created {len(self.phases)} execution phases")

    # Now place tiles in SRAM.
    # Uses greedy strategy.    
    def allocate_stamps(self, allocation_strategy: str = "greedy"):
        """
        Allocate on-chip memory addresses for each phase's tiles
        
        Args:
            allocation_strategy: "greedy" or "optimal"
        """
        if allocation_strategy != "greedy":
            # Previously any other value silently fell through the `if` below
            # and appended an *empty* stamp for every phase, which then made
            # compute_deltas() emit nothing and print "0 deltas" with no error.
            raise ValueError(
                f"Unsupported allocation_strategy {allocation_strategy!r}; "
                f"only 'greedy' is implemented."
            )

        for phase_id, phase_tiles in enumerate(self.phases):
            stamp = MemoryStamp(phase_id=phase_id)
            # Create an empty memory stamp for this phase

            if allocation_strategy == "greedy":
                # Simple greedy allocation - Start allocating from the beginning of on-chip memory
                current_addr = 0
                
                # Sort tiles by type for better locality
                sorted_tiles = sorted(phase_tiles, 
                                    key=lambda t: (t.tile_type.value, t.tile_id))
                
                # Place tiles sequentially in SRAM
                for tile in sorted_tiles:
                    if current_addr + tile.size_bytes > self.on_chip_size:
                        #If exceeds SRAM:
                        raise ValueError(
                            f"Phase {phase_id} doesn't fit in on-chip memory! "
                            f"Required: {current_addr + tile.size_bytes}, "
                            f"Available: {self.on_chip_size}"
                        )
                    
                    stamp.add_tile(tile, current_addr)
                    current_addr += tile.size_bytes
            
            self.stamps.append(stamp)
        
        print(f"Allocated {len(self.stamps)} memory stamps")
        
    def compute_deltas(self):
        """
        Compute deltas between consecutive stamps to identify:
        1. Tiles/sub-regions that can be kept (same location, identical data)
        2. Tiles/sub-regions that can be moved (identical data, on-chip reshuffle)
        3. Data that must be loaded from off-chip (genuinely new/different)
        4. Output tiles, which are always freshly allocated (produced by
           compute, never fetched from DRAM)

        Reuse is decided on tile *identity*, not merely tile *shape*:
        - WEIGHT tiles are only reusable if they cover the same output-channel
          slice (src_oc match) — same-shape weights from a different slice are
          different filter data and must be reloaded.
        - INPUT tiles are only reusable to the extent their spatial footprint
          (src_h/src_w) actually overlaps the previous phase's footprint; the
          overlapping region is a "move" (on-chip halo shift) and only the
          non-overlapping remainder is a genuine "load".
        """
        for i in range(len(self.stamps) - 1):
            current_stamp = self.stamps[i]
            next_stamp = self.stamps[i + 1]

            delta = StampDelta(from_phase=i, to_phase=i + 1)

            curr_by_type = {loc.tile.tile_type: (loc.tile, loc.start_addr)
                             for loc in current_stamp.locations}

            for loc in next_stamp.locations:
                next_tile, next_addr = loc.tile, loc.start_addr
                curr_tile, curr_addr = curr_by_type.get(
                    next_tile.tile_type, (None, None))

                if next_tile.tile_type == TileType.WEIGHT:
                    ops = self._delta_weight(curr_tile, curr_addr, next_tile, next_addr)
                elif next_tile.tile_type == TileType.INPUT:
                    ops = self._delta_input(curr_tile, curr_addr, next_tile, next_addr)
                elif next_tile.tile_type == TileType.OUTPUT:
                    ops = [self._delta_output(next_tile, next_addr)]
                else:
                    # No reuse model defined for this tile type: conservatively
                    # treat as a fresh load rather than silently dropping it.
                    ops = [DeltaOperation(op_type="load", tile=next_tile,
                                           src_addr=-1, dst_addr=next_addr,
                                           size=next_tile.size_bytes)]

                for op in ops:
                    delta.add_operation(op)

            self.deltas.append(delta)

        print(f"Computed {len(self.deltas)} deltas")

    def _input_dram_addr(self, h: int, w: int) -> int:
        """
        Byte address of element (channel 0, h, w) of the full input tensor,
        assuming a channel-major (C, H, W) off-chip layout. h/w outside
        [0, ih)/[0, iw) fall in the zero-padding halo — not a real DRAM
        fetch — so -1 is returned as a "no DRAM traffic" sentinel.
        """
        if h < 0 or w < 0 or h >= self._ih or w >= self._iw:
            return -1
        return self.input_base_addr + (h * self._iw + w) * self._bpe

    def _clip_input_region(self, h0: int, w0: int, rows: int, cols: int):
        """
        Split an input-tile sub-region against the real tensor bounds.

        A region near the border of a padded convolution straddles the
        zero-padding halo: part of it is genuine tensor data that must come
        from DRAM, the rest is implicit zeros that cost no off-chip traffic.
        Charging the whole region as a DRAM "load" (and pointing it at the -1
        sentinel when merely the *top-left corner* lands in padding, as the
        earlier revision did) both overstated off-chip bytes and produced an
        unusable source address for the hardware controller.

        Returns (src_addr, real_bytes, pad_bytes):
            src_addr   -- DRAM byte address of the first in-bounds element,
                          or -1 when the region is entirely padding
            real_bytes -- bytes that genuinely come from DRAM
            pad_bytes  -- bytes that are implicit zeros (zero-fill on-chip)
        """
        ic = self._ic
        full_bytes = ic * rows * cols * self._bpe

        # Intersect the region with the real tensor extent.
        ch0, ch1 = max(h0, 0), min(h0 + rows, self._ih)
        cw0, cw1 = max(w0, 0), min(w0 + cols, self._iw)
        real_rows = max(0, ch1 - ch0)
        real_cols = max(0, cw1 - cw0)

        real_bytes = ic * real_rows * real_cols * self._bpe
        pad_bytes = full_bytes - real_bytes

        src = self._input_dram_addr(ch0, cw0) if real_bytes > 0 else -1
        return src, real_bytes, pad_bytes

    def _input_load_ops(self, tile: Tile, dst_addr: int,
                        h0: int, w0: int, rows: int, cols: int
                        ) -> List[DeltaOperation]:
        """Emit the DRAM-load / zero-fill pair for one input sub-region."""
        src, real_bytes, pad_bytes = self._clip_input_region(h0, w0, rows, cols)

        ops: List[DeltaOperation] = []
        if real_bytes > 0:
            ops.append(DeltaOperation(op_type="load", tile=tile,
                                      src_addr=src, dst_addr=dst_addr,
                                      size=real_bytes))
        if pad_bytes > 0:
            # Implicit zero-padding: written on-chip, never read from DRAM.
            ops.append(DeltaOperation(op_type="zero", tile=tile,
                                      src_addr=-1,
                                      dst_addr=dst_addr + real_bytes,
                                      size=pad_bytes))
        return ops

    def _weight_dram_addr(self, src_oc: int) -> int:
        """
        Byte address of the first weight of output-channel slice src_oc,
        assuming an (OC, IC, KH, KW) off-chip layout.
        """
        return (self.weight_base_addr
                + src_oc * self._ic * self._kh * self._kw * self._bpe)

    def _delta_weight(self, curr_tile, curr_addr, next_tile, next_addr) -> List[DeltaOperation]:
        """A weight tile is reusable only if it is literally the same filter
        data — same shape *and* same output-channel slice (src_oc)."""
        same_data = (curr_tile is not None
                     and curr_tile.shape == next_tile.shape
                     and curr_tile.src_oc == next_tile.src_oc)

        if same_data:
            op_type = "keep" if curr_addr == next_addr else "move"
            return [DeltaOperation(op_type=op_type, tile=next_tile,
                                    src_addr=curr_addr, dst_addr=next_addr,
                                    size=next_tile.size_bytes)]

        # Different output-channel slice => genuinely different filter
        # weights; must come from DRAM.
        src = self._weight_dram_addr(next_tile.src_oc)
        return [DeltaOperation(op_type="load", tile=next_tile,
                                src_addr=src, dst_addr=next_addr,
                                size=next_tile.size_bytes)]

    def _input_row_col_overlap(self, prev: Tile, nxt: Tile):
        """
        Compute how much of `nxt`'s spatial footprint is already resident
        on-chip from `prev`, restricted to the common output-stationary
        sliding-window case: a pure row-shift or a pure column-shift between
        consecutive phases. A simultaneous row+col shift (e.g. wrap-around
        into a new output-channel slice) is not representable as a single
        rectangle here and is conservatively treated as "no overlap" -> full
        reload. This never *overstates* reuse, it only under-claims it in
        that one edge case.

        Returns (overlap_bytes, new_rect) where new_rect is the
        (h0, w0, rows, cols) rectangle of genuinely-new input coordinates in
        full-tensor space, or None when the footprint is unchanged. Returns
        None overall if no usable overlap exists.
        """
        if prev is None or prev.shape != nxt.shape:
            return None
        # Note: -1 is a genuine (padding-adjacent) coordinate here, e.g.
        # ih_start = oh_start*stride - padding == -1 when oh_start=0 and
        # padding=1 — it is NOT the Tile-field "unset" sentinel for INPUT
        # tiles, since create_conv_phases() always assigns src_h/src_w for
        # them. Do not filter it out as if the field were missing.

        ic, h, w = nxt.shape

        if prev.src_h == nxt.src_h and prev.src_w == nxt.src_w:
            return ic * h * w * self._bpe, None

        if prev.src_h == nxt.src_h:
            # Pure column shift.
            col_ov_start = max(prev.src_w, nxt.src_w)
            col_ov_end = min(prev.src_w + w, nxt.src_w + w)
            if col_ov_end <= col_ov_start:
                return None
            ov_cols = col_ov_end - col_ov_start
            new_cols = w - ov_cols
            new_col_start = nxt.src_w if nxt.src_w < prev.src_w else col_ov_end
            return (ic * h * ov_cols * self._bpe,
                    (nxt.src_h, new_col_start, h, new_cols))

        if prev.src_w == nxt.src_w:
            # Pure row shift.
            row_ov_start = max(prev.src_h, nxt.src_h)
            row_ov_end = min(prev.src_h + h, nxt.src_h + h)
            if row_ov_end <= row_ov_start:
                return None
            ov_rows = row_ov_end - row_ov_start
            new_rows = h - ov_rows
            new_row_start = nxt.src_h if nxt.src_h < prev.src_h else row_ov_end
            return (ic * ov_rows * w * self._bpe,
                    (new_row_start, nxt.src_w, new_rows, w))

        return None  # both row and col shifted simultaneously

    def _delta_input(self, curr_tile, curr_addr, next_tile, next_addr) -> List[DeltaOperation]:
        overlap = self._input_row_col_overlap(curr_tile, next_tile)

        if overlap is None:
            # No usable overlap: the whole receptive field is (re)fetched,
            # minus whatever part of it is zero-padding.
            _ic, h, w = next_tile.shape
            return self._input_load_ops(next_tile, next_addr,
                                        next_tile.src_h, next_tile.src_w, h, w)

        ov_bytes, new_rect = overlap

        if new_rect is None:
            # Identical footprint already resident (e.g. wrap-around lands on
            # the same region a previous phase used).
            op_type = "keep" if curr_addr == next_addr else "move"
            return [DeltaOperation(op_type=op_type, tile=next_tile,
                                    src_addr=curr_addr, dst_addr=next_addr,
                                    size=ov_bytes)]

        ops = []
        if ov_bytes > 0:
            # Halo overlap: the still-valid rows/cols are reused on-chip.
            ops.append(DeltaOperation(op_type="move", tile=next_tile,
                                       src_addr=curr_addr, dst_addr=next_addr,
                                       size=ov_bytes))
        # Only the non-overlapping halo is genuinely new; of that, only the
        # in-bounds part is real off-chip traffic.
        nh, nw, nrows, ncols = new_rect
        ops.extend(self._input_load_ops(next_tile, next_addr + ov_bytes,
                                        nh, nw, nrows, ncols))
        return ops

    def _delta_output(self, next_tile, next_addr) -> DeltaOperation:
        """Outputs are produced by compute, never fetched from DRAM: allocate
        the on-chip slot and let the array write back into it."""
        return DeltaOperation(op_type="alloc", tile=next_tile,
                               src_addr=-1, dst_addr=next_addr,
                               size=next_tile.size_bytes)
    
    def generate_metadata(self, output_file: str):
        """
        Generate metadata file for the hardware controller
        
        The metadata includes:
        - Phase configurations
        - Memory stamp layouts
        - Delta operations with move offsets
        """
        metadata = {
            "on_chip_size": self.on_chip_size,
            "data_width": self.data_width,
            "num_phases": len(self.phases),
            "stamps": [],
            "deltas": []
        }
        
        # Add stamp information
        for stamp in self.stamps:
            stamp_data = {
                "phase_id": stamp.phase_id,
                "total_size": stamp.total_size,
                "tiles": [
                    {
                        "tile_id": loc.tile.tile_id,
                        "tile_type": loc.tile.tile_type.value,
                        "shape": loc.tile.shape,
                        "start_addr": loc.start_addr,
                        "end_addr": loc.end_addr,
                        "size": loc.tile.size_bytes
                    }
                    for loc in stamp.locations
                ]
            }
            metadata["stamps"].append(stamp_data)
        
        # Add delta information
        for delta in self.deltas:
            delta_data = {
                "from_phase": delta.from_phase,
                "to_phase": delta.to_phase,
                "operations": [op.to_dict() for op in delta.operations],
                "stats": delta.get_stats()
            }
            metadata["deltas"].append(delta_data)
        
        # Per-delta base index into the flattened delta-op stream.  The
        # hardware controller starts a phase at `phase_base_addr` and runs
        # `num_delta_ops` entries, so a testbench replaying the real compiler
        # output needs this table -- without it every phase restarts at op 0
        # and re-runs the first delta forever.
        metadata["phase_table"] = self.phase_table()
        metadata["opcodes"] = dict(OPCODE)

        # Write to file
        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"Metadata written to {output_file}")

    def phase_table(self) -> List[Dict]:
        """(phase, base_index, num_ops) for each delta, in stream order."""
        table = []
        base = 0
        for delta in self.deltas:
            n = len(delta.operations)
            table.append({
                "phase_id": delta.to_phase,
                "base_index": base,
                "num_ops": n,
            })
            base += n
        return table

    def flat_operations(self) -> List[DeltaOperation]:
        """Every delta operation, flattened in phase order."""
        return [op for delta in self.deltas for op in delta.operations]

    @staticmethod
    def _u32(value: int) -> int:
        """Two's-complement 32-bit encoding (src_addr uses -1 as a sentinel)."""
        return value & 0xFFFF_FFFF

    def emit_delta_ops_hex(self, output_file: str,
                           metadata_depth: int = 256) -> int:
        """
        Emit the flattened delta-op stream as 128-bit hex words for
        $readmemh() into the controller's metadata RAM.

        One line per operation, packed exactly as the controller decodes it
        (see METADATA_WORD_BITS above).  Returns the number of ops written.

        This closes the loop the project always described but never had: the
        RTL testbench previously read a hand-maintained delta_ops.hex that had
        drifted out of sync with the compiler, so the "end-to-end with real
        compiler metadata" test was replaying a stale op mix.
        """
        ops = self.flat_operations()

        if len(ops) > metadata_depth:
            print(f"  WARNING: {len(ops)} delta ops exceed the controller's "
                  f"METADATA_DEPTH={metadata_depth}. The hardware can only "
                  f"hold the first {metadata_depth}; re-run the phases in "
                  f"batches or raise METADATA_DEPTH.")

        with open(output_file, 'w') as f:
            for op in ops:
                word = (
                    (OPCODE[op.op_type] & 0xFF) << 112
                    | (op.tile.tile_id & 0xFFFF) << 96
                    | self._u32(op.src_addr) << 64
                    | self._u32(op.dst_addr) << 32
                    | self._u32(op.size)
                )
                f.write(f"{word:032x}\n")

        print(f"Delta-op stream written to {output_file} ({len(ops)} ops)")
        return len(ops)

    def emit_phase_table_svh(self, output_file: str) -> None:
        """
        Emit a tiny SystemVerilog include so the testbench can walk the real
        phase boundaries instead of hardcoding "3 ops per phase".
        """
        table = self.phase_table()
        with open(output_file, 'w') as f:
            f.write("// Auto-generated by stamp_compiler.py - do not edit.\n")
            f.write(f"localparam int STAMP_NUM_PHASES = {len(table)};\n")
            f.write(f"localparam int STAMP_TOTAL_OPS  = "
                    f"{sum(t['num_ops'] for t in table)};\n")
            f.write(f"localparam int STAMP_PHASE_BASE [0:{max(len(table)-1, 0)}] = '{{\n")
            f.write("    " + ", ".join(str(t["base_index"]) for t in table) + "\n};\n")
            f.write(f"localparam int STAMP_PHASE_NOPS [0:{max(len(table)-1, 0)}] = '{{\n")
            f.write("    " + ", ".join(str(t["num_ops"]) for t in table) + "\n};\n")
        print(f"Phase table written to {output_file} ({len(table)} phases)")


    def print_statistics(self):
        """Print statistics about the stamp-based allocation"""
        print("\n" + "="*80)
        print("STAMP-BASED MEMORY MANAGEMENT STATISTICS")
        print("="*80)
        
        print(f"\nOn-chip memory size: {self.on_chip_size:,} bytes")
        print(f"Number of phases: {len(self.phases)}")
        print(f"Number of deltas: {len(self.deltas)}")
        
        # Stamp statistics
        avg_stamp_size = np.mean([s.total_size for s in self.stamps])
        max_stamp_size = max([s.total_size for s in self.stamps])
        utilization = (avg_stamp_size / self.on_chip_size) * 100
        
        print(f"\nStamp Statistics:")
        print(f"  Average stamp size: {avg_stamp_size:,.0f} bytes")
        print(f"  Maximum stamp size: {max_stamp_size:,} bytes")
        print(f"  Average utilization: {utilization:.1f}%")
        
        # Delta statistics
        if self.deltas:
            agg = [d.get_stats() for d in self.deltas]

            def _tot(key):
                return sum(s[key] for s in agg)

            total_loads = _tot('loads')
            total_moves = _tot('moves')
            total_keeps = _tot('keeps')
            total_allocs = _tot('allocs')
            total_zeros = _tot('zeros')
            total_load_bytes = _tot('load_bytes')
            total_move_bytes = _tot('move_bytes')
            total_keep_bytes = _tot('keep_bytes')
            total_alloc_bytes = _tot('alloc_bytes')
            total_zero_bytes = _tot('zero_bytes')
            total_bandwidth_saved = _tot('bandwidth_saved')

            print("\nDelta Statistics:")
            print(f"  Total load operations:  {total_loads}")
            print(f"  Total move operations:  {total_moves}")
            print(f"  Total keep operations:  {total_keeps}")
            print(f"  Total alloc operations: {total_allocs} (output tiles; not off-chip traffic)")
            print(f"  Total zero operations:  {total_zeros} (padding halo; not off-chip traffic)")
            print(f"  Total bytes loaded (from DRAM):        {total_load_bytes:,}")
            print(f"  Total bytes moved (on-chip reuse):     {total_move_bytes:,}")
            print(f"  Total bytes kept (same on-chip addr):  {total_keep_bytes:,}")
            print(f"  Total bytes allocated (output, no DRAM read): {total_alloc_bytes:,}")
            print(f"  Total bytes zero-filled (padding, no DRAM read): {total_zero_bytes:,}")
            print(f"  Off-chip read bandwidth saved: {total_bandwidth_saved:,} bytes")

            # Denominator = everything that was a *candidate* for a DRAM read
            # (loaded + reused); output allocations never competed for
            # off-chip read bandwidth in the first place, so they're excluded.
            candidate_bytes = total_load_bytes + total_bandwidth_saved
            if candidate_bytes > 0:
                savings_pct = 100 * total_bandwidth_saved / candidate_bytes
                print(f"  Bandwidth savings: {savings_pct:.1f}%")

        print("="*80 + "\n")


def main():
    """Example usage of the StampCompiler"""
    
    # Example: Smaller convolution layer that fits in 16KB scratchpad
    layer_config = {
        'input_channels': 16,
        'input_height': 14,
        'input_width': 14,
        'output_channels': 32,
        'output_height': 14,
        'output_width': 14,
        'kernel_height': 3,
        'kernel_width': 3,
        'stride': 1,
        'padding': 1
    }
    
    # On-chip memory: 16 KB scratchpad
    on_chip_size = 16 * 1024
    systolic_array_size = (4, 4)
    
    # Create compiler
    compiler = StampCompiler(on_chip_size=on_chip_size, data_width=4)
    
    # Generate phases
    compiler.create_conv_phases(layer_config, systolic_array_size)
    
    # Allocate stamps
    compiler.allocate_stamps(allocation_strategy="greedy")
    
    # Compute deltas
    compiler.compute_deltas()
    
    # Generate metadata
    compiler.generate_metadata("stamp_metadata.json")

    # Generate the hardware-facing artefacts consumed by the RTL testbench
    compiler.emit_delta_ops_hex("delta_ops.hex")
    compiler.emit_phase_table_svh("stamp_phase_table.svh")

    # Print statistics
    compiler.print_statistics()


if __name__ == "__main__":
    main()
