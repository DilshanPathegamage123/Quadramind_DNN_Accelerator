// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_multi_dnn_exec.h for the primary calling header

#include "Vtb_multi_dnn_exec__pch.h"

void Vtb_multi_dnn_exec___024root___ctor_var_reset(Vtb_multi_dnn_exec___024root* vlSelf);

Vtb_multi_dnn_exec___024root::Vtb_multi_dnn_exec___024root(Vtb_multi_dnn_exec__Syms* symsp, const char* namep)
    : __VdlySched{*symsp->_vm_contextp__}
 {
    vlSymsp = symsp;
    vlNamep = strdup(namep);
    // Reset structure values
    Vtb_multi_dnn_exec___024root___ctor_var_reset(this);
}

void Vtb_multi_dnn_exec___024root::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

Vtb_multi_dnn_exec___024root::~Vtb_multi_dnn_exec___024root() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
