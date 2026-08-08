//=============================================================================
// Testbench: tb_multi_dnn_exec
//
// Drives multi_dnn_exec_top under Verilator (--binary --timing) and emits a
// JSON record of the run: aggregate statistics plus a full MT/CT event
// timeline, which is what the Gantt / utilisation figures are built from.
//
// Everything that varies across the sweep is a runtime plusarg, so one
// compiled binary covers the scheduler, workload, batch and DRAM dimensions.
// Only the on-chip capacity sweep needs re-elaboration (it is a parameter
// inside the schedulers).
//
//   +sched=<0..13>         scheduler_select
//   +workload=<path>       scheduling-table file (see format below)
//   +json=<path>           output file
//   +dram_lat=<n>          DRAM first-beat latency, cycles
//   +dram_bw=<n>           DRAM sustained bandwidth, bytes/cycle
//   +fill_drain=<n>        systolic pipeline fill+drain, cycles
//   +timeout=<n>           hard cycle cap
//
// Workload file format (whitespace separated, '#' comment lines ignored):
//   line 1 : <n_layers>
//   then n : <idx> <dnn_id> <prev> <mem_cyc> <cmp_cyc> <wfp> <ifp> <ofp> <batch>
//=============================================================================

`timescale 1ns/1ps

module tb_multi_dnn_exec;

    localparam int MAX_LAYERS     = 32;
    localparam int LAYER_ID_WIDTH = 8;
    localparam int DNN_ID_WIDTH   = 4;
    localparam int BATCH_WIDTH    = 8;
    localparam int CYCLE_WIDTH    = 32;
    localparam int MEM_WIDTH      = 32;
    localparam int MAX_EVENTS     = 40000;

    logic clk = 1'b0;
    logic rst_n = 1'b0;
    always #5 clk = ~clk;

    //--- Runtime configuration
    int unsigned sched_sel   = 11;
    int unsigned dram_lat    = 20;
    int unsigned dram_bw     = 16;
    int unsigned fill_drain  = 16;
    int unsigned timeout_cyc = 20_000_000;
    string       wl_path     = "workload.txt";
    string       json_path   = "run.json";

    //--- Workload storage
    int unsigned n_layers;
    int unsigned wl_dnn   [MAX_LAYERS];
    int unsigned wl_prev  [MAX_LAYERS];
    int unsigned wl_memc  [MAX_LAYERS];
    int unsigned wl_cmpc  [MAX_LAYERS];
    int unsigned wl_wfp   [MAX_LAYERS];
    int unsigned wl_ifp   [MAX_LAYERS];
    int unsigned wl_ofp   [MAX_LAYERS];
    int unsigned wl_batch [MAX_LAYERS];

    //--- DUT signals
    logic        run_enable = 1'b0;
    logic        run_done;
    logic [4:0]  scheduler_select;
    logic [15:0] cfg_dram_latency, cfg_dram_bytes_per_cycle, cfg_array_fill_drain;

    logic                      task_valid = 1'b0;
    logic [7:0]                task_id    = '0;
    logic [15:0]               burst_time = '0;
    logic [3:0]                task_priority = '0;
    logic [31:0]               deadline   = '0;
    logic                      task_tick  = 1'b0;
    logic                      task_ready;

    logic                      st_write_en = 1'b0;
    logic [LAYER_ID_WIDTH-1:0] st_layer_idx = '0;
    logic [DNN_ID_WIDTH-1:0]   st_dnn_id = '0;
    logic [LAYER_ID_WIDTH-1:0] st_prev_layer = '0;
    logic [CYCLE_WIDTH-1:0]    st_mem_cycles = '0;
    logic [CYCLE_WIDTH-1:0]    st_compute_cycles = '0;
    logic [MEM_WIDTH-1:0]      st_weight_fp = '0;
    logic [MEM_WIDTH-1:0]      st_ifmap_fp = '0;
    logic [MEM_WIDTH-1:0]      st_ofmap_fp = '0;
    logic [BATCH_WIDTH-1:0]    st_batch = '0;
    logic [LAYER_ID_WIDTH-1:0] st_total_layers = '0;

    logic                      mt_busy, ct_busy;
    logic                      mt_start_pulse, ct_start_pulse;
    logic                      mt_done_pulse, ct_done_pulse;
    logic [LAYER_ID_WIDTH-1:0] mt_active_layer, ct_active_layer;
    logic [BATCH_WIDTH-1:0]    ct_active_batch;

    logic [31:0] stat_total_cycles, stat_mt_busy_cycles, stat_ct_busy_cycles;
    logic [31:0] stat_overlap_cycles, stat_both_idle_cycles;
    logic [31:0] stat_mt_tasks, stat_ct_tasks;
    logic [63:0] stat_inferences, stat_bytes_moved;
    logic [31:0] stat_dram_requests, stat_sched_stall_cycles;
    logic [CYCLE_WIDTH-1:0] stat_available_memory;
    logic [31:0] stat_layers_completed, stat_layers_expected;
    logic        stat_incomplete;

    assign scheduler_select         = 5'(sched_sel);
    assign cfg_dram_latency         = 16'(dram_lat);
    assign cfg_dram_bytes_per_cycle = 16'(dram_bw);
    assign cfg_array_fill_drain     = 16'(fill_drain);

    // MAX_DNNS = 8, not the default 4.  BATCH-DNN / BATCH-DNN++ index
    // per-DNN state (current_batch, prev_batch, sub-batch stacks) by dnn_id,
    // and Workload mix 6 co-schedules SIX networks.  At MAX_DNNS = 4 those
    // arrays are [3:0] while dnn_id reaches 5, so the two highest-numbered
    // DNNs read out-of-range state and their layers were never retired
    // (16 of 24 completed).  Sizing the parameter to the workload fixes it;
    // DNN_ID_WIDTH = 4 already allows up to 16.
    multi_dnn_exec_top #(
        .MAX_TASKS      (MAX_LAYERS),
        .MAX_LAYERS     (MAX_LAYERS),
        .MAX_DNNS       (8),
        .ONCHIP_MEM_SIZE(`ONCHIP_MEM_BYTES),
        .COMPUTE_BAL_THRESH(`COMPUTE_BAL_THRESH)
    ) dut (
        .clk (clk), .rst_n (rst_n),
        .run_enable (run_enable), .run_done (run_done),
        .scheduler_select (scheduler_select),
        .cfg_dram_latency (cfg_dram_latency),
        .cfg_dram_bytes_per_cycle (cfg_dram_bytes_per_cycle),
        .cfg_array_fill_drain (cfg_array_fill_drain),
        .task_valid (task_valid), .task_id (task_id),
        .burst_time (burst_time), .task_priority (task_priority),
        .deadline (deadline), .task_tick (task_tick), .task_ready (task_ready),
        .st_write_en (st_write_en), .st_layer_idx (st_layer_idx),
        .st_dnn_id (st_dnn_id), .st_prev_layer (st_prev_layer),
        .st_mem_cycles (st_mem_cycles), .st_compute_cycles (st_compute_cycles),
        .st_weight_fp (st_weight_fp), .st_ifmap_fp (st_ifmap_fp),
        .st_ofmap_fp (st_ofmap_fp), .st_batch (st_batch),
        .st_total_layers (st_total_layers),
        .mt_busy (mt_busy), .ct_busy (ct_busy),
        .mt_start_pulse (mt_start_pulse), .ct_start_pulse (ct_start_pulse),
        .mt_done_pulse (mt_done_pulse), .ct_done_pulse (ct_done_pulse),
        .mt_active_layer (mt_active_layer), .ct_active_layer (ct_active_layer),
        .ct_active_batch (ct_active_batch),
        .stat_total_cycles (stat_total_cycles),
        .stat_mt_busy_cycles (stat_mt_busy_cycles),
        .stat_ct_busy_cycles (stat_ct_busy_cycles),
        .stat_overlap_cycles (stat_overlap_cycles),
        .stat_both_idle_cycles (stat_both_idle_cycles),
        .stat_mt_tasks (stat_mt_tasks), .stat_ct_tasks (stat_ct_tasks),
        .stat_inferences (stat_inferences),
        .stat_bytes_moved (stat_bytes_moved),
        .stat_dram_requests (stat_dram_requests),
        .stat_sched_stall_cycles (stat_sched_stall_cycles),
        .stat_available_memory (stat_available_memory),
        .stat_layers_completed (stat_layers_completed),
        .stat_layers_expected (stat_layers_expected),
        .stat_incomplete (stat_incomplete)
    );

    //=========================================================================
    // Event capture -- one record per MT/CT start and done.
    //=========================================================================
    int unsigned ev_cycle [MAX_EVENTS];
    int unsigned ev_kind  [MAX_EVENTS];   // 0=mt_start 1=mt_done 2=ct_start 3=ct_done
    int unsigned ev_layer [MAX_EVENTS];
    int unsigned ev_batch [MAX_EVENTS];
    int unsigned ev_n = 0;

    int unsigned cyc = 0;

    task automatic push_event(int unsigned k, int unsigned l, int unsigned b);
        if (ev_n < MAX_EVENTS) begin
            ev_cycle[ev_n] = cyc;
            ev_kind [ev_n] = k;
            ev_layer[ev_n] = l;
            ev_batch[ev_n] = b;
            ev_n = ev_n + 1;
        end
    endtask

    always @(posedge clk) begin
        if (rst_n) begin
            cyc <= cyc + 1;
            if (mt_start_pulse) push_event(0, mt_active_layer, 1);
            if (mt_done_pulse)  push_event(1, mt_active_layer, 1);
            if (ct_start_pulse) push_event(2, ct_active_layer, ct_active_batch);
            if (ct_done_pulse)  push_event(3, ct_active_layer, ct_active_batch);
        end
    end

    //=========================================================================
    // Workload loader
    //=========================================================================
    task automatic load_workload(string path);
        int fd, code;
        int unsigned idx, d, p, mc, cc, wf, iff_, of, bt;
        string line;
        fd = $fopen(path, "r");
        if (fd == 0) begin
            $display("FATAL: cannot open workload file %s", path);
            $finish;
        end
        code = $fscanf(fd, "%d", n_layers);
        if (code != 1) begin
            $display("FATAL: bad workload header in %s", path);
            $finish;
        end
        for (int i = 0; i < int'(n_layers); i++) begin
            code = $fscanf(fd, "%d %d %d %d %d %d %d %d %d",
                           idx, d, p, mc, cc, wf, iff_, of, bt);
            if (code != 9) begin
                $display("FATAL: bad workload row %0d in %s (got %0d fields)",
                         i, path, code);
                $finish;
            end
            wl_dnn[idx]   = d;
            wl_prev[idx]  = p;
            wl_memc[idx]  = mc;
            wl_cmpc[idx]  = cc;
            wl_wfp[idx]   = wf;
            wl_ifp[idx]   = iff_;
            wl_ofp[idx]   = of;
            wl_batch[idx] = bt;
        end
        $fclose(fd);
    endtask

    //=========================================================================
    // Scheduling-table programming
    //=========================================================================
    task automatic program_table();
        @(negedge clk);
        for (int i = 0; i < int'(n_layers); i++) begin
            st_write_en       <= 1'b1;
            st_layer_idx      <= LAYER_ID_WIDTH'(i);
            st_dnn_id         <= DNN_ID_WIDTH'(wl_dnn[i]);
            st_prev_layer     <= LAYER_ID_WIDTH'(wl_prev[i]);
            st_mem_cycles     <= CYCLE_WIDTH'(wl_memc[i]);
            st_compute_cycles <= CYCLE_WIDTH'(wl_cmpc[i]);
            st_weight_fp      <= MEM_WIDTH'(wl_wfp[i]);
            st_ifmap_fp       <= MEM_WIDTH'(wl_ifp[i]);
            st_ofmap_fp       <= MEM_WIDTH'(wl_ofp[i]);
            st_batch          <= BATCH_WIDTH'(wl_batch[i]);
            st_total_layers   <= LAYER_ID_WIDTH'(n_layers);
            @(negedge clk);
        end
        st_write_en <= 1'b0;
        @(negedge clk);
    endtask

    //=========================================================================
    // Basic-task submission (schedulers 0..10 consume this queue)
    //=========================================================================
    task automatic submit_basic_tasks();
        @(negedge clk);
        for (int i = 0; i < int'(n_layers); i++) begin
            while (!task_ready) @(negedge clk);
            task_valid    <= 1'b1;
            task_id       <= 8'(i);
            // Declared burst time: the compiler's estimate of total service.
            burst_time    <= 16'((wl_memc[i] + wl_cmpc[i]) >> 4);
            task_priority <= 4'(i % 8);
            deadline      <= 32'(1000 * (i + 1));
            @(negedge clk);
            task_valid <= 1'b0;
            @(negedge clk);
        end
        task_valid <= 1'b0;
    endtask

    //=========================================================================
    // JSON writer
    //=========================================================================
    task automatic write_json(string path);
        int fd;
        real util_ct, util_mt, overlap_pct;
        fd = $fopen(path, "w");
        if (fd == 0) begin
            $display("FATAL: cannot open json output %s", path);
            $finish;
        end

        util_ct     = (stat_total_cycles == 0) ? 0.0 :
                      100.0 * real'(stat_ct_busy_cycles) / real'(stat_total_cycles);
        util_mt     = (stat_total_cycles == 0) ? 0.0 :
                      100.0 * real'(stat_mt_busy_cycles) / real'(stat_total_cycles);
        overlap_pct = (stat_total_cycles == 0) ? 0.0 :
                      100.0 * real'(stat_overlap_cycles) / real'(stat_total_cycles);

        $fwrite(fd, "{\n");
        $fwrite(fd, "  \"scheduler_select\": %0d,\n", sched_sel);
        $fwrite(fd, "  \"workload\": \"%s\",\n", wl_path);
        $fwrite(fd, "  \"config\": {\n");
        $fwrite(fd, "    \"dram_latency\": %0d,\n", dram_lat);
        $fwrite(fd, "    \"dram_bytes_per_cycle\": %0d,\n", dram_bw);
        $fwrite(fd, "    \"array_fill_drain\": %0d,\n", fill_drain);
        $fwrite(fd, "    \"onchip_mem_bytes\": %0d,\n", `ONCHIP_MEM_BYTES);
        $fwrite(fd, "    \"compute_bal_thresh\": %0d,\n", `COMPUTE_BAL_THRESH);
        $fwrite(fd, "    \"n_layers\": %0d\n", n_layers);
        $fwrite(fd, "  },\n");
        $fwrite(fd, "  \"stats\": {\n");
        $fwrite(fd, "    \"total_cycles\": %0d,\n",     stat_total_cycles);
        $fwrite(fd, "    \"mt_busy_cycles\": %0d,\n",   stat_mt_busy_cycles);
        $fwrite(fd, "    \"ct_busy_cycles\": %0d,\n",   stat_ct_busy_cycles);
        $fwrite(fd, "    \"overlap_cycles\": %0d,\n",   stat_overlap_cycles);
        $fwrite(fd, "    \"both_idle_cycles\": %0d,\n", stat_both_idle_cycles);
        $fwrite(fd, "    \"mt_tasks\": %0d,\n",         stat_mt_tasks);
        $fwrite(fd, "    \"ct_tasks\": %0d,\n",         stat_ct_tasks);
        $fwrite(fd, "    \"inferences\": %0d,\n",       stat_inferences);
        $fwrite(fd, "    \"bytes_moved\": %0d,\n",      stat_bytes_moved);
        $fwrite(fd, "    \"dram_requests\": %0d,\n",    stat_dram_requests);
        $fwrite(fd, "    \"sched_stall_cycles\": %0d,\n", stat_sched_stall_cycles);
        $fwrite(fd, "    \"array_utilization_pct\": %0.4f,\n", util_ct);
        $fwrite(fd, "    \"dma_utilization_pct\": %0.4f,\n",   util_mt);
        $fwrite(fd, "    \"overlap_pct\": %0.4f,\n",           overlap_pct);
        $fwrite(fd, "    \"layers_completed\": %0d,\n", stat_layers_completed);
        $fwrite(fd, "    \"layers_expected\": %0d,\n",  stat_layers_expected);
        $fwrite(fd, "    \"incomplete\": %0d,\n",       stat_incomplete);
        $fwrite(fd, "    \"timed_out\": %0d\n", (cyc >= timeout_cyc) ? 1 : 0);
        $fwrite(fd, "  },\n");

        $fwrite(fd, "  \"events\": [\n");
        for (int unsigned i = 0; i < ev_n; i++) begin
            $fwrite(fd, "    {\"c\": %0d, \"k\": %0d, \"l\": %0d, \"b\": %0d}%s\n",
                    ev_cycle[i], ev_kind[i], ev_layer[i], ev_batch[i],
                    (i == ev_n - 1) ? "" : ",");
        end
        $fwrite(fd, "  ]\n");
        $fwrite(fd, "}\n");
        $fclose(fd);
    endtask

    //=========================================================================
    // Main
    //=========================================================================
    initial begin
        void'($value$plusargs("sched=%d",      sched_sel));
        void'($value$plusargs("dram_lat=%d",   dram_lat));
        void'($value$plusargs("dram_bw=%d",    dram_bw));
        void'($value$plusargs("fill_drain=%d", fill_drain));
        void'($value$plusargs("timeout=%d",    timeout_cyc));
        void'($value$plusargs("workload=%s",   wl_path));
        void'($value$plusargs("json=%s",       json_path));

        load_workload(wl_path);

        rst_n = 1'b0;
        repeat (8) @(negedge clk);
        rst_n = 1'b1;
        repeat (4) @(negedge clk);

        program_table();

        if (sched_sel <= 10) submit_basic_tasks();

        run_enable <= 1'b1;

        fork
            begin : wait_done
                wait (run_done == 1'b1);
            end
            begin : wait_timeout
                while (cyc < timeout_cyc) @(posedge clk);
                $display("WARNING: timeout after %0d cycles (sched=%0d)",
                         cyc, sched_sel);
            end
        join_any
        disable fork;

        repeat (4) @(negedge clk);

        $display("sched=%0d cycles=%0d array_util=%0d%% overlap=%0d%% ct_tasks=%0d layers=%0d/%0d%s",
                 sched_sel, stat_total_cycles,
                 (stat_total_cycles == 0) ? 0 :
                     (100 * stat_ct_busy_cycles) / stat_total_cycles,
                 (stat_total_cycles == 0) ? 0 :
                     (100 * stat_overlap_cycles) / stat_total_cycles,
                 stat_ct_tasks,
                 stat_layers_completed, stat_layers_expected,
                 stat_incomplete ? "  *** INCOMPLETE ***" : "");

        write_json(json_path);
        $finish;
    end

endmodule : tb_multi_dnn_exec
