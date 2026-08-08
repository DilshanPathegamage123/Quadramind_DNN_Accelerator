//=============================================================================
// Module: dram_model
// Description: Bandwidth- and latency-limited off-chip memory responder.
//
// Why this exists: the original framework had no time cost for memory at all
// (software_ref.estimate_cycles is a pure compute formula, and bytes_loaded is
// never converted into cycles).  With free memory there is nothing for AI-MT
// to hide, so its overlap can never pay.  This module gives memory a real
// cost:
//
//     service_cycles = cfg_latency + ceil(req_bytes / cfg_bytes_per_cycle)
//
// Both knobs are runtime inputs rather than parameters so a bandwidth sweep
// does not require re-elaboration.
//
// Interface is a simple request/response pair: raise req_valid with req_bytes
// while req_ready is high, then wait for the one-cycle resp_valid pulse.
//=============================================================================

`timescale 1ns/1ps

module dram_model #(
    parameter int BYTE_WIDTH = 32   // width of the byte-count fields
) (
    input  logic                    clk,
    input  logic                    rst_n,

    //--- Runtime configuration
    input  logic [15:0]             cfg_latency,          // cycles to first beat
    input  logic [15:0]             cfg_bytes_per_cycle,  // sustained bandwidth

    //--- Request / response
    input  logic                    req_valid,
    input  logic [BYTE_WIDTH-1:0]   req_bytes,
    output logic                    req_ready,
    output logic                    resp_valid,           // 1-cycle completion pulse

    //--- Status / stats
    output logic                    busy,
    output logic [31:0]             stats_requests,
    output logic [63:0]             stats_bytes_served,
    output logic [31:0]             stats_busy_cycles
);

    typedef enum logic [1:0] { M_IDLE, M_LATENCY, M_XFER } mstate_t;
    mstate_t state;

    logic [BYTE_WIDTH-1:0] remaining;
    logic [15:0]           lat_ctr;

    // A zero-byte request still costs the latency, never zero cycles.
    logic [15:0] bw_eff;
    always_comb bw_eff = (cfg_bytes_per_cycle == 16'd0) ? 16'd1 : cfg_bytes_per_cycle;

    assign req_ready = (state == M_IDLE);
    assign busy      = (state != M_IDLE);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state              <= M_IDLE;
            remaining          <= '0;
            lat_ctr            <= '0;
            resp_valid         <= 1'b0;
            stats_requests     <= '0;
            stats_bytes_served <= '0;
            stats_busy_cycles  <= '0;
        end else begin
            resp_valid <= 1'b0;

            if (state != M_IDLE)
                stats_busy_cycles <= stats_busy_cycles + 32'd1;

            case (state)
                M_IDLE: begin
                    if (req_valid) begin
                        remaining      <= req_bytes;
                        lat_ctr        <= cfg_latency;
                        stats_requests <= stats_requests + 32'd1;
                        state          <= (cfg_latency == 16'd0) ? M_XFER : M_LATENCY;
                    end
                end

                M_LATENCY: begin
                    if (lat_ctr <= 16'd1) state   <= M_XFER;
                    else                  lat_ctr <= lat_ctr - 16'd1;
                end

                M_XFER: begin
                    if (remaining <= {{(BYTE_WIDTH-16){1'b0}}, bw_eff}) begin
                        // Final (possibly partial) beat retires this cycle.
                        stats_bytes_served <= stats_bytes_served + 64'(remaining);
                        remaining          <= '0;
                        resp_valid         <= 1'b1;
                        state              <= M_IDLE;
                    end else begin
                        stats_bytes_served <= stats_bytes_served + 64'(bw_eff);
                        remaining          <= remaining -
                                              {{(BYTE_WIDTH-16){1'b0}}, bw_eff};
                    end
                end

                default: state <= M_IDLE;
            endcase
        end
    end

endmodule : dram_model
