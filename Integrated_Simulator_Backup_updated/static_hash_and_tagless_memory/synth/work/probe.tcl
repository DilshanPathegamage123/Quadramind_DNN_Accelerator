create_project -in_memory -part xczu7ev-ffvc1156-2-e
read_verilog -sv ../../../sim_framework/rtl/memory/stamp_based_memory_controller.sv
synth_design -top stamp_based_memory_controller -part xczu7ev-ffvc1156-2-e -mode out_of_context -no_iobuf
puts "PROBE_TOTAL_CELLS [llength [get_cells -hier]]"
set groups [dict create]
foreach c [get_cells -hier] {
  set g [get_property -quiet PRIMITIVE_GROUP $c]
  if {$g eq ""} { set g "<empty>" }
  dict incr groups $g
}
puts "PROBE_GROUPS $groups"
puts "PROBE_UTIL_START"
puts [report_utilization -return_string]
puts "PROBE_UTIL_END"
