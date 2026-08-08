//=============================================================================
// Module: ct_engine  --  Compute Task engine (the systolic-array half)
//
// The second INDEPENDENT execution resource.  It owns the PE array and the
// on-chip buffer read ports; it never issues an off-chip request, so it can
// run concurrently with mt_engine.  That independence is the whole point --
// in the original multi_dnn_top there was one shared resource and a
// run-to-completion FSM, so an MT could never overlap a CT.
//
// Occupancy model:
//
//     cycles = cycles_per_batch * batch + ARRAY_FILL_DRAIN
//
// Compute scales linearly with batch (every inference does its own MACs),
// while mt_engine's byte cost does NOT scale the weight term.  The asymmetry
// between those two lines is exactly what a batching scheduler exploits.
//
// ARRAY_FILL_DRAIN is the systolic pipeline fill+drain, paid once per
// dispatched task rather than per inference -- so batching also amortises the
// pipeline bubble, a second (smaller) reason larger batches win.
//=============================================================================

`timescale 1ns/1ps

module ct_engine #(
    parameter int CYCLE_WIDTH = 32,
    parameter int BATCH_WIDTH = 8
) (
    input  logic                    clk,
    input  logic                    rst_n,

    //--- Array geometry: pipeline fill + drain, paid once per dispatch
    input  logic [15:0]             cfg_fill_drain,

    //--- Task issue
    input  logic                    start,             // 1-cycle pulse
    input  logic [CYCLE_WIDTH-1:0]  cycles_per_batch,  // MAC cycles for ONE inference
    input  logic [BATCH_WIDTH-1:0]  batch,

    //--- Completion
    output logic                    done,              // 1-cycle pulse
    output logic                    busy,

    //--- Stats
    output logic [31:0]             stats_tasks,
    output logic [63:0]             stats_inferences,
    output logic [31:0]             stats_busy_cycles
);

    typedef enum logic [0:0] { C_IDLE, C_RUN } cstate_t;
    cstate_t state;

    logic [CYCLE_WIDTH-1:0] remaining;

    assign busy = (state != C_IDLE);

    logic [CYCLE_WIDTH-1:0] cycles_calc;
    logic [BATCH_WIDTH-1:0] batch_eff;
    always_comb begin
        batch_eff   = (batch == '0) ? BATCH_WIDTH'(1) : batch;
        cycles_calc = CYCLE_WIDTH'(cycles_per_batch * batch_eff) +
                      CYCLE_WIDTH'(cfg_fill_drain);
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state             <= C_IDLE;
            remaining         <= '0;
            done              <= 1'b0;
            stats_tasks       <= '0;
            stats_inferences  <= '0;
            stats_busy_cycles <= '0;
        end else begin
            done <= 1'b0;

            if (state != C_IDLE)
                stats_busy_cycles <= stats_busy_cycles + 32'd1;

            case (state)
                C_IDLE: begin
                    if (start) begin
                        // A task always occupies the array for >= 1 cycle.
                        remaining        <= (cycles_calc == '0) ? CYCLE_WIDTH'(1)
                                                                : cycles_calc;
                        stats_tasks      <= stats_tasks + 32'd1;
                        stats_inferences <= stats_inferences + 64'(batch_eff);
                        state            <= C_RUN;
                    end
                end

                C_RUN: begin
                    if (remaining <= CYCLE_WIDTH'(1)) begin
                        remaining <= '0;
                        done      <= 1'b1;
                        state     <= C_IDLE;
                    end else begin
                        remaining <= remaining - CYCLE_WIDTH'(1);
                    end
                end

                default: state <= C_IDLE;
            endcase
        end
    end

endmodule : ct_engine
