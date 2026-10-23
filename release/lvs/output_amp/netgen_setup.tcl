########################################################################
#
# Copyright 2026 IHP PDK Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
########################################################################

#---------------------------------------------------------------
# Setup file for netgen LVS
# IHP ihp-sg13cmos5l
#---------------------------------------------------------------
permute default
property default
property parallel none

# Allow override of default #columns in the output format.
catch {format $env(NETGEN_COLUMNS)}

#---------------------------------------------------------------
# For the following, get the cell lists from
# circuit1 and circuit2.
#---------------------------------------------------------------

set cells1 [cells list -all -circuit1]
set cells2 [cells list -all -circuit2]

#-------------------------------------------
# Resistors (except metal)
#-------------------------------------------

set devices {}
lappend devices ptap1
lappend devices ntap1
lappend devices rsil
lappend devices rppd
lappend devices rhigh

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	permute "-circuit1 $dev" 1 2
	property "-circuit1 $dev" series enable
	property "-circuit1 $dev" series {w critical}
	property "-circuit1 $dev" series {l add}
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {l critical}
	property "-circuit1 $dev" parallel {w add}
	property "-circuit1 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	property "-circuit1 $dev" delete b mm_ok
    }
    if {[lsearch $cells2 $dev] >= 0} {
	permute "-circuit2 $dev" 1 2
	property "-circuit2 $dev" series enable
	property "-circuit2 $dev" series {w critical}
	property "-circuit2 $dev" series {l add}
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" parallel {l critical}
	property "-circuit2 $dev" parallel {w add}
	property "-circuit2 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete b mm_ok
    }
}

#-------------------------------------------
# MRM (metal) resistors
#-------------------------------------------

set devices {}
lappend devices rm1
lappend devices rm2
lappend devices rm3
lappend devices rm4
lappend devices rm5

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	permute "-circuit1 $dev" end_a end_b
	property "-circuit1 $dev" series enable
	property "-circuit1 $dev" series {w critical}
	property "-circuit1 $dev" series {l add}
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {l critical}
	property "-circuit1 $dev" parallel {w add}
	property "-circuit1 $dev" tolerance {l 10.0} {w 10.0}
	# Ignore these properties
	property "-circuit1 $dev" delete mult
    }
    if {[lsearch $cells2 $dev] >= 0} {
	permute "-circuit2 $dev" end_a end_b
	property "-circuit2 $dev" series enable
	property "-circuit2 $dev" series {w critical}
	property "-circuit2 $dev" series {l add}
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" parallel {l critical}
	property "-circuit2 $dev" parallel {w add}
	property "-circuit2 $dev" tolerance {l 10.0} {w 10.0}
	# Ignore these properties
	property "-circuit2 $dev" delete mult
    }
}

#-------------------------------------------
# (MOS) transistors and varactor
#-------------------------------------------

set devices {}
lappend devices sg13_hv_nmos
lappend devices sg13_hv_pmos
lappend devices sg13_lv_nmos
lappend devices sg13_lv_pmos
lappend devices sg13_hv_svaricap

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	permute "-circuit1 $dev" 1 3
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {l critical}
	property "-circuit1 $dev" parallel {w add}
	property "-circuit1 $dev" tolerance {w 0.01} {l 0.01}
	# Ignore these properties
	property "-circuit1 $dev" delete ng as ad pd ps trise z1 z2 wmin rfmode mm_ok pre_layout
    }
    if {[lsearch $cells2 $dev] >= 0} {
	permute "-circuit2 $dev" 1 3
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" parallel {l critical}
	property "-circuit2 $dev" parallel {w add}
	property "-circuit2 $dev" tolerance {w 0.01} {l 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete ng as ad pd ps trise z1 z2 wmin rfmode mm_ok pre_layout
    }
}

#-------------------------------------------
# (Lateral) bipolar transistor
#-------------------------------------------

set devices {}
lappend devices pnpMPA

# TODO: check parallel merge
foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {le critical}
	property "-circuit1 $dev" parallel {we add}
	property "-circuit1 $dev" tolerance {we 0.01} {le 0.01}
	# Ignore these properties
	property "-circuit1 $dev" delete Nx Ny
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" parallel {le critical}
	property "-circuit2 $dev" parallel {we add}
	property "-circuit2 $dev" tolerance {we 0.01} {le 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete Nx Ny
    }
}

#---------------------------------------------------------------------
# Extended drain MOSFET devices.  These have asymmetric source and
# drain, and so the source and drain are not permutable.  (Placeholder)
#---------------------------------------------------------------------

set devices {}

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {l critical}
	property "-circuit1 $dev" parallel {w add}
	property "-circuit1 $dev" tolerance {w 0.01} {l 0.01}
	# Ignore these properties
	property "-circuit1 $dev" delete as ad ps pd mult sa sb sd nf nrd nrs area perim topography
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" parallel {l critical}
	property "-circuit2 $dev" parallel {w add}
	property "-circuit2 $dev" tolerance {w 0.01} {l 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete as ad ps pd mult sa sb sd nf nrd nrs area perim topography
    }
}

#---------------------------------------------------------------------
# (MOS) ESD transistors. (Placeholder)
#---------------------------------------------------------------------

set devices {}

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	permute "-circuit1 $dev" 1 3
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {l critical}
	property "-circuit1 $dev" parallel {w add}
	property "-circuit1 $dev" tolerance {w 0.07} {l 0.01}
	# Ignore these properties
	property "-circuit1 $dev" delete as ad ps pd mult sa sb sd nf nrd nrs area perim topography
    }
    if {[lsearch $cells2 $dev] >= 0} {
	permute "-circuit2 $dev" 1 3
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" parallel {l critical}
	property "-circuit2 $dev" parallel {w add}
	property "-circuit2 $dev" tolerance {w 0.07} {l 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete as ad ps pd mult sa sb sd nf nrd nrs area perim topography
    }
}

#-------------------------------------------
# diodes
#-------------------------------------------

set devices {}
lappend devices dantenna
lappend devices dpantenna

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {l critical}
	property "-circuit1 $dev" parallel {w add}
	property "-circuit1 $dev" tolerance {w 0.01} {l 0.01}
	# Ignore these properties
	property "-circuit1 $dev" delete DEV_A DEV_P DEV_C
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" parallel {l critical}
	property "-circuit2 $dev" parallel {w add}
	property "-circuit2 $dev" tolerance {w 0.01} {l 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete DEV_A DEV_P DEV_C
    }
}

#-------------------------------------------
# capacitors
#-------------------------------------------

set devices {}
lappend devices cap_cmomf
lappend devices cap_cmomi

# Do not allow parallel combination of capacitors unless all valid
# parameters match.  The device value depends on geometry and the number
# of layers used, all of which must be specified for each device.  
# However, the cap_cmomf device model does not define the capacitance to
# substrate, so the two pins are effectively permutable.  cap_cmomi
# terminals are not permutable.

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	if {$dev == "cap_cmomf"} {
	    permute "-circuit1 $dev" 1 2
	}
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" tolerance {w 0.01} {l 0.01}
	property "-circuit1 $dev" tolerance {mmin 0} {mmax 0} {subblock 0}
	# Ignore these properties
	property "-circuit1 $dev" delete mm_ok
    }
    if {[lsearch $cells2 $dev] >= 0} {
	if {$dev == "cap_cmomf"} {
	    permute "-circuit2 $dev" 1 2
	}
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" tolerance {w 0.01} {l 0.01}
	property "-circuit2 $dev" tolerance {mmin 0} {mmax 0} {subblock 0}
	# Ignore these properties
	property "-circuit2 $dev" delete mm_ok
    }
}

#-------------------------------------------
# Fixed-layout devices
# ESD devices
#-------------------------------------------

set devices {}
lappend devices nmoscl_2
lappend devices nmoscl_4

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	# Ignore these properties
	property "-circuit1 $dev" delete mult
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $dev" parallel enable
	# Ignore these properties
	property "-circuit2 $dev" delete mult
    }
}

#---------------------------------------------------------------
# Schematic cells which are not extractable
#---------------------------------------------------------------

set devices {}
lappend devices Rparasitic
lappend devices cparasitic

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	ignore class "-circuit1 $dev"
    }
    if {[lsearch $cells2 $dev] >= 0} {
	ignore class "-circuit2 $dev"
    }
}

#---------------------------------------------------------------
# Allow the fill, decap, etc., cells to be parallelized
#---------------------------------------------------------------

set devices {}
lappend devices sg13cmos5l_antennap

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $cell" parallel enable
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $cell" parallel enable
    }
}

foreach cell $cells1 {
    if {[regexp {sg13cmos5l_decap_[[:digit:]]+} $cell match]} {
	property "-circuit1 $cell" parallel enable
    }
    if {[regexp {sg13cmos5l_fill_[[:digit:]]+} $cell match]} {
	property "-circuit1 $cell" parallel enable
    }
}
foreach cell $cells2 {
    if {[regexp {sg13cmos5l_decap_[[:digit:]]+} $cell match]} {
	property "-circuit2 $cell" parallel enable
    }
    if {[regexp {sg13cmos5l_fill_[[:digit:]]+} $cell match]} {
	property "-circuit2 $cell" parallel enable
    }
}

#---------------------------------------------------------------
# Match pins on black-box cells if LVS is called with "-blackbox"
#---------------------------------------------------------------

if {[model blackbox]} {
    foreach cell $cells1 {
	if {[model "-circuit1 $cell"] == "blackbox"} {
	    if {[lsearch $cells2 $cell] >= 0} {
		puts stdout "Matching pins of $cell in circuits 1 and 2"
		equate pins "-circuit1 $cell" "-circuit2 $cell"
	    }
	}
    }
}

#---------------------------------------------------------------

# --- project-local patch: cap_cmomf/cap_cmomi as netgen's own capacitor
# model type (IHP-Open-PDK PR #1241 not yet merged, see magic_layout.py's
# own _NETGEN_LOCAL_PATCH docstring) ---
foreach cell $cells1 {
    if {[regexp {^cap_cmom[fi](_|$)} $cell]} {
        model "-circuit1 $cell" capacitor
        # ext2spice's own subckt header names cap_cmomf's real two pins
        # "c1"/"c2" (unlike circuit2's side, an undefined-reference
        # placeholder netgen itself numbers "1"/"2") -- permute needs each
        # side's own actual pin names/numbers, confirmed live that "1 2"
        # here silently did nothing (circuit1 stayed unpermuted while
        # circuit2 alone showed "(1,2)" combined) where "c1 c2" does.
        permute "-circuit1 $cell" c1 c2
    }
}
foreach cell $cells2 {
    if {[regexp {^cap_cmom[fi](_|$)} $cell]} {
        model "-circuit2 $cell" capacitor
        permute "-circuit2 $cell" 1 2
    }
}

# "all pins shorted" dummy transistors (common-centroid array edge/matching
# dummies, layout_spec.json's own "dummy": true instances, e.g.
# sbvfcm_M6_M7_d01..d04) were investigated here as a source of LVS noise --
# confirmed live (raw extracted netlist) they really do tie all 4 of their
# OWN terminals to one net ("Xsbvfcm_M6_M7_d01 vss_uq3 vss_uq3 vss_uq3
# vss_uq3 sg13_hv_nmos_2XZV6D"). netgen's own `ignore shorted <cellname>`
# is the documented mechanism for exactly this case -- but applying it to
# the shared unit-cell wrapper class (e.g. "sg13_hv_nmos_2XZV6D", a
# per-layout Magic hash, looped over via regexp match the same way
# cap_cmomf's block above does) SEGFAULTS netgen 1.5.321 outright
# (confirmed live: `timeout ... netgen ...` -> "dumped core", exit 139,
# right after this setup file's own device-property/model messages, no
# Tcl-level error text at all -- a real crash in netgen's own native code,
# not a Tcl syntax issue worth chasing further here). No workaround
# attempted from this side of netgen's own API; the actual fix for these
# dummies is physical (connect their shared net to the real vss rail via
# routing -- see the Layout tab's own Verification flow for the up to date
# state of that), not a netgen setup-file trick.
