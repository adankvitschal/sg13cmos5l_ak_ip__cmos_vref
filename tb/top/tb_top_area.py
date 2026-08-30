"""Parser for the area test: a static W*L*ng*m sum over top's sized
devices (across cmos_vref, output_amp, and top's own M1/M2/R1-R8/M6-M9)
in an xschem-expanded netlist -- no simulation involved (see config.json's
"simulator": "netlist" for this test). Reuses tb_top_power.sch purely as a
cheap vehicle to get xschem to expand the DUT's devices; the .op analysis
inside it never actually runs for this test."""
from parser_common import estimate_area_um2, in_spec

# Same factor as cmos_vref's/output_amp's own area tests, for comparability.
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
