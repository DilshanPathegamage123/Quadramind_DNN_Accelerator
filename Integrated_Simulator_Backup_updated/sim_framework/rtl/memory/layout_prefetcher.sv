//=============================================================================
// Module: layout_prefetcher
//
// Purpose (layout fix): during the memory phase, walk the layer's weight and
// input tiles element-by-element IN FETCH ORDER through the layout-dependent
// address mapping (the same formulas the array's fetchers use), coalesce
// consecutive addresses into AXI bursts, and issue REAL AXI read requests
// for them. Storage-order contiguity therefore becomes physically different
// off-chip traffic per layout:
//   CHANNEL_MAJOR: fetch order is address-contiguous  -> long bursts
//   ROW_MAJOR:     stride C between consecutive fetches -> short bursts
//   COLUMN_MAJOR:  stride H*C                           -> single-beat bursts
//
// The read DATA is consumed (rready held high) but not forwarded to the
// array: the compute data plane still uses the ext_* direct ports ("v1
// wiring" in single_dnn_top). This module changes off-chip traffic and
// memory-phase timing only - never computed values.
//
// Walk order (mirrors the OS fetchers):
//   phase 0 weights: r (array row / out_ch) outer, then c -> kh -> kw
//                    (out_ch = tile_ch_start + r; rows with out_ch >= K skip)
//   phase 1 inputs:  ch outer, then kh -> kw -> col (0..ARRAY_WIDTH-1)
//                    element = (ch, tile_row + kh, tile_col_start + col + kw)
//
// Casting scheme (how a shared value maps to off-chip reads):
//   CAST_MULTICAST: one read per unique value. Weights: 1 read/element.
//                   Inputs: the per-column window walk is replaced by a
//                   dedup walk over the tile's unique halo footprint
//                   (kw held at 0, col sweeps 0..ARRAY_WIDTH+KW-2), so
//                   window-overlap duplicates are fetched once.
//   CAST_UNICAST:   one read per consuming PE. Each weight element is
//                   re-issued ARRAY_WIDTH times (row-broadcast consumers);
//                   each input (tuple,col) request is re-issued
//                   ARRAY_HEIGHT times (column-ripple consumers).
//                   Repeated identical addresses never coalesce (the run
//                   test requires addr == last+1), so every replica is a
//                   distinct AXI AR transaction - by design.
//   CAST_HYBRID:    weights multicast, inputs unicast.
//=============================================================================

module layout_prefetcher
    import sim_framework_pkg::*;
#(
    parameter int ADDR_WIDTH   = 32,
    parameter int ARRAY_HEIGHT = 4,
    parameter int ARRAY_WIDTH  = 4,
    parameter int MAX_BURST    = 16      // max beats per coalesced AXI burst
) (
    input  logic clk,
    input  logic rst_n,

    // Configuration (same ports the array fetchers see)
    input  mem_layout_t           layout,
    input  casting_t              casting,
    input  logic [15:0]           input_c, input_h, input_w,
    input  logic [15:0]           weight_k, weight_c, weight_kh, weight_kw,
    input  logic [ADDR_WIDTH-1:0] input_base_addr, weight_base_addr,
    input  logic [15:0]           tile_row, tile_col_start, tile_ch_start,

    // Control
    input  logic start,
    output logic busy,
    output logic done,          // 1-cycle pulse

    // AXI read master
    output logic [ADDR_WIDTH-1:0] axi_araddr,
    output logic [7:0]            axi_arlen,
    output logic                  axi_arvalid,
    input  logic                  axi_arready,
    input  logic                  axi_rvalid,
    input  logic                  axi_rlast,
    output logic                  axi_rready
);

    typedef enum logic [2:0] { PF_IDLE, PF_SCAN, PF_ISSUE, PF_DATA, PF_DONE } pf_t;
    pf_t state;

    // walk counters
    logic        phase;                       // 0 = weights, 1 = inputs
    logic [15:0] w_r, w_c, w_kh, w_kw;        // weight walk
    logic [15:0] i_ch, i_kh, i_kw, i_col;     // input walk
    logic [15:0] w_rep, i_rep;                // per-consumer replica counters
    logic        walk_done;

    // casting mode decode
    wire wt_unicast = (casting == CAST_UNICAST);
    wire in_unicast = (casting == CAST_UNICAST) || (casting == CAST_HYBRID);
    // multicast inputs: dedup walk over the halo footprint (kw pinned at 0,
    // col sweeps the union of col+kw positions)
    wire [15:0] i_col_last = in_unicast ? 16'(ARRAY_WIDTH - 1)
                                        : 16'(ARRAY_WIDTH - 1) + (weight_kw - 16'd1);

    // burst run under construction
    logic                  run_valid;
    logic [ADDR_WIDTH-1:0] run_start, run_last;
    logic [7:0]            run_len;           // beats-1
    logic                  pend_valid;
    logic [ADDR_WIDTH-1:0] pend_addr;
    logic                  final_issue;

    // ------------------------------------------------------------------
    // Current element address (combinational; mirrors the fetchers' math)
    // ------------------------------------------------------------------
    logic [31:0] cur_off;
    logic [ADDR_WIDTH-1:0] cur_addr;
    logic cur_skip;
    logic [15:0] och, ih_pos, iw_pos;

    always_comb begin
        cur_off  = '0;
        cur_skip = 1'b0;
        och      = tile_ch_start + w_r;
        ih_pos   = tile_row + i_kh;
        iw_pos   = tile_col_start + i_col + i_kw;

        if (!phase) begin
            // weight element (out_ch = och, c = w_c, kh = w_kh, kw = w_kw)
            cur_skip = (och >= weight_k);
            case (layout)
                CHANNEL_MAJOR: // [K, C, KH, KW]
                    cur_off = 32'(och)  * (32'(weight_c) * 32'(weight_kh) * 32'(weight_kw))
                            + 32'(w_c)  * (32'(weight_kh) * 32'(weight_kw))
                            + 32'(w_kh) *  32'(weight_kw)
                            + 32'(w_kw);
                ROW_MAJOR:     // [K, KH, KW, C]
                    cur_off = 32'(och)  * (32'(weight_kh) * 32'(weight_kw) * 32'(weight_c))
                            + 32'(w_kh) * (32'(weight_kw) * 32'(weight_c))
                            + 32'(w_kw) *  32'(weight_c)
                            + 32'(w_c);
                COLUMN_MAJOR:  // [K, KW, KH, C]
                    cur_off = 32'(och)  * (32'(weight_kw) * 32'(weight_kh) * 32'(weight_c))
                            + 32'(w_kw) * (32'(weight_kh) * 32'(weight_c))
                            + 32'(w_kh) *  32'(weight_c)
                            + 32'(w_c);
                default: cur_off = '0;
            endcase
            cur_addr = weight_base_addr + ADDR_WIDTH'(cur_off);
        end else begin
            // input element (c = i_ch, h = ih_pos, w = iw_pos)
            case (layout)
                CHANNEL_MAJOR: // c*(H*W) + h*W + w
                    cur_off = 32'(i_ch)   * (32'(input_h) * 32'(input_w))
                            + 32'(ih_pos) *  32'(input_w)
                            + 32'(iw_pos);
                ROW_MAJOR:     // h*(W*C) + w*C + c
                    cur_off = 32'(ih_pos) * (32'(input_w) * 32'(input_c))
                            + 32'(iw_pos) *  32'(input_c)
                            + 32'(i_ch);
                COLUMN_MAJOR:  // w*(H*C) + h*C + c
                    cur_off = 32'(iw_pos) * (32'(input_h) * 32'(input_c))
                            + 32'(ih_pos) *  32'(input_c)
                            + 32'(i_ch);
                default: cur_off = '0;
            endcase
            cur_addr = input_base_addr + ADDR_WIDTH'(cur_off);
        end
    end

    // ------------------------------------------------------------------
    // Walk advance helpers (one element consumed per PF_SCAN cycle)
    // ------------------------------------------------------------------
    // weight walk: rep -> kw -> kh -> c -> r; then phase 1
    //   (rep only advances under CAST_UNICAST: one replica per consuming
    //    column PE of the row-broadcast weight)
    // input walk:  rep -> col -> kw -> kh -> ch; then walk_done
    //   (rep only under UNICAST/HYBRID: one replica per consuming row PE of
    //    the column ripple; under MULTICAST kw is pinned at 0 and col sweeps
    //    the dedup halo footprint 0..ARRAY_WIDTH+KW-2)
    task automatic advance_walk();
        if (!phase) begin
            if (wt_unicast && w_rep != 16'(ARRAY_WIDTH - 1)) w_rep <= w_rep + 1;
            else begin
                w_rep <= '0;
                if (w_kw != weight_kw - 1) w_kw <= w_kw + 1;
                else begin
                    w_kw <= '0;
                    if (w_kh != weight_kh - 1) w_kh <= w_kh + 1;
                    else begin
                        w_kh <= '0;
                        if (w_c != weight_c - 1) w_c <= w_c + 1;
                        else begin
                            w_c <= '0;
                            if (w_r != 16'(ARRAY_HEIGHT - 1)) w_r <= w_r + 1;
                            else begin
                                w_r  <= '0;
                                phase <= 1'b1;
                            end
                        end
                    end
                end
            end
        end else begin
            if (in_unicast && i_rep != 16'(ARRAY_HEIGHT - 1)) i_rep <= i_rep + 1;
            else begin
                i_rep <= '0;
                if (i_col != i_col_last) i_col <= i_col + 1;
                else begin
                    i_col <= '0;
                    if (in_unicast && i_kw != weight_kw - 1) i_kw <= i_kw + 1;
                    else begin
                        i_kw <= '0;
                        if (i_kh != weight_kh - 1) i_kh <= i_kh + 1;
                        else begin
                            i_kh <= '0;
                            if (i_ch != input_c - 1) i_ch <= i_ch + 1;
                            else walk_done <= 1'b1;
                        end
                    end
                end
            end
        end
    endtask

    // ------------------------------------------------------------------
    // Main FSM
    // ------------------------------------------------------------------
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= PF_IDLE;
            phase <= 1'b0; walk_done <= 1'b0;
            w_r <= '0; w_c <= '0; w_kh <= '0; w_kw <= '0;
            i_ch <= '0; i_kh <= '0; i_kw <= '0; i_col <= '0;
            w_rep <= '0; i_rep <= '0;
            run_valid <= 1'b0; run_start <= '0; run_last <= '0; run_len <= '0;
            pend_valid <= 1'b0; pend_addr <= '0;
            final_issue <= 1'b0;
            axi_arvalid <= 1'b0; axi_araddr <= '0; axi_arlen <= '0;
            done <= 1'b0;
        end else begin
            done <= 1'b0;
            case (state)
                PF_IDLE: begin
                    if (start) begin
                        phase <= 1'b0; walk_done <= 1'b0;
                        w_r <= '0; w_c <= '0; w_kh <= '0; w_kw <= '0;
                        i_ch <= '0; i_kh <= '0; i_kw <= '0; i_col <= '0;
                        w_rep <= '0; i_rep <= '0;
                        run_valid <= 1'b0; pend_valid <= 1'b0;
                        final_issue <= 1'b0;
                        state <= PF_SCAN;
                    end
                end

                PF_SCAN: begin
                    if (pend_valid) begin
                        // absorb the element that broke the previous run
                        run_start  <= pend_addr;
                        run_last   <= pend_addr;
                        run_len    <= '0;
                        run_valid  <= 1'b1;
                        pend_valid <= 1'b0;
                    end else if (walk_done) begin
                        if (run_valid) begin
                            axi_araddr  <= run_start;
                            axi_arlen   <= run_len;
                            axi_arvalid <= 1'b1;
                            final_issue <= 1'b1;
                            state       <= PF_ISSUE;
                        end else begin
                            done  <= 1'b1;
                            state <= PF_DONE;
                        end
                    end else if (cur_skip) begin
                        advance_walk();
                    end else if (!run_valid) begin
                        run_start <= cur_addr;
                        run_last  <= cur_addr;
                        run_len   <= '0;
                        run_valid <= 1'b1;
                        advance_walk();
                    end else if (cur_addr == run_last + 1 &&
                                 run_len != 8'(MAX_BURST - 1)) begin
                        run_last <= cur_addr;
                        run_len  <= run_len + 1;
                        advance_walk();
                    end else begin
                        // discontinuity (or burst full): issue current run
                        pend_addr   <= cur_addr;
                        pend_valid  <= 1'b1;
                        axi_araddr  <= run_start;
                        axi_arlen   <= run_len;
                        axi_arvalid <= 1'b1;
                        advance_walk();
                        state <= PF_ISSUE;
                    end
                end

                PF_ISSUE: begin
                    if (axi_arready) begin
                        axi_arvalid <= 1'b0;
                        state       <= PF_DATA;
                    end
                end

                PF_DATA: begin
                    if (axi_rvalid && axi_rlast) begin
                        run_valid <= 1'b0;
                        if (final_issue) begin
                            done  <= 1'b1;
                            state <= PF_DONE;
                        end else begin
                            state <= PF_SCAN;
                        end
                    end
                end

                PF_DONE: state <= PF_IDLE;

                default: state <= PF_IDLE;
            endcase
        end
    end

    assign busy       = (state != PF_IDLE) && (state != PF_DONE);
    assign axi_rready = (state == PF_DATA);

endmodule : layout_prefetcher
