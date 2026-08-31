"""Parser for the area test: a static W*L*ng*m sum over output_amp's sized
devices in an xschem-expanded netlist -- no simulation involved (see
config.json's "simulator": "netlist" for this test). Reuses
tb_amp_power.sch purely as a cheap vehicle to get xschem to expand the
DUT's devices; the .op analysis inside it never actually runs for this
test."""
from parser_common import estimate_area_um2, typical_min_max

# Analog-layout overhead over raw active-device area (wells, guard rings,
# routing) -- schematic-only proxy, not a DRC-clean layout number. Same
# factor as cmos_vref's area test for comparability across blocks.
OVERHEAD_FACTOR = 2.5


def extract(data_path):
    netlist_text = data_path.read_text(encoding="utf-8")
    return estimate_area_um2(netlist_text, OVERHEAD_FACTOR)


def evaluate(runs, outputs, typical, plot_base=None):
    """Area doesn't vary by corner/temperature -- this test declares no
    conditions, so runs has exactly one entry (the default corner/
    temperature combination), and typical == min == max trivially."""
    spec = outputs[0]
    result = typical_min_max(runs, typical, lambda r: r["estimated_area_um2"])
    return [{
        "name": spec["description"],
        "typical": result["typical"], "min": result["min"], "max": result["max"],
        "unit": spec["unit"],
        "minimum": spec.get("minimum"),
        "maximum": spec.get("maximum"),
    }]
