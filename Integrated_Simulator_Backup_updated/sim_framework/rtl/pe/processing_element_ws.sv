//=============================================================================
// Module: processing_element_ws
// Description: Single PE for weight stationary systolic array
//              Weight stays fixed, inputs broadcast horizontally,
//              partial sums flow diagonally
//=============================================================================

module processing_element_ws #(
    parameter int DATA_WIDTH = 32,
    parameter int ACCUM_WIDTH = 48
) (
    input  logic                    clk,
    input  logic                    rst_n,
    
    // Control
    input  logic                    enable,
    input  logic                    clear_accum,
    
    // Input activation (broadcast from left)
    input  logic [DATA_WIDTH-1:0]   activation_in,
    input  logic                    activation_valid_in,
    
    // Weight (stationary - loaded once)
    input  logic [DATA_WIDTH-1:0]   weight,
    input  logic                    weight_valid,
    
    // Partial sum (from upper-left diagonal
    input  logic [ACCUM_WIDTH-1:0]  psum_in,
    input  logic                    psum_valid_in,
    
    // Outputs
    output logic [DATA_WIDTH-1:0]   activation_out,
    output logic                    activation_valid_out,
    output logic [ACCUM_WIDTH-1:0]  psum_out,
    output logic                    psum_valid_out,
    output logic [ACCUM_WIDTH-1:0]  result  // Final accumulated result
);

    // Internal registers
    logic [DATA_WIDTH-1:0]   weight_reg;
    logic [ACCUM_WIDTH-1:0]  accumulator;
    logic [ACCUM_WIDTH-1:0]  product;
    logic [ACCUM_WIDTH-1:0]  mac_result;

    // MAC operation. The local accumulator (read by writeback via `result`)
    // accumulates only this PE's own products; psum_in is forwarded on the
    // diagonal chain only. Folding psum_in into the accumulation corrupts
    // every PE off the top/left boundary (finding F8, WS instance).
    always_comb begin
        product    = $signed(activation_in) * $signed(weight_reg);
        mac_result = $signed(product) + $signed(psum_in);
    end
    
    // Weight register (stationary - loaded once and stays)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            weight_reg <= '0;
        end else if (weight_valid) begin
            weight_reg <= weight;
        end
    end
    
    // Accumulator (for final result in this PE)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            accumulator <= '0;
        end else if (clear_accum) begin
            accumulator <= '0;
        end else if (enable && activation_valid_in && psum_valid_in) begin
            accumulator <= accumulator + product;
        end
    end
    
    // Broadcast activation horizontally (to right neighbor)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            activation_out <= '0;
            activation_valid_out <= 1'b0;
        end else begin
            activation_out <= activation_in;
            activation_valid_out <= activation_valid_in;
        end
    end
    
    // Pass partial sum diagonally (to lower-right neighbor)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            psum_out <= '0;
            psum_valid_out <= 1'b0;
        end else if (enable && activation_valid_in && psum_valid_in) begin
            psum_out <= mac_result;
            psum_valid_out <= 1'b1;
        end else begin
            psum_valid_out <= 1'b0;
        end
    end
    
    // Output accumulated result
    assign result = accumulator;

endmodule : processing_element_ws
