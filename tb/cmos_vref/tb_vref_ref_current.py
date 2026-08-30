"""Parser for tb_vref_ref_current.sch: single-point (.op) core reference
current -- v.x1.vm_b1#branch, the ammeter already wired in series with
M3's source (sch/cmos_vref/cmos_vref_default.sch, between vdd and M3's own
source net #net1). Note the ngspice vector name for a branch current
through a hierarchical subcircuit instance is "v.<instance>.<source>#branch",
NOT the "i(<instance>.<source>)" form that works for a top-level element --
confirmed empirically (the latter raises "no such function as i"). This is
the exact current top's own M1 bias mirror is sized against (see
params/top/default.json's cross_block "scale_to_target" derivation of
amp_bias_width) -- the "current_na" key this extract() returns is a
load-bearing contract read by analog_designer.sim.run_sim's
resolve_cross_block_metrics(), not just a display value.

No absolute target here: cmos_vref alone has no "correct" bias current --
m3_width (0.30u-100u range) is a free parameter tuned for cmos_vref's OWN
specs (Vref, TC, consumption -- see config.json blocks.cmos_vref.profiles),
completely independent of what output_amp happens to need."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import read_data, in_spec, add_spec_bounds, legend_if_any


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"current_na": abs(rows[-1][-1]) * 1e9}


def evaluate(runs, outputs, plot_base=None):
    """runs: list of {"conditions": {...}, "current_na": ...}, one per
    condition (temperature, corner, ...) this test was simulated at.
    Reports the NOMINAL (corner=tt, temperature=25) value, not a worst-case
    across PVT -- unlike every other parser in this project, this metric's
    "value" is read back by resolve_cross_block_metrics() as a sizing
    reference for top's amp_bias_width, and a single fixed width can only
    be calibrated against one condition. tt/25 matches the flat (no
    corner/temperature dependence) 100nA design point output_amp's own
    standalone testbenches use. Corner/temperature variation of the actual
    delivered current is still observable -- see tb/top's own
    amp_bias_current test, swept across the same PVT grid."""
    spec = outputs[0]
    values = [r["current_na"] for r in runs]
    passed = all(in_spec(v, spec) for v in values)

    if plot_base and len(runs) > 1:
        labels = [_condition_label(r["conditions"]) for r in runs]
        colors = ["tab:green" if in_spec(v, spec) else "tab:red" for v in values]
        fig, ax = plt.subplots(figsize=(max(4, len(runs) * 0.6), 3))
        ax.bar(labels, values, color=colors)
        add_spec_bounds(ax, values, spec, orientation="y")
        ax.set_ylabel(f"{spec['description']} ({spec['unit']})")
        ax.tick_params(axis="x", rotation=45)
        legend_if_any(ax, fontsize=8)
        fig.tight_layout()
        fig.savefig(f"{plot_base}.png", dpi=150)
        plt.close(fig)

    nominal = next(
        (r["current_na"] for r in runs
         if r["conditions"].get("corner") == "tt" and r["conditions"].get("temperature") == "25"),
        None,
    )
    if nominal is None:
        raise ValueError(
            "reference_current: no corner=tt/temperature=25 condition among "
            "this test's runs -- needed as the nominal sizing reference for "
            "top's amp_bias_width cross_block derivation"
        )

    return [{
        "name": spec["description"],
        "value": nominal,
        "unit": spec["unit"],
        "minimum": spec.get("minimum"),
        "maximum": spec.get("maximum"),
        "pass": passed,
    }]


def _condition_label(conditions):
    return ",".join(f"{k}={v}" for k, v in conditions.items()) or "default"
