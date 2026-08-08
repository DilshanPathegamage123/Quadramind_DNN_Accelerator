//=============================================================================
// Module: mt_engine  --  Memory Task engine (the DMA half of the accelerator)
//
// One of the two INDEPENDENT execution resources that make AI-MT's overlap
// physically possible.  It owns the off-chip port and nothing else; it never
// touches the systolic array, so it can run concurrently with ct_engine.
//
// Byte accounting -- this is where batching earns its keep:
//
//     bytes = weight_bytes + batch * ifmap_bytes
//
// Weights are fetched ONCE for the whole batch; only the feature maps scale
// with it.  So per-inference memory traffic is (weight/B + ifmap), which falls
// as B grows.  That is precisely the BATCH-DNN thesis, and it is why a
// batching scheduler can beat AI-MT on a memory-bound mix.
//
// `start` is a one-cycle pulse; `done` likewise.  `busy` is the level the top
// counts to measure DMA utilisation and MT/CT overlap.
//=============================================================================

`timescale 1ns/1ps

module mt_engine #(
    parameter int MEM_WIDTH   = 32,
    parameter int BATCH_WIDTH = 8
) (
    input  logic                    clk,
    input  logic                    rst_n,

    //--- Runtime DRAM configuration (forwarded to dram_model)
    input  logic [15:0]             cfg_latency,
    input  logic [15:0]             cfg_bytes_per_cycle,

    //--- Task issue
    input  logic                    start,           // 1-cycle pulse
    input  logic [MEM_WIDTH-1:0]    weight_bytes,    // loaded once per batch
    input  logic [MEM_WIDTH-1:0]    ifmap_bytes,     // scales with batch
    input  logic [BATCH_WIDTH-1:0]  batch,

    //--- Completion
    output logic                    done,            // 1-cycle pulse
    output logic                    busy,

    //--- Stats
    output logic [31:0]             stats_tasks,
    output logic [63:0]             stats_bytes,
    output logic [31:0]             stats_busy_cycles,
    output logic [31:0]             dram_requests
);

    typedef enum logic [1:0] { E_IDLE, E_REQ, E_WAIT } estate_t;
    estate_t state;

    logic [MEM_WIDTH-1:0] req_bytes_q;

    // dram_model handshake
    logic                 dm_req_valid;
    logic [MEM_WIDTH-1:0] dm_req_bytes;
    logic                 dm_req_ready;
    logic                 dm_resp_valid;
    logic                 dm_busy;
    logic [63:0]          dm_bytes_served;
    logic [31:0]          dm_busy_cycles;

    dram_model #(
        .BYTE_WIDTH (MEM_WIDTH)
    ) u_dram (
        .clk                 (clk),
        .rst_n               (rst_n),
        .cfg_latency         (cfg_latency),
        .cfg_bytes_per_cycle (cfg_bytes_per_cycle),
        .req_valid           (dm_req_valid),
        .req_bytes           (dm_req_bytes),
        .req_ready           (dm_req_ready),
        .resp_valid          (dm_resp_valid),
        .busy                (dm_busy),
        .stats_requests      (dram_requests),
        .stats_bytes_served  (dm_bytes_served),
        .stats_busy_cycles   (dm_busy_cycles)
    );

    assign dm_req_valid = (state == E_REQ);
    assign dm_req_bytes = req_bytes_q;
    assign busy         = (state != E_IDLE);

    // bytes = weight + batch * ifmap   (weights amortised across the batch)
    logic [MEM_WIDTH-1:0] bytes_calc;
    always_comb begin
        automatic logic [BATCH_WIDTH-1:0] b_eff;
        b_eff      = (batch == '0) ? BATCH_WIDTH'(1) : batch;
        bytes_calc = weight_bytes + MEM_WIDTH'(ifmap_bytes * b_eff);
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state             <= E_IDLE;
            req_bytes_q       <= '0;
            done              <= 1'b0;
            stats_tasks       <= '0;
            stats_bytes       <= '0;
            stats_busy_cycles <= '0;
        end else begin
            done <= 1'b0;

            if (state != E_IDLE)
                stats_busy_cycles <= stats_busy_cycles + 32'd1;

            case (state)
                E_IDLE: begin
                    if (start) begin
                        req_bytes_q <= bytes_calc;
                        stats_tasks <= stats_tasks + 32'd1;
                        stats_bytes <= stats_bytes + 64'(bytes_calc);
                        state       <= E_REQ;
                    end
                end

                E_REQ: begin
                    if (dm_req_ready) state <= E_WAIT;
                end

                E_WAIT: begin
                    if (dm_resp_valid) begin
                        done  <= 1'b1;
                        state <= E_IDLE;
                    end
                end

                default: state <= E_IDLE;
            endcase
        end
    end

endmodule : mt_engine
