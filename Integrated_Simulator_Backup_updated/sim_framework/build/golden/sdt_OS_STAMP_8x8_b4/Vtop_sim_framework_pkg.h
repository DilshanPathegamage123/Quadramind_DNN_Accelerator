// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtop.h for the primary calling header

#ifndef VERILATED_VTOP_SIM_FRAMEWORK_PKG_H_
#define VERILATED_VTOP_SIM_FRAMEWORK_PKG_H_  // guard

#include "verilated.h"


class Vtop__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtop_sim_framework_pkg final {
  public:

    // INTERNAL VARIABLES
    Vtop__Syms* vlSymsp;
    const char* vlNamep;

    // PARAMETERS
    static constexpr CData/*4:0*/ SCHED_FIFO = 0U;
    static constexpr CData/*4:0*/ SCHED_LIFO = 1U;
    static constexpr CData/*4:0*/ SCHED_SJF = 2U;
    static constexpr CData/*4:0*/ SCHED_RR = 3U;
    static constexpr CData/*4:0*/ SCHED_PRI = 4U;
    static constexpr CData/*4:0*/ SCHED_EDF = 5U;
    static constexpr CData/*4:0*/ SCHED_LRU = 6U;
    static constexpr CData/*4:0*/ SCHED_SRTF = 7U;
    static constexpr CData/*4:0*/ SCHED_HRRN = 8U;
    static constexpr CData/*4:0*/ SCHED_MLQ = 9U;
    static constexpr CData/*4:0*/ SCHED_MLFQ = 0x0aU;
    static constexpr CData/*4:0*/ SCHED_AIMT = 0x0bU;
    static constexpr CData/*4:0*/ SCHED_BATCHDNN = 0x0cU;
    static constexpr CData/*4:0*/ SCHED_BATCHDNNPP = 0x0dU;

    // CONSTRUCTORS
    Vtop_sim_framework_pkg();
    ~Vtop_sim_framework_pkg();
    void ctor(Vtop__Syms* symsp, const char* namep);
    void dtor();
    VL_UNCOPYABLE(Vtop_sim_framework_pkg);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
