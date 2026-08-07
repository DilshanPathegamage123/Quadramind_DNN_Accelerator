#=============================================================================
# Out-of-context synthesis of the on-chip memory subsystem, for measured area
# and timing numbers.
#
# Scope: memory management module only. Nothing here touches the systolic
# array, the schedulers or the loop optimizer.
#
# Every configuration is synthesised out-of-context (no I/O buffers), so the
# reported LUT/FF/BRAM counts are the logic itself and are directly comparable
# between configurations.
#
# Emits: area_results.csv
#
# Usage: vivado -mode batch -source synth_area.tcl -tclargs <rtl_dir> <out_dir>
#=============================================================================

set rtl_dir [lindex $argv 0]
set out_dir [lindex $argv 1]
set part    "xczu7ev-ffvc1156-2-e"   ;# ZCU104, the board named in the project

set harness_dir [file normalize [file dirname [info script]]]

file mkdir $out_dir
set csv_path $out_dir/area_results.csv

# Resume support: synthesising the deeper metadata RAMs takes many minutes, so
# a rerun should not redo configurations that already have a row.
set done_configs {}
if {[file exists $csv_path]} {
    set fh [open $csv_path r]
    foreach line [split [read $fh] "\n"] {
        set line [string trim $line]
        if {$line eq "" || [string match "config,*" $line]} { continue }
        lappend done_configs [lindex [split $line ","] 0]
    }
    close $fh
    set csv [open $csv_path a]
    puts "Resuming: [llength $done_configs] configuration(s) already done."
} else {
    set csv [open $csv_path w]
    puts $csv "config,scheme,knob,knob_value,luts,ffs,brams,dsps,lutram,wns_ns,fmax_mhz"
}

# Target 100 MHz; WNS then tells us the real achievable frequency.
set period 10.0

#-----------------------------------------------------------------------------
# Pull one numeric cell out of the report_utilization table. Rows look like:
#   | CLB LUTs*               |  6435 |     0 |          0 |    230400 |  2.79 |
# The leading label may carry a trailing '*' and arbitrary indentation.
#-----------------------------------------------------------------------------
proc util_field {rpt label} {
    foreach line [split $rpt "\n"] {
        if {![string match "|*" $line]} { continue }
        set cols [split $line "|"]
        if {[llength $cols] < 3} { continue }
        set name [string trim [lindex $cols 1]]
        set name [string trimright $name "*"]
        set name [string trim $name]
        if {$name eq $label} {
            set v [string trim [lindex $cols 2]]
            if {[string is integer -strict $v]} { return $v }
            # Some rows report fractional usage; round to nearest integer.
            if {[string is double -strict $v]} { return [expr {int($v + 0.5)}] }
        }
    }
    return 0
}

#-----------------------------------------------------------------------------
# One synthesis run.  Returns by writing a CSV row.
#-----------------------------------------------------------------------------
proc run_one {csv part period rtl_dir out_dir name scheme knob knob_value top files generics} {
    global done_configs harness_dir
    if {[lsearch -exact $done_configs $name] >= 0} {
        puts "  Skipping $name (already in area_results.csv)"
        return
    }
    puts "\n=========================================================="
    puts "  Synthesising $name  (top = $top)"
    puts "=========================================================="

    create_project -in_memory -part $part

    foreach f $files {
        set path [file join $rtl_dir $f]
        if {![file exists $path]} {
            # Harness-only sources (e.g. paged_mgmt_wrap.sv) live next to this
            # script, not in the RTL tree.
            set path [file join $harness_dir [file tail $f]]
        }
        if {[string match "*.v" $f]} {
            read_verilog $path
        } else {
            read_verilog -sv $path
        }
    }

    set gen_args {}
    foreach {g v} $generics { lappend gen_args "$g=$v" }

    if {[llength $gen_args] > 0} {
        synth_design -top $top -part $part -mode out_of_context \
                     -generic $gen_args -no_iobuf
    } else {
        synth_design -top $top -part $part -mode out_of_context -no_iobuf
    }

    # Constrain a clock so timing numbers mean something.
    if {[llength [get_ports -quiet clk]] > 0} {
        create_clock -name clk -period $period [get_ports clk]
    }
    opt_design -quiet

    # Read the utilization report rather than filtering on PRIMITIVE_GROUP.
    # On UltraScale+ that property only returns coarse buckets (CLB / REGISTER
    # / OTHERS), so it cannot separate LUTs from LUTRAM or count BRAM tiles.
    # report_utilization is the authoritative source.
    set rpt [report_utilization -return_string]

    set luts   [util_field $rpt "CLB LUTs"]
    set ffs    [util_field $rpt "CLB Registers"]
    set brams  [util_field $rpt "Block RAM Tile"]
    set dsps   [util_field $rpt "DSPs"]
    set lutram [util_field $rpt "LUT as Memory"]

    set wns 0.0
    set fmax 0.0
    if {[llength [get_clocks -quiet]] > 0} {
        set tp [get_property SLACK [get_timing_paths -quiet -max_paths 1 -setup]]
        if {$tp ne ""} {
            set wns $tp
            set achieved [expr {$period - $wns}]
            if {$achieved > 0} { set fmax [expr {1000.0 / $achieved}] }
        }
    }

    puts $csv [format "%s,%s,%s,%s,%d,%d,%d,%d,%d,%.3f,%.1f" \
               $name $scheme $knob $knob_value $luts $ffs $brams $dsps $lutram $wns $fmax]
    flush $csv

    puts "  -> LUT=$luts  FF=$ffs  BRAM=$brams  LUTRAM=$lutram  WNS=${wns}ns  Fmax=${fmax}MHz"
    close_project
}

#-----------------------------------------------------------------------------
# 2. STATIC scheme management logic: the delta-op sequencer.
#    Swept over metadata depth, which is the scheme's scaling cost.
#-----------------------------------------------------------------------------
foreach md {256 512 1024} {
    run_one $csv $part $period $rtl_dir $out_dir \
        "stamp_ctrl_m$md" "STAMP (static)" "metadata_depth" $md \
        stamp_based_memory_controller {memory/stamp_based_memory_controller.sv} \
        [list ADDR_WIDTH 32 DATA_WIDTH 32 SPAD_DEPTH 4096 METADATA_DEPTH $md]
}

#-----------------------------------------------------------------------------
# 3. DYNAMIC scheme management logic: per-port address translation.
#    Swept over page count, its equivalent scaling cost.
#-----------------------------------------------------------------------------
foreach np {128 256 512} {
    set vpn [expr {int(ceil(log($np)/log(2)))}]
    run_one $csv $part $period $rtl_dir $out_dir \
        "paged_mgmt_p$np" "PAGED (dynamic)" "num_pages" $np \
        paged_mgmt_wrap {memory/paged_table.v paged_mgmt_wrap.sv} \
        [list N_PORTS 4 NUM_PAGES $np VPN_WIDTH $vpn PPN_WIDTH 20]
}

#-----------------------------------------------------------------------------
# 1. Shared scratchpad, swept over bank count.
#    Both schemes need this; it is the area cost of banking itself, and pairs
#    with the measured bank-conflict counts.
#
#    NOTE ON DEPTH: this scratchpad has 5 concurrent read ports and 5 write
#    ports. No FPGA block-RAM primitive supports that (BRAM is at most true
#    dual-port), so Vivado must implement it in LUTs/registers. At DEPTH=4096
#    that is 131,072 bits and synthesis refuses outright. Synthesising at
#    DEPTH=256 keeps the run tractable while preserving the *relative*
#    comparison across bank counts, which is what this sweep is for.
#    The refusal at 4096 is itself a reportable result: a genuinely
#    multi-ported scratchpad does not map to BRAM, which is precisely why real
#    accelerators bank the memory and give each bank a single port.
#-----------------------------------------------------------------------------
set spad_depth 256
foreach nb {1 2 4 8 16} {
    run_one $csv $part $period $rtl_dir $out_dir \
        "scratchpad_b$nb" "Shared scratchpad" "num_banks" $nb \
        scratchpad_ram {memory/scratchpad_ram.sv} \
        [list DATA_WIDTH 32 DEPTH $spad_depth N_PORTS 5 NUM_BANKS $nb]
}

#close $csv
puts "\nWrote $out_dir/area_results.csv"
