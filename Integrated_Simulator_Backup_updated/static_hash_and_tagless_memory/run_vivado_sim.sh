#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Regenerate the stamp-based memory controller verification evidence.
#
#   1. runs stamp_compiler.py       -> stamp_metadata.json
#                                      delta_ops.hex
#                                      stamp_phase_table.svh
#   2. runs stamp_analyzer.py       -> stamp_analysis_summary.txt
#   3. compiles + simulates the RTL testbench in Vivado xsim
#   4. copies the console log into sim_framework/results/vivado/
#
# Usage:   ./run_vivado_sim.sh
#          VIVADO_ROOT=/path/to/Vivado ./run_vivado_sim.sh
# ---------------------------------------------------------------------------
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
BUILD="$HERE/.xsim_build"
RESULTS="$REPO/sim_framework/results/vivado"

VIVADO_ROOT="${VIVADO_ROOT:-/FYP_Vivado/2025.2/Vivado}"

echo "==> 1/4  Running the stamp compiler"
cd "$HERE"
python3 stamp_compiler.py

echo
echo "==> 2/4  Running the stamp analyzer"
python3 stamp_analyzer.py > /dev/null
echo "    stamp_analysis_summary.txt updated"

echo
echo "==> 3/4  Compiling and simulating in Vivado xsim"
if [[ ! -f "$VIVADO_ROOT/settings64.sh" ]]; then
    echo "ERROR: Vivado not found at $VIVADO_ROOT" >&2
    echo "       Set VIVADO_ROOT=/path/to/Vivado and re-run." >&2
    exit 1
fi
# shellcheck disable=SC1091
source "$VIVADO_ROOT/settings64.sh"

rm -rf "$BUILD"
mkdir -p "$BUILD"
cp stamp_memory_pkg.sv \
   stamp_based_memory_controller.sv \
   tb_stamp_based_memory_controller.sv \
   delta_ops.hex \
   stamp_phase_table.svh \
   "$BUILD/"

cd "$BUILD"
xvlog -sv --nolog -i . \
      stamp_memory_pkg.sv \
      stamp_based_memory_controller.sv \
      tb_stamp_based_memory_controller.sv > compile.log 2>&1
xelab -debug typical --nolog tb_stamp_based_memory_controller -s tb_sim > elab.log 2>&1
xsim tb_sim -runall --nolog > sim_output.txt 2>&1

echo
echo "==> 4/4  Results"
PASSES=$(grep -c 'PASS' sim_output.txt || true)
FAILS=$(grep -c 'FAIL  ' sim_output.txt || true)
echo "    PASS assertions : $PASSES"
echo "    FAIL assertions : $FAILS"

mkdir -p "$RESULTS"
cp sim_output.txt "$RESULTS/stamp_controller_xsim.log"
echo "    log copied to sim_framework/results/vivado/stamp_controller_xsim.log"

echo
grep -E "phases replayed|delta ops executed|stats_" sim_output.txt | tail -12

if [[ "$FAILS" -ne 0 ]]; then
    echo
    echo "FAILURES PRESENT:" >&2
    grep 'FAIL  ' sim_output.txt >&2
    exit 1
fi

echo
echo "All assertions passed."
