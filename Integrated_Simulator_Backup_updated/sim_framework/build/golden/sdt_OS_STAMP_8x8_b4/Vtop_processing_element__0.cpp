// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)(vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][0U];
    vlSelfRef.clear_accum = (1U & (IData)(vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear));
    vlSelfRef.enable = (1U & (IData)(vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable));
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U]);
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][0U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U]);
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][0U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*47:0*/ __Vdly__accumulator;
    __Vdly__accumulator = 0;
    // Body
    __Vdly__accumulator = vlSelfRef.accumulator;
    if (vlSelfRef.rst_n) {
        if (vlSelfRef.clear_accum) {
            __Vdly__accumulator = 0ULL;
        } else if (((IData)(vlSelfRef.enable) & (IData)(vlSelfRef.activation_valid_in))) {
            __Vdly__accumulator = (0x0000ffffffffffffULL 
                                   & (vlSelfRef.accumulator 
                                      + vlSelfRef.mac_result));
        }
        if (vlSelfRef.weight_valid) {
            vlSelfRef.weight_reg = vlSelfRef.weight;
        }
        vlSelfRef.activation_out = vlSelfRef.activation_in;
        if (((IData)(vlSelfRef.enable) & (IData)(vlSelfRef.activation_valid_in))) {
            vlSelfRef.psum_out = vlSelfRef.mac_result;
        }
    } else {
        __Vdly__accumulator = 0ULL;
        vlSelfRef.weight_reg = 0U;
        vlSelfRef.activation_out = 0U;
        vlSelfRef.psum_out = 0ULL;
    }
    vlSelfRef.psum_valid_out = ((IData)(vlSelfRef.rst_n) 
                                && (((IData)(vlSelfRef.enable) 
                                     & (IData)(vlSelfRef.activation_valid_in)) 
                                    && (IData)(vlSelfRef.psum_valid_in)));
    vlSelfRef.activation_valid_out = ((IData)(vlSelfRef.rst_n) 
                                      && (IData)(vlSelfRef.activation_valid_in));
    vlSelfRef.accumulator = __Vdly__accumulator;
    vlSelfRef.result = vlSelfRef.accumulator;
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)(vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear));
    vlSelfRef.weight_valid = (1U & (IData)(vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][0U];
    vlSelfRef.enable = (1U & (IData)(vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][0U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][0U];
    vlSelfRef.psum_valid_in = (1U & vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U]);
    vlSelfRef.activation_valid_in = (1U & vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U]);
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 1U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 1U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 1U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][1U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 1U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][1U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 1U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][1U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 1U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 1U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][1U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 1U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][1U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][1U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 1U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 1U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 2U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 2U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 2U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][2U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 2U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][2U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 2U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][2U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 2U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 2U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][2U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 2U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][2U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][2U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 2U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 2U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 3U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 3U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 3U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][3U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 3U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][3U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 3U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][3U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 3U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 3U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][3U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 3U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][3U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][3U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 3U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 3U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 4U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 4U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 4U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][4U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 4U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][4U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 4U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][4U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 4U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 4U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][4U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 4U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][4U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][4U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 4U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 4U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 5U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 5U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 5U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][5U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 5U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][5U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 5U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][5U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 5U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 5U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][5U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 5U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][5U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][5U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 5U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 5U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 6U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 6U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 6U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][6U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 6U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][6U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 6U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][6U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 6U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 6U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][6U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 6U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][6U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][6U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 6U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 6U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 7U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 7U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 7U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][7U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 7U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][7U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 7U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][7U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 7U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 7U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[0U][7U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 7U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[0U][7U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[0U][7U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 7U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 7U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 8U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 8U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 8U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][0U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 9U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][0U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 8U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][0U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 8U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 8U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][0U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 8U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][0U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][0U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 9U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 8U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 9U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 9U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 9U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][1U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000000aU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][1U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 9U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][1U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 9U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 9U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][1U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 9U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][1U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][1U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000000aU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 9U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000000aU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000000aU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000000aU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][2U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000000bU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][2U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000000aU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][2U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000000aU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000000aU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][2U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000000aU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][2U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][2U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000000bU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000000aU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000000bU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000000bU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000000bU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][3U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000000cU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][3U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000000bU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][3U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000000bU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000000bU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][3U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000000bU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][3U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][3U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000000cU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000000bU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000000cU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000000cU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000000cU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][4U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000000dU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][4U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000000cU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][4U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000000cU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000000cU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][4U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000000cU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][4U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][4U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000000dU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000000cU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000000dU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000000dU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000000dU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][5U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000000eU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][5U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000000dU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][5U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000000dU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000000dU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][5U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000000dU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][5U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][5U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000000eU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000000dU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000000eU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000000eU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000000eU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][6U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000000fU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][6U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000000eU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][6U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000000eU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000000eU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][6U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000000eU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][6U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][6U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000000fU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000000eU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000000fU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000000fU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000000fU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][7U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000010U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][7U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000000fU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][7U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000000fU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000000fU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[1U][7U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000000fU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[1U][7U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[1U][7U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000010U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000000fU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000010U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000010U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000010U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][0U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000012U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][0U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000010U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][0U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000010U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000010U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][0U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000010U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][0U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][0U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000012U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000010U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000011U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000011U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000011U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][1U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000013U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][1U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000011U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][1U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000011U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000011U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][1U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000011U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][1U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][1U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000013U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000011U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000012U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000012U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000012U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][2U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000014U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][2U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000012U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][2U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000012U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000012U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][2U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000012U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][2U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][2U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000014U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000012U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000013U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000013U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000013U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][3U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000015U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][3U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000013U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][3U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000013U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000013U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][3U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000013U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][3U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][3U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000015U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000013U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000014U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000014U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000014U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][4U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000016U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][4U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000014U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][4U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000014U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000014U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][4U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000014U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][4U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][4U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000016U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000014U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000015U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000015U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000015U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][5U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000017U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][5U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000015U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][5U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000015U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000015U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][5U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000015U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][5U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][5U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000017U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000015U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000016U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000016U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000016U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][6U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000018U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][6U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000016U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][6U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000016U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000016U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][6U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000016U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][6U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][6U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000018U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000016U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000017U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000017U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000017U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][7U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000019U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][7U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000017U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][7U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000017U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000017U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[2U][7U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000017U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[2U][7U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[2U][7U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x00000019U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000017U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000018U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000018U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000018U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][0U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000001bU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][0U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000018U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][0U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000018U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000018U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][0U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000018U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][0U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][0U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000001bU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000018U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000019U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000019U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000019U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][1U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000001cU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][1U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000019U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][1U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000019U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000019U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][1U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000019U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][1U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][1U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000001cU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x00000019U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000001aU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000001aU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000001aU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][2U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000001dU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][2U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000001aU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][2U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000001aU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000001aU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][2U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000001aU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][2U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][2U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000001dU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000001aU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000001bU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000001bU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000001bU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][3U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000001eU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][3U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000001bU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][3U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000001bU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000001bU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][3U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000001bU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][3U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][3U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                                     >> 0x0000001eU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000001bU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000001cU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000001cU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000001cU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][4U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                               >> 0x0000001fU);
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][4U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000001cU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][4U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000001cU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000001cU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][4U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000001cU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][4U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][4U];
    vlSelfRef.psum_valid_in = (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[0U] 
                               >> 0x0000001fU);
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000001cU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000001dU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000001dU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000001dU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][5U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U]);
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][5U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000001dU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][5U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000001dU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000001dU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][5U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000001dU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][5U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][5U];
    vlSelfRef.psum_valid_in = (1U & vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U]);
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000001dU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000001eU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000001eU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000001eU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][6U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 1U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][6U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000001eU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][6U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000001eU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000001eU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][6U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000001eU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][6U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][6U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 1U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                           >> 0x0000001eU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000001fU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000001fU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000001fU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][7U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 2U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][7U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                     >> 0x0000001fU);
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][7U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000001fU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000001fU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[3U][7U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000001fU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[3U][7U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[3U][7U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 2U));
    vlSelfRef.activation_valid_in = (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[0U] 
                                     >> 0x0000001fU);
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000020U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000020U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000020U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][0U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 4U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][0U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U]);
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][0U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000020U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000020U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][0U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000020U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][0U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][0U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 4U));
    vlSelfRef.activation_valid_in = (1U & vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U]);
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000021U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000021U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000021U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][1U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 5U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][1U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 1U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][1U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000021U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000021U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][1U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000021U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][1U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][1U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 5U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 1U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000022U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000022U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000022U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][2U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 6U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][2U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 2U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][2U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000022U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000022U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][2U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000022U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][2U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][2U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 6U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 2U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000023U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000023U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000023U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][3U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 7U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][3U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 3U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][3U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000023U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000023U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][3U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000023U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][3U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][3U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 7U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 3U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000024U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000024U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000024U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][4U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 8U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][4U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 4U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][4U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000024U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000024U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][4U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000024U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][4U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][4U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 8U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 4U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000025U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000025U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000025U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][5U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 9U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][5U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 5U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][5U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000025U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000025U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][5U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000025U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][5U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][5U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 9U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 5U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000026U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000026U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000026U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][6U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000000aU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][6U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 6U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][6U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000026U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000026U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][6U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000026U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][6U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][6U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000000aU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 6U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000027U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000027U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000027U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][7U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000000bU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][7U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 7U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][7U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000027U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000027U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[4U][7U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000027U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[4U][7U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[4U][7U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000000bU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 7U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000028U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000028U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000028U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][0U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000000dU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][0U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 8U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][0U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000028U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000028U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][0U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000028U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][0U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][0U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000000dU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 8U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000029U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000029U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000029U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][1U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000000eU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][1U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 9U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][1U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000029U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000029U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][1U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000029U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][1U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][1U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000000eU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 9U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000002aU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000002aU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000002aU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][2U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000000fU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][2U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000000aU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][2U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000002aU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000002aU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][2U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000002aU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][2U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][2U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000000fU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000000aU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000002bU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000002bU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000002bU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][3U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000010U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][3U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000000bU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][3U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000002bU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000002bU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][3U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000002bU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][3U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][3U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000010U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000000bU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000002cU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000002cU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000002cU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][4U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000011U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][4U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000000cU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][4U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000002cU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000002cU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][4U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000002cU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][4U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][4U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000011U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000000cU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000002dU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000002dU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000002dU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][5U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000012U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][5U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000000dU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][5U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000002dU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000002dU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][5U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000002dU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][5U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][5U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000012U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000000dU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000002eU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000002eU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000002eU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][6U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000013U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][6U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000000eU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][6U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000002eU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000002eU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][6U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000002eU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][6U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][6U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000013U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000000eU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000002fU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000002fU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000002fU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][7U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000014U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][7U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000000fU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][7U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000002fU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000002fU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[5U][7U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000002fU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[5U][7U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[5U][7U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000014U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000000fU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000030U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000030U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000030U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][0U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000016U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][0U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000010U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][0U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000030U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000030U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][0U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000030U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][0U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][0U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000016U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000010U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000031U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000031U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000031U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][1U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000017U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][1U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000011U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][1U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000031U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000031U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][1U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000031U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][1U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][1U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000017U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000011U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000032U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000032U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000032U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][2U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000018U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][2U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000012U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][2U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000032U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000032U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][2U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000032U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][2U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][2U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000018U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000012U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000033U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000033U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000033U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][3U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000019U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][3U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000013U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][3U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000033U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000033U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][3U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000033U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][3U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][3U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x00000019U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000013U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000034U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000034U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000034U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][4U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000001aU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][4U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000014U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][4U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000034U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000034U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][4U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000034U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][4U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][4U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000001aU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000014U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000035U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000035U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000035U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][5U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000001bU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][5U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000015U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][5U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000035U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000035U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][5U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000035U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][5U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][5U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000001bU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000015U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000036U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000036U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000036U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][6U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000001cU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][6U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000016U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][6U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000036U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000036U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][6U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000036U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][6U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][6U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000001cU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000016U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000037U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000037U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000037U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][7U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000001dU));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][7U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000017U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][7U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000037U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000037U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[6U][7U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000037U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[6U][7U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[6U][7U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                                     >> 0x0000001dU));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000017U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000038U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000038U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000038U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][0U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                               >> 0x0000001fU);
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][0U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000018U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][0U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000038U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000038U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][0U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000038U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][0U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][0U];
    vlSelfRef.psum_valid_in = (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[1U] 
                               >> 0x0000001fU);
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000018U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000039U)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000039U)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000039U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][1U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[2U]);
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][1U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000019U));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][1U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x00000039U)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x00000039U)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][1U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x00000039U)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][1U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][1U];
    vlSelfRef.psum_valid_in = (1U & vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[2U]);
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x00000019U));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000003aU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000003aU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000003aU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][2U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[2U] 
                                     >> 1U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][2U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000001aU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][2U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000003aU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000003aU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][2U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000003aU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][2U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][2U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[2U] 
                                     >> 1U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000001aU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000003bU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000003bU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000003bU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][3U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[2U] 
                                     >> 2U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][3U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000001bU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][3U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000003bU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000003bU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][3U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000003bU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][3U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][3U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[2U] 
                                     >> 2U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000001bU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000003cU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000003cU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000003cU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][4U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[2U] 
                                     >> 3U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][4U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000001cU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][4U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000003cU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000003cU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][4U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000003cU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][4U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][4U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[2U] 
                                     >> 3U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000001cU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000003dU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000003dU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000003dU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][5U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[2U] 
                                     >> 4U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][5U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000001dU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][5U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000003dU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000003dU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][5U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000003dU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][5U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][5U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[2U] 
                                     >> 4U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000001dU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000003eU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000003eU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000003eU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][6U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[2U] 
                                     >> 5U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][6U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000001eU));
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][6U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000003eU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000003eU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][6U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000003eU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][6U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][6U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[2U] 
                                     >> 5U));
    vlSelfRef.activation_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                           >> 0x0000001eU));
}

void Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ico_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000003fU)));
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000003fU)));
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000003fU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][7U];
    vlSelfRef.result = vlSelfRef.accumulator;
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[2U] 
                                     >> 6U));
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][7U];
    vlSelfRef.clk = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__clk;
    vlSelfRef.rst_n = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__rst_n;
    vlSelfRef.activation_valid_in = (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                     >> 0x0000001fU);
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][7U];
    vlSelfRef.mac_result = (0x0000ffffffffffffULL & 
                            (vlSelfRef.psum_in + VL_MULS_QQQ(48, 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.activation_in)), 
                                                             (0x0000ffffffffffffULL 
                                                              & VL_EXTENDS_QI(48,32, vlSelfRef.weight_reg)))));
}

void Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_sequent__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__1\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.clear_accum = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_clear 
                                           >> 0x0000003fU)));
    vlSelfRef.weight_valid = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight_valid 
                                            >> 0x0000003fU)));
    vlSelfRef.weight = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_weight[7U][7U];
    vlSelfRef.enable = (1U & (IData)((vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_enable 
                                      >> 0x0000003fU)));
}

void Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___nba_comb__TOP__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.activation_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation[7U][7U];
    vlSelfRef.psum_in = vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum[7U][7U];
    vlSelfRef.psum_valid_in = (1U & (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_psum_valid[2U] 
                                     >> 6U));
    vlSelfRef.activation_valid_in = (vlSymsp->TOP.single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__pe_activation_valid[1U] 
                                     >> 0x0000001fU);
}
