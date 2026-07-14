// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"

VL_ATTR_COLD void Vtop_processing_element___ctor_var_reset(Vtop_processing_element* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtop_processing_element___ctor_var_reset\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->clk = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16707436170211756652ull);
    vlSelf->rst_n = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1638864771569018232ull);
    vlSelf->enable = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11030669854614834172ull);
    vlSelf->clear_accum = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15487476412549094114ull);
    vlSelf->activation_in = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9131938757397554059ull);
    vlSelf->activation_valid_in = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7052532065763578313ull);
    vlSelf->weight = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14629473433807880010ull);
    vlSelf->weight_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4809823684574151013ull);
    vlSelf->psum_in = VL_SCOPED_RAND_RESET_Q(48, __VscopeHash, 7829686683607283609ull);
    vlSelf->psum_valid_in = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14269774895728449257ull);
    vlSelf->activation_out = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8415456637915070068ull);
    vlSelf->activation_valid_out = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5396576976884848759ull);
    vlSelf->psum_out = VL_SCOPED_RAND_RESET_Q(48, __VscopeHash, 6077996691324072374ull);
    vlSelf->psum_valid_out = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2521158571471204470ull);
    vlSelf->result = VL_SCOPED_RAND_RESET_Q(48, __VscopeHash, 16664408842984530663ull);
    vlSelf->weight_reg = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4557041961183947728ull);
    vlSelf->accumulator = VL_SCOPED_RAND_RESET_Q(48, __VscopeHash, 635851360026796673ull);
    vlSelf->mac_result = VL_SCOPED_RAND_RESET_Q(48, __VscopeHash, 15471305799828506445ull);
}
