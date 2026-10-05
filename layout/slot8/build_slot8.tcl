# build_slot8.tcl -- put the `top` layout into the Chipalooza slot-8 wrapper (placement only;
# the pins are NOT routed, see README.md for the pin map).
#
# Run from layout/slot8:
#   magic -dnull -noconsole -rcfile $PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc ./build_slot8.tcl
#   LABELS=1 magic ...     also adds the router netlist (see below)
# Starts from the pristine wrapper in bringup_ref/ (as delivered by the bringup repo), so it can be
# it OVERWRITES slot8_wrapper.mag, including any routing done by hand, so it refuses to run when
# that file exists unless FORCE=1.  (Only needed to start over from the bringup wrapper.)
#
# LABELS=1 -- router netlist.  The eda-env autoroute finds nets by plain labels (not flabel/port)
# carrying the same name on every pin of the net, so each connection below gets a plain label on
# the top pin (a 1:1 metal2 marker is painted under it, because a label needs paint in the wrapper
# cell) and one on the wrapper pin.  Names use "_" instead of "[ ]" (Magic cell names, and the
# router names its route cells after the net, cannot contain "[").
# Equal label names merge nets in extraction, which would hide an open route:  strip them once
# routed (rebuild without LABELS and re-route, or delete the plain labels / markers by hand).

locking disable
set here [file dirname [file normalize [info script]]]

if {[file exists slot8_wrapper.mag] && !([info exists ::env(FORCE)] && $::env(FORCE) eq "1")} {
    puts "slot8_wrapper.mag exists (routing would be lost): set FORCE=1 to rebuild"
    quit -noprompt
}
file copy -force $here/bringup_ref/slot8_wrapper.mag slot8_wrapper.mag

# top's bbox lower-left lands at (TX,TY) (internal units, 1 unit = 5 nm)
set TX 5000
set TY 14000
set DX [expr {$TX + 500}]
set DY [expr {$TY - 300}]

load slot8_wrapper
box values ${TX}i ${TY}i ${TX}i ${TY}i
getcell ../top/top-default-5997f5/top
box values 0i 0i 0i 0i

# top pin | wrapper pin | rect of the top pin in top coordinates (metal2).  vptat is not a port of
# the top layout.
set pins {
    {avdd   vdd_3v3      9300   500  9500   700}
    {avss   vss_3v3     10700   400 10900   500}
    {dvdd   vdd_1v2     12600   500 12800   700}
    {dvss   vss_1v2     12900   500 13100   700}
    {trim0  dig_in[0]   12353   500 12500   700}
    {trim1  dig_in[1]   12000   500 12200   700}
    {trim2  dig_in[2]   11700   500 11900   700}
    {trim3  dig_in[3]   11400   500 11600   700}
    {ena    enable      11100   500 11300   700}
    {vbg    s8_an[0]    15800 13000 16000 13200}
    {vbgsc  analog_bus0 17000 13000 17200 13200}
    {vbgtg  analog_bus1 16600 13000 16800 13200}
}
proc rn {n} {string map {[ _ ] {}} $n}

if {[info exists ::env(LABELS)] && $::env(LABELS) eq "1"} {
    set nl [open $here/netlist.txt w]
    puts $nl "# slot 8 router netlist: net (router label) = top pin + wrapper pin"
    foreach p $pins {
        lassign $p tpin wpin x0 y0 x1 y1
        box values [expr {$x0+$DX}]i [expr {$y0+$DY}]i [expr {$x1+$DX}]i [expr {$y1+$DY}]i
        paint metal2
        label [rn $wpin] center metal2
        puts $nl [format "%-12s = top_0/%-6s  %s" [rn $wpin] $tpin $wpin]
    }
    close $nl
    # wrapper side: the pin metal is in the pristine wrapper's flabel lines (same name, same layer)
    set fh [open $here/bringup_ref/slot8_wrapper.mag]
    set lines [split [read $fh] "\n"]
    close $fh
    set wanted [lmap p $pins {lindex $p 1}]
    foreach l $lines {
        if {[regexp {^flabel (\S+) (-?\d+) (-?\d+) (-?\d+) (-?\d+) \d+ \S+ \d+ \d+ \d+ \d+ (\S+)$} $l -> lay x0 y0 x1 y1 name] && $name in $wanted} {
            box values ${x0}i ${y0}i ${x1}i ${y1}i
            label [rn $name] center $lay
        }
    }
    box values 0i 0i 0i 0i
}
save slot8_wrapper
