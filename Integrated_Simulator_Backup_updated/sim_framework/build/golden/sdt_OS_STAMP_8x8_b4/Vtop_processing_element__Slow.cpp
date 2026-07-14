// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"

// Parameter definitions for Vtop_processing_element
constexpr IData/*31:0*/ Vtop_processing_element::DATA_WIDTH;
constexpr IData/*31:0*/ Vtop_processing_element::ACCUM_WIDTH;


void Vtop_processing_element___ctor_var_reset(Vtop_processing_element* vlSelf);

Vtop_processing_element::Vtop_processing_element() = default;
Vtop_processing_element::~Vtop_processing_element() = default;

void Vtop_processing_element::ctor(Vtop__Syms* symsp, const char* namep) {
    vlSymsp = symsp;
    vlNamep = strdup(Verilated::catName(vlSymsp->name(), namep));
    // Reset structure values
    Vtop_processing_element___ctor_var_reset(this);
}

void Vtop_processing_element::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

void Vtop_processing_element::dtor() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
