// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Model implementation (design independent parts)

#include "Vtb_multi_dnn_exec__pch.h"

//============================================================
// Constructors

Vtb_multi_dnn_exec::Vtb_multi_dnn_exec(VerilatedContext* _vcontextp__, const char* _vcname__)
    : VerilatedModel{*_vcontextp__}
    , vlSymsp{new Vtb_multi_dnn_exec__Syms(contextp(), _vcname__, this)}
    , rootp{&(vlSymsp->TOP)}
{
    // Register model with the context
    contextp()->addModel(this);
}

Vtb_multi_dnn_exec::Vtb_multi_dnn_exec(const char* _vcname__)
    : Vtb_multi_dnn_exec(Verilated::threadContextp(), _vcname__)
{
}

//============================================================
// Destructor

Vtb_multi_dnn_exec::~Vtb_multi_dnn_exec() {
    delete vlSymsp;
}

//============================================================
// Evaluation function

#ifdef VL_DEBUG
void Vtb_multi_dnn_exec___024root___eval_debug_assertions(Vtb_multi_dnn_exec___024root* vlSelf);
#endif  // VL_DEBUG
void Vtb_multi_dnn_exec___024root___eval_static(Vtb_multi_dnn_exec___024root* vlSelf);
void Vtb_multi_dnn_exec___024root___eval_initial(Vtb_multi_dnn_exec___024root* vlSelf);
void Vtb_multi_dnn_exec___024root___eval_settle(Vtb_multi_dnn_exec___024root* vlSelf);
void Vtb_multi_dnn_exec___024root___eval(Vtb_multi_dnn_exec___024root* vlSelf);

void Vtb_multi_dnn_exec::eval_step() {
    VL_DEBUG_IF(VL_DBG_MSGF("+++++TOP Evaluate Vtb_multi_dnn_exec::eval_step\n"); );
#ifdef VL_DEBUG
    // Debug assertions
    Vtb_multi_dnn_exec___024root___eval_debug_assertions(&(vlSymsp->TOP));
#endif  // VL_DEBUG
    vlSymsp->__Vm_deleter.deleteAll();
    if (VL_UNLIKELY(!vlSymsp->__Vm_didInit)) {
        VL_DEBUG_IF(VL_DBG_MSGF("+ Initial\n"););
        Vtb_multi_dnn_exec___024root___eval_static(&(vlSymsp->TOP));
        Vtb_multi_dnn_exec___024root___eval_initial(&(vlSymsp->TOP));
        Vtb_multi_dnn_exec___024root___eval_settle(&(vlSymsp->TOP));
        vlSymsp->__Vm_didInit = true;
    }
    VL_DEBUG_IF(VL_DBG_MSGF("+ Eval\n"););
    Vtb_multi_dnn_exec___024root___eval(&(vlSymsp->TOP));
    // Evaluate cleanup
    Verilated::endOfEval(vlSymsp->__Vm_evalMsgQp);
}

//============================================================
// Events and timing
bool Vtb_multi_dnn_exec::eventsPending() { return !vlSymsp->TOP.__VdlySched.empty() && !contextp()->gotFinish(); }

uint64_t Vtb_multi_dnn_exec::nextTimeSlot() { return vlSymsp->TOP.__VdlySched.nextTimeSlot(); }

//============================================================
// Utilities

const char* Vtb_multi_dnn_exec::name() const {
    return vlSymsp->name();
}

//============================================================
// Invoke final blocks

void Vtb_multi_dnn_exec___024root___eval_final(Vtb_multi_dnn_exec___024root* vlSelf);

VL_ATTR_COLD void Vtb_multi_dnn_exec::final() {
    contextp()->executingFinal(true);
    Vtb_multi_dnn_exec___024root___eval_final(&(vlSymsp->TOP));
    contextp()->executingFinal(false);
}

//============================================================
// Implementations of abstract methods from VerilatedModel

const char* Vtb_multi_dnn_exec::hierName() const { return vlSymsp->name(); }
const char* Vtb_multi_dnn_exec::modelName() const { return "Vtb_multi_dnn_exec"; }
unsigned Vtb_multi_dnn_exec::threads() const { return 1; }
void Vtb_multi_dnn_exec::prepareClone() const { contextp()->prepareClone(); }
void Vtb_multi_dnn_exec::atClone() const {
    contextp()->threadPoolpOnClone();
}
