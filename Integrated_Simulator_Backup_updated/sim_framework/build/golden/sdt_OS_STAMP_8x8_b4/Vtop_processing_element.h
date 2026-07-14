// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtop.h for the primary calling header

#ifndef VERILATED_VTOP_PROCESSING_ELEMENT_H_
#define VERILATED_VTOP_PROCESSING_ELEMENT_H_  // guard

#include "verilated.h"


class Vtop__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtop_processing_element final {
  public:

    // DESIGN SPECIFIC STATE
    CData/*0:0*/ clk;
    CData/*0:0*/ rst_n;
    CData/*0:0*/ enable;
    CData/*0:0*/ clear_accum;
    CData/*0:0*/ activation_valid_in;
    CData/*0:0*/ weight_valid;
    CData/*0:0*/ psum_valid_in;
    CData/*0:0*/ activation_valid_out;
    CData/*0:0*/ psum_valid_out;
    IData/*31:0*/ activation_in;
    IData/*31:0*/ weight;
    IData/*31:0*/ activation_out;
    IData/*31:0*/ weight_reg;
    QData/*47:0*/ psum_in;
    QData/*47:0*/ psum_out;
    QData/*47:0*/ result;
    QData/*47:0*/ accumulator;
    QData/*47:0*/ mac_result;

    // INTERNAL VARIABLES
    Vtop__Syms* vlSymsp;
    const char* vlNamep;

    // PARAMETERS
    static constexpr IData/*31:0*/ DATA_WIDTH = 0x00000020U;
    static constexpr IData/*31:0*/ ACCUM_WIDTH = 0x00000030U;

    // CONSTRUCTORS
    Vtop_processing_element();
    ~Vtop_processing_element();
    void ctor(Vtop__Syms* symsp, const char* namep);
    void dtor();
    VL_UNCOPYABLE(Vtop_processing_element);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
