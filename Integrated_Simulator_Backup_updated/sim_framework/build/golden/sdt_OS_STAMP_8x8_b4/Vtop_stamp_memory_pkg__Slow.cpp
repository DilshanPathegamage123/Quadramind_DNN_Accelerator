// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"

// Parameter definitions for Vtop_stamp_memory_pkg
constexpr CData/*7:0*/ Vtop_stamp_memory_pkg::OP_KEEP;
constexpr CData/*7:0*/ Vtop_stamp_memory_pkg::OP_MOVE;
constexpr CData/*7:0*/ Vtop_stamp_memory_pkg::OP_LOAD;



Vtop_stamp_memory_pkg::Vtop_stamp_memory_pkg() = default;
Vtop_stamp_memory_pkg::~Vtop_stamp_memory_pkg() = default;

void Vtop_stamp_memory_pkg::ctor(Vtop__Syms* symsp, const char* namep) {
    vlSymsp = symsp;
    vlNamep = strdup(Verilated::catName(vlSymsp->name(), namep));
    // Reset structure values
}

void Vtop_stamp_memory_pkg::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

void Vtop_stamp_memory_pkg::dtor() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
