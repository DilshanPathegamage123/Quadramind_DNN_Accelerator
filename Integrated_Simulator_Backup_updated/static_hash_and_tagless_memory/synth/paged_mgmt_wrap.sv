//=============================================================================
// Module: paged_mgmt_wrap
//
// Synthesis harness that isolates the *management logic* of the page-table
// (dynamic) memory scheme, so its FPGA area can be compared fairly against
// the stamp (static) scheme's management logic.
//
// Both schemes need the same scratchpad SRAM, so the scratchpad is excluded
// from both sides of the comparison and synthesised separately. What differs
// is:
//
//   dynamic (PAGED) : N_PORTS address-translation tables, queried on every
//                     access                       <-- this module
//   static  (STAMP) : one delta-op sequencer + its metadata RAM, run once per
//                     phase                        <-- stamp_based_memory_controller
//
// This module is verification/characterisation infrastructure. It is not part
// of the datapath and is never instantiated by the design.
//=============================================================================

module paged_mgmt_wrap #(
    parameter int N_PORTS        = 4,
    parameter int VADDR_WIDTH    = 32,
    parameter int PADDR_WIDTH    = 32,
    parameter int PAGE_SIZE_BITS = 12,
    parameter int NUM_PAGES      = 256,
    parameter int VPN_WIDTH      = 8,
    parameter int PPN_WIDTH      = 20
) (
    input  logic                    clk,
    input  logic                    rst_n,

    // One translation request per read port
    input  logic [VADDR_WIDTH-1:0]  vaddr [N_PORTS],
    output logic [PADDR_WIDTH-1:0]  paddr [N_PORTS],
    output logic [N_PORTS-1:0]      hit,

    // Page-table update port, broadcast to every port's table
    input  logic                    pt_write_en,
    input  logic [VPN_WIDTH-1:0]    pt_write_vpn,
    input  logic [PPN_WIDTH-1:0]    pt_write_ppn,
    input  logic                    pt_write_valid,

    // Hit/miss counters, matching paged_memory_backend
    output logic [31:0]             stats_page_hits,
    output logic [31:0]             stats_page_misses
);

    logic [N_PORTS-1:0] tx_valid;

    genvar p;
    generate
        for (p = 0; p < N_PORTS; p++) begin : g_pt
            page_table #(
                .VADDR_WIDTH    (VADDR_WIDTH),
                .PADDR_WIDTH    (PADDR_WIDTH),
                .PAGE_SIZE_BITS (PAGE_SIZE_BITS),
                .NUM_PAGES      (NUM_PAGES),
                .VPN_WIDTH      (VPN_WIDTH),
                .PPN_WIDTH      (PPN_WIDTH)
            ) u_pt (
                .clk         (clk),
                .rst_n       (rst_n),
                .vaddr       (vaddr[p]),
                .paddr       (paddr[p]),
                .hit         (hit[p]),
                .valid       (tx_valid[p]),
                .write_en    (pt_write_en),
                .write_vpn   (pt_write_vpn),
                .write_ppn   (pt_write_ppn),
                .write_valid (pt_write_valid)
            );
        end
    endgenerate

    // Same counting scheme as the fixed paged_memory_backend: tally the active
    // ports combinationally, then add once per cycle.
    logic [$clog2(N_PORTS+1)-1:0] hit_count, miss_count;
    always_comb begin
        hit_count  = '0;
        miss_count = '0;
        for (int i = 0; i < N_PORTS; i++) begin
            if (hit[i]) hit_count  = hit_count  + 1'b1;
            else        miss_count = miss_count + 1'b1;
        end
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            stats_page_hits   <= '0;
            stats_page_misses <= '0;
        end else begin
            stats_page_hits   <= stats_page_hits   + 32'(hit_count);
            stats_page_misses <= stats_page_misses + 32'(miss_count);
        end
    end

endmodule : paged_mgmt_wrap
