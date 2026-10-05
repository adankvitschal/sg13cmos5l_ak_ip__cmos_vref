# Slot 8 (Chipalooza IHP harness)

Slot 8 of `sg13cmos5l_ocd_chipalooza` (1 dedicated analog pad). Wrapper taken from the bringup
repo at `origin/main` commit `1906830` (it includes the metal5 power-pin fix of `41399a8`).

## Deliverable expected by the bringup flow (`scripts/get_project_gds.sh`)

- File `slot_8.gds` (or `slot_8.gds.gz`, never both) in `final/gds/` (IHP's preferred layout)
  or `gds/`; the script searches those two, then anywhere in the repo as a last resort.
- Its top cell must be named `slot_8`, written with full hierarchical processing (Magic's
  default). It is read verbatim as read-only GDS over the slot wrapper; every cell below the top
  gets a random prefix, so only the top-cell name matters.
- `config.txt` also has `s8_version: <branch> <commit>`; the commit freezes the project for
  tapeout, so push before it is set.

`final/gds/slot_8.gds` (repo root) is written by `write_gds.tcl` from `slot8_wrapper.mag` (top cell
`slot_8`, 38 cells, router labels left out). Regenerate it after every layout change; it has not
been checked with LVS or the KLayout DRC.

| Path | What |
| --- | --- |
| `bringup_ref/slot8_wrapper.mag` | Wrapper exactly as delivered by the bringup repo (outline, pins, obstruction). Do not edit. |
| `slot8_wrapper.mag` | Wrapper with `top` placed inside (`top_0`, referenced in place from `../top/top-default-5997f5`) and routed by hand. |
| `build_slot8.tcl` | Starts over from the reference (placement, `LABELS=1` for the router netlist). Refuses to overwrite `slot8_wrapper.mag` unless `FORCE=1`. |
| `write_gds.tcl` | Writes `final/gds/slot_8.gds`. Run from this directory. |
| `netlist.txt` | The 12 top-pin to wrapper-pin connections. |

## Pin map (top -> wrapper)

| top pin | wrapper pin | note |
| --- | --- | --- |
| `vbg` | `s8_an[0]` | the one dedicated pad (non-ESD side); `s8_an_0_esd` left open |
| `vbgsc` | `analog_bus0` | shared analog line (< 5 ohm switch, heavy capacitive load) |
| `vbgtg` | `analog_bus1` | shared analog line |
| `trim0..trim3` | `dig_in[0..3]` | |
| `ena` | `enable` | |
| `avdd` / `avss` | `vdd_3v3` / `vss_3v3` | |
| `dvdd` / `dvss` | `vdd_1v2` / `vss_1v2` | |

Not connected: `clk`, `reset`, `dig_in[4..23]`, `dig_out[*]`, `ibias0/1`, `vbias`, `analog_bus2/3`.
`vptat` is on `top.sym` but is not a port of the `top` layout, so it has no wrapper pin.

## Router netlist

`LABELS=1` on `build_slot8.tcl` adds the nets for the eda-env autoroute (plain labels with the same
name on the top pin and the wrapper pin, `[0]` written `_0`) and writes [netlist.txt](netlist.txt).
The Route tab then lists 12 unrouted nets. `vss_3v3` shows 3 pins (the wrapper has a second one on
the right edge, already tied by the frame): route it with a window around the left edge. The
labels must be removed after routing (equal names merge nets in extraction); `slot8_wrapper.mag`
still has them (`write_gds.tcl` leaves them out of the GDS).

## Geometry notes for routing

- Wrapper is 537.15 x 273 um (107430 x 54600 internal units, 5 nm each). `top` sits with its bbox
  lower-left at (5000, 14000), i.e. translation (5500, 13700); its pins are metal2 stubs
  (bottom edge: `avdd avss dvdd dvss trim* ena`; top edge: `vbg vbgsc vbgtg`).
- Digital pins on the left edge are metal3, 0.22 um tall at 0.44 um pitch; power rails are
  metal5 strips at x = 0..2 um; `s8_an[0]` is on the right edge (metal3) ~430 um from `top`.
- eda-env autoroute findings: it ignores `flabel`/`port` labels (needs plain labels with the same
  name at both ends), cannot use net names with `[`, hit its search limit on the 430 um `vbg` run,
  and could not leave `top`'s bottom pins for the power nets. Remove any temporary plain labels
  afterwards, since equal names merge nets in extraction and hide open routes.
