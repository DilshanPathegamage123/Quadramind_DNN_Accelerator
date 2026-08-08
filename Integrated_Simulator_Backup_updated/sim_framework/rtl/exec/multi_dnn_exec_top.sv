//=============================================================================
// Module: multi_dnn_exec_top
// Description: Dual-issue multi-DNN execution top.  This is the machine that
//              lets AI-MT / BATCH-DNN / BATCH-DNN++ actually deliver what they
//              were designed to deliver.
//
// WHY THIS MODULE EXISTS
// ----------------------
// The three DNN-aware schedulers were already implemented correctly: each one
// drives an INDEPENDENT mt_valid and ct_valid, exactly as the papers require.
// Three things downstream destroyed that parallelism before it could pay:
//
//   1. unified_scheduler_wrapper collapsed the concurrent {mt_valid, ct_valid}
//      pair into a single tagged union that gives the CT priority -- so only
//      one of the two could be seen per cycle.  (Fixed by the *_o passthroughs
//      that this top consumes.)
//   2. multi_dnn_top's dispatch FSM was single-issue run-to-completion
//      (D_IDLE -> D_RUN -> D_WAIT_DONE), holding one task until it retired.
//   3. single_dnn_top's FSM ran S_MEM -> S_COMPUTE strictly in sequence, so
//      even within one layer the array idled through the whole memory phase.
//
// Net effect: memory and compute could never be in flight at the same time,
// which is the one thing AI-MT is for.  The measured consequence was all five
// schedulers landing within a single cycle of each other (13,412 vs 13,413).
//
// WHAT THIS TOP DOES DIFFERENTLY
// ------------------------------
// Two genuinely independent execution resources --
//     mt_engine : owns the off-chip port  (bandwidth+latency limited DRAM)
//     ct_engine : owns the systolic array
// -- driven by two independent dispatch channels that can both launch in the
// same cycle.  A memory task for layer B therefore overlaps a compute task for
// layer A, and the array stops idling through prefetch.
//
// FAIR BASELINE
// -------------
// The basic (non-DNN-aware) schedulers, select 0..10, run on the SAME machine
// through a serial MT->CT channel.  That is not a handicap invented to flatter
// the DNN-aware family: a FIFO/SJF/RR scheduler emits one undifferentiated
// task stream and has no notion of a memory task to overlap, so it physically
// cannot fill the DMA/array bubble.  Same workload, same engines, same DRAM --
// the only difference is whether the policy can express MT/CT concurrency.
//
// TERMINATION
// -----------
// Quiescence, not a task count: done when both engines are idle and the
// scheduler is asserting neither valid for SETTLE_CYCLES consecutive cycles.
// A count would be wrong for BATCH-DNN, whose sub-batch splitting legitimately
// dispatches one layer as several CTs.
//=============================================================================

`timescale 1ns/1ps

module multi_dnn_exec_top
    import sim_framework_pkg::*;
#(
    parameter int MAX_TASKS          = 16,
    parameter int TASK_ID_WIDTH      = 8,
    parameter int MAX_LAYERS         = 32,
    parameter int MAX_DNNS           = 4,
    parameter int LAYER_ID_WIDTH     = 8,
    parameter int DNN_ID_WIDTH       = 4,
    parameter int BATCH_WIDTH        = 8,
    parameter int CYCLE_WIDTH        = 32,
    parameter int MEM_WIDTH          = 32,
    parameter     ONCHIP_MEM_SIZE    = 44*1024*1024,
    parameter     WORD_BITS          = 16,
    parameter     COMPUTE_BAL_THRESH = 1000,
    parameter     MAX_LAYER_DISTANCE = 5,
    parameter     STACK_DEPTH        = 16,
    parameter int SETTLE_CYCLES      = 64
) (
    input  logic clk,
    input  logic rst_n,

    //--- Run control
    input  logic        run_enable,
    output logic        run_done,

    //--- Scheduler selection
    input  logic [4:0]  scheduler_select,

    //--- Runtime machine configuration
    input  logic [15:0] cfg_dram_latency,
    input  logic [15:0] cfg_dram_bytes_per_cycle,
    input  logic [15:0] cfg_array_fill_drain,

    //--- Basic-task interface (schedulers 0..10)
    input  logic                      task_valid,
    input  logic [TASK_ID_WIDTH-1:0]  task_id,
    input  logic [15:0]               burst_time,
    input  logic [3:0]                task_priority,
    input  logic [31:0]               deadline,
    input  logic                      task_tick,
    output logic                      task_ready,

    //--- Scheduling-table load (shared by the scheduler and the exec table)
    input  logic                       st_write_en,
    input  logic [LAYER_ID_WIDTH-1:0]  st_layer_idx,
    input  logic [DNN_ID_WIDTH-1:0]    st_dnn_id,
    input  logic [LAYER_ID_WIDTH-1:0]  st_prev_layer,
    input  logic [CYCLE_WIDTH-1:0]     st_mem_cycles,
    input  logic [CYCLE_WIDTH-1:0]     st_compute_cycles,
    input  logic [MEM_WIDTH-1:0]       st_weight_fp,
    input  logic [MEM_WIDTH-1:0]       st_ifmap_fp,
    input  logic [MEM_WIDTH-1:0]       st_ofmap_fp,
    input  logic [BATCH_WIDTH-1:0]     st_batch,
    input  logic [LAYER_ID_WIDTH-1:0]  st_total_layers,

    //--- Cycle-level observability (the testbench builds its Gantt from these)
    output logic                       mt_busy,
    output logic                       ct_busy,
    output logic                       mt_start_pulse,
    output logic                       ct_start_pulse,
    output logic                       mt_done_pulse,
    output logic                       ct_done_pulse,
    output logic [LAYER_ID_WIDTH-1:0]  mt_active_layer,
    output logic [LAYER_ID_WIDTH-1:0]  ct_active_layer,
    output logic [BATCH_WIDTH-1:0]     ct_active_batch,

    //--- Aggregate statistics
    output logic [31:0]                stat_total_cycles,
    output logic [31:0]                stat_mt_busy_cycles,
    output logic [31:0]                stat_ct_busy_cycles,
    output logic [31:0]                stat_overlap_cycles,
    output logic [31:0]                stat_both_idle_cycles,
    output logic [31:0]                stat_mt_tasks,
    output logic [31:0]                stat_ct_tasks,
    output logic [63:0]                stat_inferences,
    output logic [63:0]                stat_bytes_moved,
    output logic [31:0]                stat_dram_requests,
    output logic [31:0]                stat_sched_stall_cycles,
    output logic [CYCLE_WIDTH-1:0]     stat_available_memory,

    //--- Completion accounting.  A run is only comparable if it actually
    //    finished the workload; a scheduler that wedges with layers still
    //    outstanding must be REJECTED, not credited with a fast time.
    output logic [31:0]                stat_layers_completed,
    output logic [31:0]                stat_layers_expected,
    output logic                       stat_incomplete
);

    // ---------------------------------------------------------------------
    // Local execution descriptor table.
    // The execution units need the same per-layer metadata the scheduler
    // reasons over (footprints, cycle counts, batch).  Mirrored here from the
    // same st_* write stream so there is exactly one source of truth.
    // ---------------------------------------------------------------------
    typedef struct packed {
        logic                    valid;
        logic [DNN_ID_WIDTH-1:0] dnn_id;
        logic [CYCLE_WIDTH-1:0]  compute_cycles;
        logic [MEM_WIDTH-1:0]    weight_fp;
        logic [MEM_WIDTH-1:0]    ifmap_fp;
        logic [BATCH_WIDTH-1:0]  batch;
    } exec_entry_t;

    exec_entry_t exec_table [MAX_LAYERS];
    logic [LAYER_ID_WIDTH-1:0] total_layers_q;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 0; i < MAX_LAYERS; i++) exec_table[i] <= '0;
            total_layers_q <= '0;
        end else if (st_write_en) begin
            exec_table[st_layer_idx].valid          <= 1'b1;
            exec_table[st_layer_idx].dnn_id         <= st_dnn_id;
            exec_table[st_layer_idx].compute_cycles <= st_compute_cycles;
            exec_table[st_layer_idx].weight_fp      <= st_weight_fp;
            exec_table[st_layer_idx].ifmap_fp       <= st_ifmap_fp;
            exec_table[st_layer_idx].batch          <= (st_batch == '0)
                                                       ? BATCH_WIDTH'(1) : st_batch;
            total_layers_q <= st_total_layers;
        end
    end

    // ---------------------------------------------------------------------
    // Scheduler
    // ---------------------------------------------------------------------
    sched_output_t              sched_out;
    logic [BATCH_WIDTH-1:0]     sched_ct_batch;
    logic                       s_mt_valid, s_ct_valid;
    logic [LAYER_ID_WIDTH-1:0]  s_mt_layer, s_ct_layer;
    logic [DNN_ID_WIDTH-1:0]    s_mt_dnn,   s_ct_dnn;
    logic [BATCH_WIDTH-1:0]     s_ct_batch;
    logic [CYCLE_WIDTH-1:0]     s_avail_mem, s_stall_cycles;
    logic                       s_dnn_stall;

    logic mem_access_done_to_sched, compute_done_to_sched, task_complete_to_sched;

    logic is_dnn_aware;
    assign is_dnn_aware = (scheduler_select >= 5'd11);

    unified_scheduler_wrapper #(
        .MAX_TASKS       (MAX_TASKS),
        .TASK_ID_WIDTH   (TASK_ID_WIDTH),
        .MAX_LAYERS      (MAX_LAYERS),
        .MAX_DNNS        (MAX_DNNS),
        .LAYER_ID_WIDTH  (LAYER_ID_WIDTH),
        .DNN_ID_WIDTH    (DNN_ID_WIDTH),
        .BATCH_WIDTH     (BATCH_WIDTH),
        .CYCLE_WIDTH     (CYCLE_WIDTH),
        .MEM_WIDTH       (MEM_WIDTH),
        .ONCHIP_MEM_SIZE (ONCHIP_MEM_SIZE),
        .WORD_BITS       (WORD_BITS),
        .COMPUTE_BAL_THRESH (COMPUTE_BAL_THRESH),
        .MAX_LAYER_DISTANCE (MAX_LAYER_DISTANCE),
        .STACK_DEPTH     (STACK_DEPTH)
    ) u_sched (
        .clk             (clk),
        .rst_n           (rst_n),
        .scheduler_select(scheduler_select),
        .task_valid      (task_valid),
        .task_id         (task_id),
        .burst_time      (burst_time),
        .task_priority   (task_priority),
        .deadline        (deadline),
        .task_tick       (task_tick),
        .task_complete   (task_complete_to_sched),
        .task_ready      (task_ready),
        .st_write_en     (st_write_en),
        .st_layer_idx    (st_layer_idx),
        .st_dnn_id       (st_dnn_id),
        .st_prev_layer   (st_prev_layer),
        .st_mem_cycles   (st_mem_cycles),
        .st_compute_cycles(st_compute_cycles),
        .st_weight_fp    (st_weight_fp),
        .st_ifmap_fp     (st_ifmap_fp),
        .st_ofmap_fp     (st_ofmap_fp),
        .st_batch        (st_batch),
        .st_total_layers (st_total_layers),
        .mem_access_done (mem_access_done_to_sched),
        .compute_done    (compute_done_to_sched),
        .sched_out       (sched_out),
        .ct_batch_size   (sched_ct_batch),
        .mt_valid_o      (s_mt_valid),
        .mt_layer_id_o   (s_mt_layer),
        .mt_dnn_id_o     (s_mt_dnn),
        .ct_valid_o      (s_ct_valid),
        .ct_layer_id_o   (s_ct_layer),
        .ct_dnn_id_o     (s_ct_dnn),
        .ct_batch_size_o (s_ct_batch),
        .dnn_available_memory  (s_avail_mem),
        .dnn_total_stall_cycles(s_stall_cycles),
        .basic_total_tasks_processed(),
        .basic_total_wait_time(),
        .basic_total_turnaround_time(),
        .dnn_stall_detected(s_dnn_stall)
    );

    // ---------------------------------------------------------------------
    // Execution engines
    // ---------------------------------------------------------------------
    logic                    mt_start, mt_done_i, mt_busy_i;
    logic [MEM_WIDTH-1:0]    mt_weight_bytes, mt_ifmap_bytes;
    logic [BATCH_WIDTH-1:0]  mt_batch;
    logic [31:0]             mt_stat_tasks, mt_stat_busy, mt_dram_reqs;
    logic [63:0]             mt_stat_bytes;

    mt_engine #(
        .MEM_WIDTH   (MEM_WIDTH),
        .BATCH_WIDTH (BATCH_WIDTH)
    ) u_mt (
        .clk                 (clk),
        .rst_n               (rst_n),
        .cfg_latency         (cfg_dram_latency),
        .cfg_bytes_per_cycle (cfg_dram_bytes_per_cycle),
        .start               (mt_start),
        .weight_bytes        (mt_weight_bytes),
        .ifmap_bytes         (mt_ifmap_bytes),
        .batch               (mt_batch),
        .done                (mt_done_i),
        .busy                (mt_busy_i),
        .stats_tasks         (mt_stat_tasks),
        .stats_bytes         (mt_stat_bytes),
        .stats_busy_cycles   (mt_stat_busy),
        .dram_requests       (mt_dram_reqs)
    );

    logic                    ct_start, ct_done_i, ct_busy_i;
    logic [CYCLE_WIDTH-1:0]  ct_cycles_per_batch;
    logic [BATCH_WIDTH-1:0]  ct_batch;
    logic [31:0]             ct_stat_tasks, ct_stat_busy;
    logic [63:0]             ct_stat_infer;

    ct_engine #(
        .CYCLE_WIDTH (CYCLE_WIDTH),
        .BATCH_WIDTH (BATCH_WIDTH)
    ) u_ct (
        .clk               (clk),
        .rst_n             (rst_n),
        .cfg_fill_drain    (cfg_array_fill_drain),
        .start             (ct_start),
        .cycles_per_batch  (ct_cycles_per_batch),
        .batch             (ct_batch),
        .done              (ct_done_i),
        .busy              (ct_busy_i),
        .stats_tasks       (ct_stat_tasks),
        .stats_inferences  (ct_stat_infer),
        .stats_busy_cycles (ct_stat_busy)
    );

    assign mt_busy = mt_busy_i;
    assign ct_busy = ct_busy_i;

    // ---------------------------------------------------------------------
    // DUAL-ISSUE DISPATCH (DNN-aware schedulers)
    //
    // Two channels, no shared state, both able to launch in the same cycle.
    // mt_valid / ct_valid are LEVELS held by the scheduler until their
    // completion pulse is acknowledged, so each channel latches an in-flight
    // flag and then waits for the valid to drop before it may re-arm.  Without
    // that ack handshake a single task would be launched repeatedly in the
    // window between `done` and the scheduler deasserting its valid.
    // ---------------------------------------------------------------------
    logic mt_inflight, mt_wait_ack;
    logic ct_inflight, ct_wait_ack;

    // ---------------------------------------------------------------------
    // SERIAL DISPATCH (basic schedulers) -- MT then CT, one task at a time.
    // ---------------------------------------------------------------------
    typedef enum logic [2:0] {
        B_IDLE, B_MEM, B_COMPUTE, B_RETIRE, B_ACK
    } bstate_t;
    bstate_t bstate;
    logic [LAYER_ID_WIDTH-1:0] b_layer;

    logic run_active;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            mt_start        <= 1'b0;
            ct_start        <= 1'b0;
            mt_inflight     <= 1'b0;
            mt_wait_ack     <= 1'b0;
            ct_inflight     <= 1'b0;
            ct_wait_ack     <= 1'b0;
            mt_active_layer <= '0;
            ct_active_layer <= '0;
            ct_active_batch <= BATCH_WIDTH'(1);
            mt_weight_bytes <= '0;
            mt_ifmap_bytes  <= '0;
            mt_batch        <= BATCH_WIDTH'(1);
            ct_cycles_per_batch <= '0;
            ct_batch        <= BATCH_WIDTH'(1);
            mem_access_done_to_sched <= 1'b0;
            compute_done_to_sched    <= 1'b0;
            task_complete_to_sched   <= 1'b0;
            bstate          <= B_IDLE;
            b_layer         <= '0;
        end else begin
            mt_start                 <= 1'b0;
            ct_start                 <= 1'b0;
            mem_access_done_to_sched <= 1'b0;
            compute_done_to_sched    <= 1'b0;
            task_complete_to_sched   <= 1'b0;

            if (is_dnn_aware) begin
                //------------------------------------------------------------
                // MT channel -- independent of the CT channel
                //------------------------------------------------------------
                if (s_mt_valid && !mt_busy_i && !mt_inflight && !mt_wait_ack
                    && run_active) begin
                    mt_start        <= 1'b1;
                    mt_inflight     <= 1'b1;
                    mt_active_layer <= s_mt_layer;
                    mt_weight_bytes <= exec_table[s_mt_layer].weight_fp;
                    mt_ifmap_bytes  <= exec_table[s_mt_layer].ifmap_fp;
                    mt_batch        <= exec_table[s_mt_layer].batch;
                end
                if (mt_done_i) begin
                    mem_access_done_to_sched <= 1'b1;
                    mt_inflight              <= 1'b0;
                    mt_wait_ack              <= 1'b1;
                end
                if (mt_wait_ack && !s_mt_valid) mt_wait_ack <= 1'b0;

                //------------------------------------------------------------
                // CT channel -- independent of the MT channel
                //------------------------------------------------------------
                if (s_ct_valid && !ct_busy_i && !ct_inflight && !ct_wait_ack
                    && run_active) begin
                    ct_start            <= 1'b1;
                    ct_inflight         <= 1'b1;
                    ct_active_layer     <= s_ct_layer;
                    ct_active_batch     <= s_ct_batch;
                    ct_cycles_per_batch <= exec_table[s_ct_layer].compute_cycles;
                    ct_batch            <= s_ct_batch;
                end
                if (ct_done_i) begin
                    compute_done_to_sched <= 1'b1;
                    ct_inflight           <= 1'b0;
                    ct_wait_ack           <= 1'b1;
                end
                if (ct_wait_ack && !s_ct_valid) ct_wait_ack <= 1'b0;

            end else begin
                //------------------------------------------------------------
                // Basic schedulers: strictly serial MT -> CT.
                //------------------------------------------------------------
                case (bstate)
                    B_IDLE: begin
                        if (sched_out.valid && run_active) begin
                            b_layer         <= sched_out.task_or_layer_id;
                            mt_active_layer <= sched_out.task_or_layer_id;
                            mt_weight_bytes <= exec_table[sched_out.task_or_layer_id].weight_fp;
                            mt_ifmap_bytes  <= exec_table[sched_out.task_or_layer_id].ifmap_fp;
                            mt_batch        <= exec_table[sched_out.task_or_layer_id].batch;
                            mt_start        <= 1'b1;
                            bstate          <= B_MEM;
                        end
                    end
                    B_MEM: begin
                        if (mt_done_i) begin
                            ct_active_layer     <= b_layer;
                            ct_active_batch     <= exec_table[b_layer].batch;
                            ct_cycles_per_batch <= exec_table[b_layer].compute_cycles;
                            ct_batch            <= exec_table[b_layer].batch;
                            ct_start            <= 1'b1;
                            bstate              <= B_COMPUTE;
                        end
                    end
                    B_COMPUTE: begin
                        if (ct_done_i) bstate <= B_RETIRE;
                    end
                    B_RETIRE: begin
                        task_complete_to_sched <= 1'b1;
                        bstate                 <= B_ACK;
                    end
                    // Wait for the scheduler to observe task_complete and
                    // withdraw its offer before looking again.  Returning
                    // straight to B_IDLE re-latched the SAME selection: the
                    // completion pulse is only presented to the scheduler on
                    // the following edge, so for one cycle sched_out still
                    // advertised the task that had just retired, and the FSM
                    // dispatched it a second time.  Every basic scheduler
                    // clears its valid on task_complete, so this cannot hang;
                    // if the queue is now empty the valid simply stays low and
                    // the run quiesces.
                    //
                    // Measured effect: FIFO ran 13 tasks for a 12-layer mix
                    // (one redundant re-run), and HRRN additionally starved a
                    // layer, retiring 11 of 12.
                    B_ACK: begin
                        if (!sched_out.valid) bstate <= B_IDLE;
                    end
                    default: bstate <= B_IDLE;
                endcase
            end
        end
    end

    assign mt_start_pulse = mt_start;
    assign ct_start_pulse = ct_start;
    assign mt_done_pulse  = mt_done_i;
    assign ct_done_pulse  = ct_done_i;

    // ---------------------------------------------------------------------
    // Statistics + quiescence-based termination
    // ---------------------------------------------------------------------
    logic [31:0] cycle_ctr;
    logic [31:0] idle_streak;
    logic        any_pending;

    // ---------------------------------------------------------------------
    // Per-layer completion. Counting ct_done pulses is NOT equivalent:
    // BATCH-DNN legitimately dispatches one layer as several sub-batch CTs,
    // and a basic scheduler can re-dispatch a task, so both over-count.
    // Distinct layers retired is the honest measure of "did the run finish".
    // ---------------------------------------------------------------------
    logic [MAX_LAYERS-1:0] layer_done;
    logic                  all_layers_done;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            layer_done            <= '0;
            stat_layers_completed <= '0;
        end else if (ct_done_i && !layer_done[ct_active_layer[$clog2(MAX_LAYERS)-1:0]]) begin
            layer_done[ct_active_layer[$clog2(MAX_LAYERS)-1:0]] <= 1'b1;
            stat_layers_completed <= stat_layers_completed + 32'd1;
        end
    end

    assign stat_layers_expected = 32'(total_layers_q);
    assign all_layers_done      = (total_layers_q != '0) &&
                                  (stat_layers_completed >= 32'(total_layers_q));

    // "Nothing left to do": both engines idle, scheduler asserting no work,
    // and (for the basic path) the serial FSM back at rest.
    always_comb begin
        any_pending = mt_busy_i || ct_busy_i;
        if (is_dnn_aware) any_pending = any_pending || s_mt_valid || s_ct_valid;
        else              any_pending = any_pending || sched_out.valid ||
                                        (bstate != B_IDLE);
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            run_active            <= 1'b0;
            run_done              <= 1'b0;
            stat_incomplete       <= 1'b0;
            cycle_ctr             <= '0;
            idle_streak           <= '0;
            stat_total_cycles     <= '0;
            stat_mt_busy_cycles   <= '0;
            stat_ct_busy_cycles   <= '0;
            stat_overlap_cycles   <= '0;
            stat_both_idle_cycles <= '0;
        end else begin
            if (run_enable && !run_done) run_active <= 1'b1;

            if (run_active && !run_done) begin
                cycle_ctr <= cycle_ctr + 32'd1;

                if (mt_busy_i)               stat_mt_busy_cycles <= stat_mt_busy_cycles + 32'd1;
                if (ct_busy_i)               stat_ct_busy_cycles <= stat_ct_busy_cycles + 32'd1;
                if (mt_busy_i && ct_busy_i)  stat_overlap_cycles <= stat_overlap_cycles + 32'd1;
                if (!mt_busy_i && !ct_busy_i)stat_both_idle_cycles <= stat_both_idle_cycles + 32'd1;

                if (all_layers_done) begin
                    // Normal termination: every layer retired.
                    run_done          <= 1'b1;
                    stat_incomplete   <= 1'b0;
                    stat_total_cycles <= cycle_ctr;
                end else if (any_pending) begin
                    idle_streak <= '0;
                end else begin
                    // Nothing in flight and nothing offered, yet layers are
                    // still outstanding -- the scheduler has wedged. Stop and
                    // mark the run incomplete so it can be rejected upstream.
                    idle_streak <= idle_streak + 32'd1;
                    if (idle_streak >= 32'(SETTLE_CYCLES)) begin
                        run_done          <= 1'b1;
                        stat_incomplete   <= 1'b1;
                        stat_total_cycles <= cycle_ctr - 32'(SETTLE_CYCLES);
                    end
                end
            end
        end
    end

    assign stat_mt_tasks           = mt_stat_tasks;
    assign stat_ct_tasks           = ct_stat_tasks;
    assign stat_inferences         = ct_stat_infer;
    assign stat_bytes_moved        = mt_stat_bytes;
    assign stat_dram_requests      = mt_dram_reqs;
    assign stat_sched_stall_cycles = s_stall_cycles;
    assign stat_available_memory   = s_avail_mem;

endmodule : multi_dnn_exec_top
