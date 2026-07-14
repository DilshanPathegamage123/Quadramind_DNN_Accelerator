// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"

// Parameter definitions for Vtop_sim_framework_pkg
constexpr CData/*4:0*/ Vtop_sim_framework_pkg::SCHED_FIFO;
constexpr CData/*4:0*/ Vtop_sim_framework_pkg::SCHED_LIFO;
constexpr CData/*4:0*/ Vtop_sim_framework_pkg::SCHED_SJF;
constexpr CData/*4:0*/ Vtop_sim_framework_pkg::SCHED_RR;
constexpr CData/*4:0*/ Vtop_sim_framework_pkg::SCHED_PRI;
constexpr CData/*4:0*/ Vtop_sim_framework_pkg::SCHED_EDF;
constexpr CData/*4:0*/ Vtop_sim_framework_pkg::SCHED_LRU;
constexpr CData/*4:0*/ Vtop_sim_framework_pkg::SCHED_SRTF;
constexpr CData/*4:0*/ Vtop_sim_framework_pkg::SCHED_HRRN;
constexpr CData/*4:0*/ Vtop_sim_framework_pkg::SCHED_MLQ;
constexpr CData/*4:0*/ Vtop_sim_framework_pkg::SCHED_MLFQ;
constexpr CData/*4:0*/ Vtop_sim_framework_pkg::SCHED_AIMT;
constexpr CData/*4:0*/ Vtop_sim_framework_pkg::SCHED_BATCHDNN;
constexpr CData/*4:0*/ Vtop_sim_framework_pkg::SCHED_BATCHDNNPP;



Vtop_sim_framework_pkg::Vtop_sim_framework_pkg() = default;
Vtop_sim_framework_pkg::~Vtop_sim_framework_pkg() = default;

void Vtop_sim_framework_pkg::ctor(Vtop__Syms* symsp, const char* namep) {
    vlSymsp = symsp;
    vlNamep = strdup(Verilated::catName(vlSymsp->name(), namep));
    // Reset structure values
}

void Vtop_sim_framework_pkg::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

void Vtop_sim_framework_pkg::dtor() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
