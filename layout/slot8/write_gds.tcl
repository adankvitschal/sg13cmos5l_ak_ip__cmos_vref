# write_gds.tcl -- write ../../final/gds/slot_8.gds from slot8_wrapper.mag.  The bringup flow
# (scripts/get_project_gds.sh) wants a top cell named slot_8 in final/gds/.  Run from layout/slot8:
#   magic -dnull -noconsole -rcfile $PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc ./write_gds.tcl
# slot8_wrapper.mag is not touched:  a copy named slot_8.mag is made without the plain (router)
# labels, written out and deleted.  Prints the DRC count of the wrapper.
locking disable
set fh [open slot8_wrapper.mag]
set keep {}
foreach l [split [read $fh] "
"] {if {![string match "rlabel *" $l]} {lappend keep $l}}
close $fh
set fh [open slot_8.mag w]
puts -nonewline $fh [join $keep "
"]
close $fh
file mkdir ../../final/gds
load slot_8
drc catchup
puts "DRC: [drc listall count]"
gds write ../../final/gds/slot_8.gds
file delete slot_8.mag
quit -noprompt
