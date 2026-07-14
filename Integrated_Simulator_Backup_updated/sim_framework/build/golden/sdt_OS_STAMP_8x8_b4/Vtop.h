// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Primary model header
//
// This header should be included by all source files instantiating the design.
// The class here is then constructed to instantiate the design.
// See the Verilator manual for examples.

#ifndef VERILATED_VTOP_H_
#define VERILATED_VTOP_H_  // guard

#include "verilated.h"
#include "svdpi.h"

class Vtop__Syms;
class Vtop___024root;
class Vtop_processing_element;
class Vtop_sim_framework_pkg;
class Vtop_stamp_memory_pkg;


// This class is the main interface to the Verilated model
class alignas(VL_CACHE_LINE_BYTES) Vtop VL_NOT_FINAL : public VerilatedModel {
  private:
    // Symbol table holding complete model state (owned by this class)
    Vtop__Syms* const vlSymsp;

  public:

    // CONSTEXPR CAPABILITIES
    // Verilated with --trace?
    static constexpr bool traceCapable = false;

    // PORTS
    // The application code writes and reads these signals to
    // propagate new values into/out from the Verilated model.
    VL_IN8(&clk,0,0);
    VL_IN8(&rst_n,0,0);
    VL_IN8(&mem_layout,1,0);
    VL_IN8(&start,0,0);
    VL_OUT8(&done,0,0);
    VL_OUT8(&busy,0,0);
    VL_OUT8(&phase_mem_done,0,0);
    VL_OUT8(&phase_compute_done,0,0);
    VL_IN8(&metadata_wr_en,0,0);
    VL_IN8(&metadata_wr_addr,7,0);
    VL_IN8(&phase_start_in,0,0);
    VL_IN8(&pt_write_en,0,0);
    VL_IN8(&pt_write_vpn,7,0);
    VL_IN8(&pt_write_valid,0,0);
    VL_OUT8(&axi_arlen,7,0);
    VL_OUT8(&axi_arvalid,0,0);
    VL_IN8(&axi_arready,0,0);
    VL_IN8(&axi_rvalid,0,0);
    VL_OUT8(&axi_rready,0,0);
    VL_IN8(&axi_rlast,0,0);
    VL_OUT8(&ext_input_addr_valid_w,7,0);
    VL_IN8(&ext_input_data_valid_w,7,0);
    VL_OUT8(&ext_input_addr_valid_h,7,0);
    VL_IN8(&ext_input_data_valid_h,7,0);
    VL_OUT8(&ext_weight_addr_valid_1d,7,0);
    VL_IN8(&ext_weight_data_valid_1d,7,0);
    VL_OUT64(&ext_weight_addr_valid_2d,63,0);
    VL_IN64(&ext_weight_data_valid_2d,63,0);
    VL_OUT64(&ext_output_addr_valid_2d,63,0);
    VL_OUT64(&ext_output_data_valid_2d,63,0);
    VL_OUT8(&ext_output_addr_valid_1d,7,0);
    VL_OUT8(&ext_output_data_valid_1d,7,0);
    VL_IN16(&input_channels,15,0);
    VL_IN16(&input_height,15,0);
    VL_IN16(&input_width,15,0);
    VL_IN16(&weight_k,15,0);
    VL_IN16(&weight_c,15,0);
    VL_IN16(&weight_kh,15,0);
    VL_IN16(&weight_kw,15,0);
    VL_IN16(&output_channels,15,0);
    VL_IN16(&output_height,15,0);
    VL_IN16(&output_width,15,0);
    VL_IN16(&tile_row,15,0);
    VL_IN16(&tile_col_start,15,0);
    VL_IN16(&tile_ch_start,15,0);
    VL_IN16(&ws_input_ch,15,0);
    VL_IN16(&ws_kernel_row,15,0);
    VL_IN16(&ws_kernel_col_start,15,0);
    VL_IN16(&phase_id_in,15,0);
    VL_IN16(&num_delta_ops_in,15,0);
    VL_IN16(&phase_base_addr_in,15,0);
    VL_IN(&input_base_addr,31,0);
    VL_IN(&weight_base_addr,31,0);
    VL_IN(&output_base_addr,31,0);
    VL_INW(&metadata_wr_data,127,0,4);
    VL_IN(&pt_write_ppn,19,0);
    VL_OUT(&axi_arvalid_addr,31,0);
    VL_IN(&axi_rdata,31,0);
    VL_OUT(&stats_loads_or_hits,31,0);
    VL_OUT(&stats_moves_or_misses,31,0);
    VL_OUT(&stats_keeps,31,0);
    VL_OUT(&stats_bytes_loaded,31,0);
    VL_OUT(&stats_bytes_moved,31,0);
    VL_OUT(&stats_compute_cycles,31,0);
    VlUnpacked<IData/*31:0*/, 8> &ext_input_addr_w;
    VlUnpacked<IData/*31:0*/, 8> &ext_input_data_w;
    VlUnpacked<IData/*31:0*/, 8> &ext_input_addr_h;
    VlUnpacked<IData/*31:0*/, 8> &ext_input_data_h;
    VlUnpacked<IData/*31:0*/, 8> &ext_weight_addr_1d;
    VlUnpacked<IData/*31:0*/, 8> &ext_weight_data_1d;
    VlUnpacked<VlUnpacked<IData/*31:0*/, 8>, 8> &ext_weight_addr_2d;
    VlUnpacked<VlUnpacked<IData/*31:0*/, 8>, 8> &ext_weight_data_2d;
    VlUnpacked<VlUnpacked<IData/*31:0*/, 8>, 8> &ext_output_addr_2d;
    VlUnpacked<VlUnpacked<IData/*31:0*/, 8>, 8> &ext_output_data_2d;
    VlUnpacked<IData/*31:0*/, 8> &ext_output_addr_1d;
    VlUnpacked<IData/*31:0*/, 8> &ext_output_data_1d;

    // CELLS
    // Public to allow access to /* verilator public */ items.
    // Otherwise the application code can consider these internals.
    Vtop_stamp_memory_pkg* const __PVT__stamp_memory_pkg;
    Vtop_sim_framework_pkg* const __PVT__sim_framework_pkg;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__0__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__1__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__2__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__3__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__4__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__5__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__6__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__0__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__1__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__2__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__3__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__4__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__5__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__6__KET____DOT__pe_inst;
    Vtop_processing_element* const __PVT__single_dnn_top__DOT__u_array__DOT__g_os__DOT__u_os__DOT__gen_pe_rows__BRA__7__KET____DOT__gen_pe_cols__BRA__7__KET____DOT__pe_inst;

    // Root instance pointer to allow access to model internals,
    // including inlined /* verilator public_flat_* */ items.
    Vtop___024root* const rootp;

    // CONSTRUCTORS
    /// Construct the model; called by application code
    /// If contextp is null, then the model will use the default global context
    /// If name is "", then makes a wrapper with a
    /// single model invisible with respect to DPI scope names.
    explicit Vtop(VerilatedContext* contextp, const char* name = "TOP");
    explicit Vtop(const char* name = "TOP");
    /// Destroy the model; called (often implicitly) by application code
    virtual ~Vtop();
  private:
    VL_UNCOPYABLE(Vtop);  ///< Copying not allowed

  public:
    // API METHODS
    /// Evaluate the model.  Application must call when inputs change.
    void eval() { eval_step(); }
    /// Evaluate when calling multiple units/models per time step.
    void eval_step();
    /// Evaluate at end of a timestep for tracing, when using eval_step().
    /// Application must call after all eval() and before time changes.
    void eval_end_step() {}
    /// Simulation complete, run final blocks.  Application must call on completion.
    void final();
    /// Are there scheduled events to handle?
    bool eventsPending();
    /// Returns time at next time slot. Aborts if !eventsPending()
    uint64_t nextTimeSlot();
    /// Trace signals in the model; called by application code
    void trace(VerilatedTraceBaseC* tfp, int levels, int options = 0) { contextp()->trace(tfp, levels, options); }
    /// Retrieve name of this model instance (as passed to constructor).
    const char* name() const;

    // Abstract methods from VerilatedModel
    const char* hierName() const override final;
    const char* modelName() const override final;
    unsigned threads() const override final;
    /// Prepare for cloning the model at the process level (e.g. fork in Linux)
    /// Release necessary resources. Called before cloning.
    void prepareClone() const;
    /// Re-init after cloning the model at the process level (e.g. fork in Linux)
    /// Re-allocate necessary resources. Called after cloning.
    void atClone() const;
  private:
    // Internal functions - trace registration
    void traceBaseModel(VerilatedTraceBaseC* tfp, int levels, int options);
};

#endif  // guard
