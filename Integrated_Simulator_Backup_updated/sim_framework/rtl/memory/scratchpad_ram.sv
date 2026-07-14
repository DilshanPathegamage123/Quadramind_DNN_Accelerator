//=============================================================================
// Module: scratchpad_ram
// Description: Behaviorally-modelled multi-port scratchpad SRAM with optional
//              multi-bank organisation for bank-conflict simulation.
//
// Banking model (NUM_BANKS > 1):
//   Low-order BANK_SEL_W address bits select the bank (interleaved mapping).
//   Remaining high-order bits are the within-bank offset.
//   When two or more simultaneously active ports target the same bank in the
//   same cycle, the lower-indexed port wins and conflicting ports receive
//   rd_valid=0 that cycle (caller must retry with rd_en the next cycle).
//   This stall behaviour propagates naturally to the stamp controller and
//   the systolic-array feed paths, producing cycle-accurate stall counts.
//
// NUM_BANKS == 1 (flat mode):
//   Falls back to the original single-backing-store implementation; no
//   conflict can ever occur.  Use this as the no-banking baseline.
//
// Conflict statistics outputs:
//   bank_conflict_detected          -- pulsed whenever ≥1 port is stalled
//   stats_bank_conflicts            -- cumulative conflict-event count
//   stats_bank_conflict_stall_cycles -- total stalled port-cycles
//
// For Vivado synthesis the banked array maps to one BRAM macro per bank.
//=============================================================================

module scratchpad_ram #(
    parameter int DATA_WIDTH = 32,
    parameter int DEPTH      = 4096,
    parameter int N_PORTS    = 4,
    parameter int NUM_BANKS  = 4     // 1 = flat (no banking); power-of-two
) (
    input  logic                              clk,
    input  logic                              rst_n,

    // Read ports
    input  logic [N_PORTS-1:0]                rd_en,
    input  logic [$clog2(DEPTH)-1:0]          rd_addr  [N_PORTS],
    output logic [DATA_WIDTH-1:0]             rd_data  [N_PORTS],
    output logic [N_PORTS-1:0]                rd_valid,

    // Write ports
    input  logic [N_PORTS-1:0]                wr_en,
    input  logic [$clog2(DEPTH)-1:0]          wr_addr  [N_PORTS],
    input  logic [DATA_WIDTH-1:0]             wr_data  [N_PORTS],

    // Bank-conflict monitoring outputs
    output logic                              bank_conflict_detected,
    output logic [31:0]                       stats_bank_conflicts,
    output logic [31:0]                       stats_bank_conflict_stall_cycles
);

    generate
        // ------------------------------------------------------------------
        // FLAT (single-bank) path -- identical to original behaviour,
        // zero conflict overhead, used as a conflict-free baseline.
        // ------------------------------------------------------------------
        if (NUM_BANKS == 1) begin : g_flat

            logic [DATA_WIDTH-1:0] mem [DEPTH];
            integer i;

            always_ff @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    rd_valid <= '0;
                    for (i = 0; i < N_PORTS; i++) rd_data[i] <= '0;
                end else begin
                    for (i = 0; i < N_PORTS; i++) begin
                        rd_valid[i] <= rd_en[i];
                        if (rd_en[i]) rd_data[i] <= mem[rd_addr[i]];
                    end
                end
            end

            always_ff @(posedge clk) begin
                for (i = 0; i < N_PORTS; i++) begin
                    if (wr_en[i]) mem[wr_addr[i]] <= wr_data[i];
                end
            end

            assign bank_conflict_detected           = 1'b0;
            assign stats_bank_conflicts             = 32'd0;
            assign stats_bank_conflict_stall_cycles = 32'd0;

        // ------------------------------------------------------------------
        // BANKED path -- interleaved multi-bank with conflict detection.
        // NUM_BANKS must be a power of two ≥ 2.
        // ------------------------------------------------------------------
        end else begin : g_banked

            localparam int SEL_W  = $clog2(NUM_BANKS); // bank-select bit width
            localparam int BDEPTH = DEPTH / NUM_BANKS;  // words per bank

            logic [DATA_WIDTH-1:0] mem [NUM_BANKS][BDEPTH];

            // Decode address into bank-select and within-bank offset
            logic [SEL_W-1:0]              rd_bid  [N_PORTS];
            logic [$clog2(BDEPTH)-1:0]     rd_boff [N_PORTS];
            logic [SEL_W-1:0]              wr_bid  [N_PORTS];
            logic [$clog2(BDEPTH)-1:0]     wr_boff [N_PORTS];

            always_comb begin
                for (int p = 0; p < N_PORTS; p++) begin
                    // Low SEL_W bits → bank id (interleaved mapping)
                    rd_bid[p]  = rd_addr[p][SEL_W-1:0];
                    rd_boff[p] = rd_addr[p][$clog2(DEPTH)-1:SEL_W];
                    wr_bid[p]  = wr_addr[p][SEL_W-1:0];
                    wr_boff[p] = wr_addr[p][$clog2(DEPTH)-1:SEL_W];
                end
            end

            // Conflict detection: port i conflicts if any earlier active port
            // targets the same bank.  Lower-indexed port wins (priority scheme).
            logic [N_PORTS-1:0] rd_conflict;
            logic [N_PORTS-1:0] rd_served;   // ports actually granted this cycle

            always_comb begin
                for (int i = 0; i < N_PORTS; i++) begin
                    rd_conflict[i] = 1'b0;
                    if (rd_en[i]) begin
                        for (int j = 0; j < i; j++) begin
                            if (rd_en[j] && (rd_bid[j] == rd_bid[i]))
                                rd_conflict[i] = 1'b1;
                        end
                    end
                    rd_served[i] = rd_en[i] & ~rd_conflict[i];
                end
            end

            assign bank_conflict_detected = |rd_conflict;

            // Synchronous reads: conflicting ports are held off (rd_valid=0).
            // The caller must re-assert rd_en the following cycle to retry.
            always_ff @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    rd_valid <= '0;
                    for (int i = 0; i < N_PORTS; i++) rd_data[i] <= '0;
                end else begin
                    for (int i = 0; i < N_PORTS; i++) begin
                        rd_valid[i] <= rd_served[i];
                        if (rd_served[i])
                            rd_data[i] <= mem[rd_bid[i]][rd_boff[i]];
                    end
                end
            end

            // Synchronous writes: if two ports target the same bank+offset,
            // the highest-indexed port wins (consistent with original semantics).
            always_ff @(posedge clk) begin
                for (int i = 0; i < N_PORTS; i++) begin
                    if (wr_en[i]) mem[wr_bid[i]][wr_boff[i]] <= wr_data[i];
                end
            end

            // Count stalled ports per conflict cycle for the stall-cycle metric
            logic [$clog2(N_PORTS+1)-1:0] conflict_port_count;
            always_comb begin
                conflict_port_count = '0;
                for (int i = 0; i < N_PORTS; i++)
                    if (rd_conflict[i])
                        conflict_port_count = conflict_port_count + 1'b1;
            end

            always_ff @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    stats_bank_conflicts             <= 32'd0;
                    stats_bank_conflict_stall_cycles <= 32'd0;
                end else if (bank_conflict_detected) begin
                    stats_bank_conflicts             <= stats_bank_conflicts + 1;
                    stats_bank_conflict_stall_cycles <= stats_bank_conflict_stall_cycles
                                                     + 32'(conflict_port_count);
                end
            end

        end
    endgenerate

endmodule : scratchpad_ram
