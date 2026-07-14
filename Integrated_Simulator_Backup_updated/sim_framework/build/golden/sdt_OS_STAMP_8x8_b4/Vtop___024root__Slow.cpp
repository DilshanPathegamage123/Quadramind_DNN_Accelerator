// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"

// Parameter definitions for Vtop___024root
constexpr CData/*1:0*/ Vtop___024root::single_dnn_top__DOT__DATAFLOW;
constexpr CData/*0:0*/ Vtop___024root::single_dnn_top__DOT__MEMORY;
constexpr CData/*1:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__DATAFLOW;
constexpr CData/*0:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__MEMORY;
constexpr SData/*15:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_stamp_ctrl__DOT__MAX_AXI_BURST_WORDS;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__ARRAY_HEIGHT;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__ARRAY_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__ACCUM_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__ADDR_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__SPAD_DEPTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__AXI_DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__METADATA_DEPTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__NUM_PAGES;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__PAGE_SIZE_BITS;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__VPN_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__PPN_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__N_MEM_PORTS;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__ARRAY_HEIGHT;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__ARRAY_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__ACCUM_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__ADDR_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__ARRAY_HEIGHT;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__ARRAY_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__ACCUM_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__ADDR_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__input_fetch_inst__DOT__ARRAY_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__input_fetch_inst__DOT__DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__input_fetch_inst__DOT__MAX_CHANNELS;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__input_fetch_inst__DOT__MAX_KERNEL;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__input_fetch_inst__DOT__addr_gen_inst__DOT__DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__output_fetch_inst__DOT__ARRAY_HEIGHT;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__output_fetch_inst__DOT__ARRAY_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__output_fetch_inst__DOT__DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__weight_fetch_inst__DOT__ARRAY_HEIGHT;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__weight_fetch_inst__DOT__DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__weight_fetch_inst__DOT__MAX_CHANNELS;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__weight_fetch_inst__DOT__MAX_KERNEL;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__ADDR_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__SPAD_DEPTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__AXI_DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__N_PORTS;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__METADATA_DEPTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__NUM_PAGES;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__PAGE_SIZE_BITS;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__VPN_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__PPN_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__NUM_BANKS;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__ADDR_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__SPAD_DEPTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__AXI_DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__N_PORTS;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__METADATA_DEPTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__NUM_BANKS;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_spad__DOT__DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_spad__DOT__DEPTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_spad__DOT__N_PORTS;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_spad__DOT__NUM_BANKS;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_spad__DOT__g_banked__DOT__SEL_W;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_spad__DOT__g_banked__DOT__BDEPTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_axi_read__DOT__ADDR_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_axi_read__DOT__DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_stamp_ctrl__DOT__ADDR_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_stamp_ctrl__DOT__DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_stamp_ctrl__DOT__SPAD_DEPTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_stamp_ctrl__DOT__AXI_DATA_WIDTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_stamp_ctrl__DOT__MAX_DELTA_OPS;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_stamp_ctrl__DOT__METADATA_DEPTH;
constexpr IData/*31:0*/ Vtop___024root::single_dnn_top__DOT__u_mem__DOT__g_stamp__DOT__u_stamp__DOT__u_stamp_ctrl__DOT__BPW;


void Vtop___024root___ctor_var_reset(Vtop___024root* vlSelf);

Vtop___024root::Vtop___024root(Vtop__Syms* symsp, const char* namep)
 {
    vlSymsp = symsp;
    vlNamep = strdup(namep);
    // Reset structure values
    Vtop___024root___ctor_var_reset(this);
}

void Vtop___024root::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

Vtop___024root::~Vtop___024root() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
