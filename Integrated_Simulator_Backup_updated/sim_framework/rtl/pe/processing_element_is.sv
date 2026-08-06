//=============================================================================
// Module: processing_element_is
// Description: Single PE for input stationary systolic array
//              Input stays fixed in PE, weights stream horizontally,
//              partial sums accumulate vertically and written back per column
//
// Input Stationary Dataflow:
//   - Inputs: Loaded once into each PE and remain stationary
//   - Weights: Stream horizontally across each row
//   - Partial sums: Flow vertically downward through each column
//   - Best for: High input reuse, spatially-local feature maps
//=============================================================================

module processing_element_is #(
    parameter int DATA_WIDTH  = 32,
    parameter int ACCUM_WIDTH = 48
) (
    input  logic                    clk,
    input  logic                    rst_n,

    // Control
    input  logic                    enable,
    input  logic                    clear_accum,
    input  logic                    load_input,    // Strobe: latch activation_in → input_reg

    // Input activation (stationary - loaded once, held in register)
    input  logic [DATA_WIDTH-1:0]   activation_in,
    input  logic                    activation_valid_in,

    // Weight (streams horizontally from left)
    input  logic [DATA_WIDTH-1:0]   weight_in,
    input  logic                    weight_valid_in,

    // Partial sum (flows vertically from PE above)
    input  logic [ACCUM_WIDTH-1:0]  psum_in,
    input  logic                    psum_valid_in,

    // Outputs
    output logic [DATA_WIDTH-1:0]   weight_out,        // Pass weight rightward
    output logic                    weight_valid_out,

    output logic [ACCUM_WIDTH-1:0]  psum_out,          // Pass psum downward
    output logic                    psum_valid_out,

    output logic [ACCUM_WIDTH-1:0]  result             // Final accumulated result
);

    // Internal registers
    logic [DATA_WIDTH-1:0]   input_reg;    // Stationary input value
    logic [ACCUM_WIDTH-1:0]  accumulator;
    logic [ACCUM_WIDTH-1:0]  product;
    logic [ACCUM_WIDTH-1:0]  mac_result;

    // MAC operation. The local accumulator (read by writeback via `result`)
    // accumulates only this PE's own products; psum_in stays on the vertical
    // forwarding chain (finding F8, IS instance). This also removes the
    // psum_valid gating from the accumulate: the vertical valid chain lags
    // each row's weight pulse by one cycle, which silently disabled every
    // row below row 0 when all rows are streamed simultaneously.
    always_comb begin
        product    = $signed(input_reg) * $signed(weight_in);
        mac_result = $signed(product) + $signed(psum_in);
    end

    // Input register (stationary). Loadable via the LOAD_INPUTS strobe and
    // also re-loadable while the PE is enabled during weight streaming
    // (finding F3): without the reload path one pass can only ever apply a
    // single stationary value against all C*KH*KW weights, which cannot
    // form a convolution.
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            input_reg <= '0;
        end else if ((load_input || enable) && activation_valid_in) begin
            input_reg <= activation_in;
        end
    end

    // Accumulator (captures running partial sum in this PE)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            accumulator <= '0;
        end else if (clear_accum) begin
            accumulator <= '0;
        end else if (enable && weight_valid_in) begin
            accumulator <= accumulator + product;
        end
    end

    // Pass weight horizontally to the right neighbour
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            weight_out       <= '0;
            weight_valid_out <= 1'b0;
        end else begin
            weight_out       <= weight_in;
            weight_valid_out <= weight_valid_in;
        end
    end

    // Pass partial sum vertically downward
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            psum_out       <= '0;
            psum_valid_out <= 1'b0;
        end else if (enable && weight_valid_in && psum_valid_in) begin
            psum_out       <= mac_result;
            psum_valid_out <= 1'b1;
        end else begin
            psum_valid_out <= 1'b0;
        end
    end

    // Final accumulated result (readable at any time)
    assign result = accumulator;

endmodule : processing_element_is
