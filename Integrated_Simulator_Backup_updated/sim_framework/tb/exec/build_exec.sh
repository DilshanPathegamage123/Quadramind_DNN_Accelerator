#!/usr/bin/env bash
# Build the dual-issue multi-DNN execution simulator with Verilator.
#
# ONCHIP_MEM_BYTES is a compile-time parameter inside the schedulers, so the
# on-chip capacity sweep re-elaborates; every other sweep dimension is a
# runtime plusarg. Pass a capacity to get a separate binary per point.
#
#   ./build_exec.sh [onchip_bytes] [compute_bal_thresh]
set -euo pipefail

ONCHIP=${1:-46137344}          # 44 MiB, the AI-MT paper's Table 1a figure
BALTHRESH=${2:-1000}

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FW="$(cd "$HERE/../.." && pwd)"

VERILATOR_ROOT_DIR="${VERILATOR_INSTALL:-/tmp/claude-1000/-home-malinga-DNN-accelerator-dilshan/75e12d63-aa87-467d-85de-449389dcc604/scratchpad/verilator-install}"
VERILATOR_BIN="$VERILATOR_ROOT_DIR/bin/verilator"
if ! command -v "$VERILATOR_BIN" >/dev/null 2>&1; then
    VERILATOR_BIN="$(command -v verilator)"
fi

OBJDIR="$FW/build/exec_sim_${ONCHIP}_${BALTHRESH}"
mkdir -p "$OBJDIR"

"$VERILATOR_BIN" --binary --timing -j "$(nproc)" \
    -DONCHIP_MEM_BYTES="$ONCHIP" \
    -DCOMPUTE_BAL_THRESH="$BALTHRESH" \
    --top-module tb_multi_dnn_exec \
    -Wno-fatal \
    --Mdir "$OBJDIR" \
    -o exec_sim \
    "$FW/rtl/pkg/sim_framework_pkg.sv" \
    "$FW/rtl/schedulers/task_scheduler.sv" \
    "$FW/rtl/schedulers/advanced_task_scheduler.sv" \
    "$FW/rtl/schedulers/multi_scheduler_wrapper.sv" \
    "$FW/rtl/schedulers/aimt_scheduler.sv" \
    "$FW/rtl/schedulers/batchdnn_scheduler.sv" \
    "$FW/rtl/schedulers/batchdnn_pp_scheduler.sv" \
    "$FW/rtl/schedulers/dnn_scheduler_wrapper.sv" \
    "$FW/rtl/schedulers/unified_scheduler_wrapper.sv" \
    "$FW/rtl/exec/dram_model.sv" \
    "$FW/rtl/exec/mt_engine.sv" \
    "$FW/rtl/exec/ct_engine.sv" \
    "$FW/rtl/exec/multi_dnn_exec_top.sv" \
    "$FW/tb/exec/tb_multi_dnn_exec.sv"

echo "built: $OBJDIR/exec_sim"
