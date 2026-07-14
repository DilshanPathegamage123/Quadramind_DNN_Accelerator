// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtop.h for the primary calling header

#ifndef VERILATED_VTOP_STAMP_MEMORY_PKG_H_
#define VERILATED_VTOP_STAMP_MEMORY_PKG_H_  // guard

#include "verilated.h"


class Vtop__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtop_stamp_memory_pkg final {
  public:

    // INTERNAL VARIABLES
    Vtop__Syms* vlSymsp;
    const char* vlNamep;

    // PARAMETERS
    static constexpr CData/*7:0*/ OP_KEEP = 0U;
    static constexpr CData/*7:0*/ OP_MOVE = 1U;
    static constexpr CData/*7:0*/ OP_LOAD = 2U;

    // CONSTRUCTORS
    Vtop_stamp_memory_pkg();
    ~Vtop_stamp_memory_pkg();
    void ctor(Vtop__Syms* symsp, const char* namep);
    void dtor();
    VL_UNCOPYABLE(Vtop_stamp_memory_pkg);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
