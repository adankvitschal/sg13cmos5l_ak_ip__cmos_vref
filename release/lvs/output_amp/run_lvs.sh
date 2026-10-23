#!/bin/sh
# Re-runs EXACTLY the netgen comparison this block's own release page
# reports under "## LVS", from the two netlists sitting next to this
# script -- so that claim can be checked independently, without the
# mh-analog-designer tool, without docker, and without the project's
# gitignored sim/ tree the original run happened in.
#
# Needs netgen on PATH and nothing else: netgen_setup.tcl here is
# self-contained (the PDK's own LVS setup file, Apache-2.0 header
# included, plus the tool's own device-class patch appended), so no
# $PDK_ROOT lookup happens at all.
#
#   output_amp_extracted_lvs.spice
#       ext2spice output of the layout cell -- connectivity only, no
#       parasitics (`ext2spice lvs`).
#   output_amp_schematic.spice
#       xschem netlist of the same block's materialized schematic.
#   lvs_report.txt / lvs_report.json
#       the report the release page quotes. This script writes
#       lvs_report_rerun.txt/.json instead, so nothing published is
#       overwritten and the two can be diffed.
set -e
cd "$(dirname "$0")"
netgen -batch lvs "output_amp_extracted_lvs.spice output_amp" "output_amp_schematic.spice output_amp" netgen_setup.tcl lvs_report_rerun.txt -json
echo "wrote lvs_report_rerun.txt -- diff it against lvs_report.txt"
