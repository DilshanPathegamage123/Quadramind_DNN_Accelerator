// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Model implementation (design independent parts)

#include "Vtop__pch.h"

//============================================================
// Constructors

Vtop::Vtop(VerilatedContext* _vcontextp__, const char* _vcname__)
    : VerilatedModel{*_vcontextp__}
    , vlSymsp{new Vtop__Syms(contextp(), _vcname__, this)}
    , clk{vlSymsp->TOP.clk}
    , rst_n{vlSymsp->TOP.rst_n}
    , mem_layout{vlSymsp->TOP.mem_layout}
    , start{vlSymsp->TOP.start}
    , done{vlSymsp->TOP.done}
    , busy{vlSymsp->TOP.busy}
    , phase_mem_done{vlSymsp->TOP.phase_mem_done}
    , phase_compute_done{vlSymsp->TOP.phase_compute_done}
    , metadata_wr_en{vlSymsp->TOP.metadata_wr_en}
    , metadata_wr_addr{vlSymsp->TOP.metadata_wr_addr}
    , phase_start_in{vlSymsp->TOP.phase_start_in}
    , pt_write_en{vlSymsp->TOP.pt_write_en}
    , pt_write_vpn{vlSymsp->TOP.pt_write_vpn}
    , pt_write_valid{vlSymsp->TOP.pt_write_valid}
    , axi_arlen{vlSymsp->TOP.axi_arlen}
    , axi_arvalid{vlSymsp->TOP.axi_arvalid}
    , axi_arready{vlSymsp->TOP.axi_arready}
    , axi_rvalid{vlSymsp->TOP.axi_rvalid}
    , axi_rready{vlSymsp->TOP.axi_rready}
    , axi_rlast{vlSymsp->TOP.axi_rlast}
    , ext_input_addr_valid_w{vlSymsp->TOP.ext_input_addr_valid_w}
    , ext_input_data_valid_w{vlSymsp->TOP.ext_input_data_valid_w}
    , ext_input_addr_valid_h{vlSymsp->TOP.ext_input_addr_valid_h}
    , ext_input_data_valid_h{vlSymsp->TOP.ext_input_data_valid_h}
    , ext_weight_addr_valid_1d{vlSymsp->TOP.ext_weight_addr_valid_1d}
    , ext_weight_data_valid_1d{vlSymsp->TOP.ext_weight_data_valid_1d}
    , ext_weight_addr_valid_2d{vlSymsp->TOP.ext_weight_addr_valid_2d}
    , ext_weight_data_valid_2d{vlSymsp->TOP.ext_weight_data_valid_2d}
    , ext_output_addr_valid_2d{vlSymsp->TOP.ext_output_addr_valid_2d}
    , ext_output_data_valid_2d{vlSymsp->TOP.ext_output_data_valid_2d}
    , ext_output_addr_valid_1d{vlSymsp->TOP.ext_output_addr_valid_1d}
    , ext_output_data_valid_1d{vlSymsp->TOP.ext_output_data_valid_1d}
    , input_channels{vlSymsp->TOP.input_channels}
    , input_height{vlSymsp->TOP.input_height}
    , input_width{vlSymsp->TOP.input_width}
    , weight_k{vlSymsp->TOP.weight_k}
    , weight_c{vlSymsp->TOP.weight_c}
    , weight_kh{vlSymsp->TOP.weight_kh}
    , weight_kw{vlSymsp->TOP.weight_kw}
    , output_channels{vlSymsp->TOP.output_channels}
    , output_height{vlSymsp->TOP.output_height}
    , output_width{vlSymsp->TOP.output_width}
    , tile_row{vlSymsp->TOP.tile_row}
    , tile_col_start{vlSymsp->TOP.tile_col_start}
    , tile_ch_start{vlSymsp->TOP.tile_ch_start}
    , ws_input_ch{vlSymsp->TOP.ws_input_ch}
    , ws_kernel_row{vlSymsp->TOP.ws_kernel_row}
    , ws_kernel_col_start{vlSymsp->TOP.ws_kernel_col_start}
    , phase_id_in{vlSymsp->TOP.phase_id_in}
    , num_delta_ops_in{vlSymsp->TOP.num_delta_ops_in}
    , phase_base_addr_in{vlSymsp->TOP.phase_base_addr_in}
    , input_base_addr{vlSymsp->TOP.input_base_addr}
    , weight_base_addr{vlSymsp->TOP.weight_base_addr}
    , output_base_addr{vlSymsp->TOP.output_base_addr}
    , metadata_wr_data{vlSymsp->TOP.metadata_wr_data}
    , pt_write_ppn{vlSymsp->TOP.pt_write_ppn}
    , axi_arvalid_addr{vlSymsp->TOP.axi_arvalid_addr}
    , axi_rdata{vlSymsp->TOP.axi_rdata}
    , stats_loads_or_hits{vlSymsp->TOP.stats_loads_or_hits}
    , stats_moves_or_misses{vlSymsp->TOP.stats_moves_or_misses}
    , stats_keeps{vlSymsp->TOP.stats_keeps}
    , stats_bytes_loaded{vlSymsp->TOP.stats_bytes_loaded}
    , stats_bytes_moved{vlSymsp->TOP.stats_bytes_moved}
    , stats_compute_cycles{vlSymsp->TOP.stats_compute_cycles}
    , ext_input_addr_w{vlSymsp->TOP.ext_input_addr_w}
    , ext_input_data_w{vlSymsp->TOP.ext_input_data_w}
    , ext_input_addr_h{vlSymsp->TOP.ext_input_addr_h}
    , ext_input_data_h{vlSymsp->TOP.ext_input_data_h}
    , ext_weight_addr_1d{vlSymsp->TOP.ext_weight_addr_1d}
    , ext_weight_data_1d{vlSymsp->TOP.ext_weight_data_1d}
    , ext_weight_addr_2d{vlSymsp->TOP.ext_weight_addr_2d}
    , ext_weight_data_2d{vlSymsp->TOP.ext_weight_data_2d}
    , ext_output_addr_2d{vlSymsp->TOP.ext_output_addr_2d}
    , ext_output_data_2d{vlSymsp->TOP.ext_output_data_2d}
    , ext_output_addr_1d{vlSymsp->TOP.ext_output_addr_1d}
    , ext_output_data_1d{vlSymsp->TOP.ext_output_data_1d}
    , __PVT__stamp_memory_pkg{vlSymsp->TOP.__PVT__stamp_memory_pkg}
    , __PVT__sim_framework_pkg{vlSymsp->TOP.__PVT__sim_framework_pkg}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst}
    , __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst{vlSymsp->TOP.__PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst}
    , rootp{&(vlSymsp->TOP)}
{
    // Register model with the context
    contextp()->addModel(this);
}

Vtop::Vtop(const char* _vcname__)
    : Vtop(Verilated::threadContextp(), _vcname__)
{
}

//============================================================
// Destructor

Vtop::~Vtop() {
    delete vlSymsp;
}

//============================================================
// Evaluation function

#ifdef VL_DEBUG
void Vtop___024root___eval_debug_assertions(Vtop___024root* vlSelf);
#endif  // VL_DEBUG
void Vtop___024root___eval_static(Vtop___024root* vlSelf);
void Vtop___024root___eval_initial(Vtop___024root* vlSelf);
void Vtop___024root___eval_settle(Vtop___024root* vlSelf);
void Vtop___024root___eval(Vtop___024root* vlSelf);

void Vtop::eval_step() {
    VL_DEBUG_IF(VL_DBG_MSGF("+++++TOP Evaluate Vtop::eval_step\n"); );
#ifdef VL_DEBUG
    // Debug assertions
    Vtop___024root___eval_debug_assertions(&(vlSymsp->TOP));
#endif  // VL_DEBUG
    vlSymsp->__Vm_deleter.deleteAll();
    if (VL_UNLIKELY(!vlSymsp->__Vm_didInit)) {
        VL_DEBUG_IF(VL_DBG_MSGF("+ Initial\n"););
        Vtop___024root___eval_static(&(vlSymsp->TOP));
        Vtop___024root___eval_initial(&(vlSymsp->TOP));
        Vtop___024root___eval_settle(&(vlSymsp->TOP));
        vlSymsp->__Vm_didInit = true;
    }
    VL_DEBUG_IF(VL_DBG_MSGF("+ Eval\n"););
    Vtop___024root___eval(&(vlSymsp->TOP));
    // Evaluate cleanup
    Verilated::endOfEval(vlSymsp->__Vm_evalMsgQp);
}

//============================================================
// Events and timing
bool Vtop::eventsPending() { return false; }

uint64_t Vtop::nextTimeSlot() {
    VL_FATAL_MT(__FILE__, __LINE__, "", "No delays in the design");
    return 0;
}

//============================================================
// Utilities

const char* Vtop::name() const {
    return vlSymsp->name();
}

//============================================================
// Invoke final blocks

void Vtop___024root___eval_final(Vtop___024root* vlSelf);

VL_ATTR_COLD void Vtop::final() {
    contextp()->executingFinal(true);
    Vtop___024root___eval_final(&(vlSymsp->TOP));
    contextp()->executingFinal(false);
}

//============================================================
// Implementations of abstract methods from VerilatedModel

const char* Vtop::hierName() const { return vlSymsp->name(); }
const char* Vtop::modelName() const { return "Vtop"; }
unsigned Vtop::threads() const { return 1; }
void Vtop::prepareClone() const { contextp()->prepareClone(); }
void Vtop::atClone() const {
    contextp()->threadPoolpOnClone();
}
