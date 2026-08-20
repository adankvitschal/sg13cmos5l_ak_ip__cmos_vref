"""Parser for the area test: a static W*L*ng*m sum over output_amp's sized
devices in an xschem-expanded netlist -- no simulation involved (see
config.json's "simulator": "netlist" for this test). Reuses
tb_amp_power.sch purely as a cheap vehicle to get xschem to expand the
DUT's devices; the .op analysis inside it never actually runs for this
test."""
from _common import estimate_area_um2, in_spec

# Analog-layout overhead over raw active-device area (wells, guard rings,
# routing) -- schematic-only proxy, not a DRC-clean layout number. Same
# factor as cmos_vref's area test for comparability across blocks.
OVERHEAD_FACTOR = 2.5


def extract(data_path):
    netlist_text = data_path.read_text(encoding="utf-8")
    return estimate_area_um2(netlist_text, OVERHEAD_FACTOR)


def evaluate(runs, outputs, plot_base=None):
    """Area doesn't vary by corner/temperature -- this test declares no
    conditions, so runs has exactly one entry (the default corner/
    temperature combination)."""
    spec = outputs[0]
    value = runs[0]["estimated_area_um2"]
    return [{
        "name": spec["description"],
        "value": value,
        "unit": spec["unit"],
        "minimum": spec.get("minimum"),
        "maximum": spec.get("maximum"),
        "pass": in_spec(value, spec),
    }]
