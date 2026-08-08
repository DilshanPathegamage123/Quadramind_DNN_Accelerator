// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table implementation internals

#include "Vtb_multi_dnn_exec__pch.h"

Vtb_multi_dnn_exec__Syms::Vtb_multi_dnn_exec__Syms(VerilatedContext* contextp, const char* namep, Vtb_multi_dnn_exec* modelp)
    : VerilatedSyms{contextp}
    // Setup internal state of the Syms class
    , __Vm_modelp{modelp}
    // Setup top module instance
    , TOP{this, namep}
{
    // Check resources
    Verilated::stackCheck(4127);
    // Setup sub module instances
    // Configure time unit / time precision
    _vm_contextp__->timeunit(-9);
    _vm_contextp__->timeprecision(-12);
    // Setup each module's pointers to their submodules
    // Setup each module's pointer back to symbol table (for public functions)
    TOP.__Vconfigure(true);
    // Setup scopes
}

Vtb_multi_dnn_exec__Syms::~Vtb_multi_dnn_exec__Syms() {
    // Tear down scopes
    // Tear down sub module instances
}
