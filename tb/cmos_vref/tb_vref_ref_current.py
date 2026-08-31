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

from parser_common import read_data, in_spec, add_spec_bounds, legend_if_any, typical_min_max


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"current_na": abs(rows[-1][-1]) * 1e9}


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: list of {"conditions": {...}, "current_na": ...}, one per
    condition (temperature, corner, ...) this test was simulated at.
    Reports {typical, min, max} like every other parser -- the TYPICAL
    (corner/temperature per conditions.typical, "tt"/"25" here) value is
    what resolve_cross_block_metrics() reads (scale_to_target's own
    "stat": "typical") as a sizing reference for top's amp_bias_width, a
    single fixed width that can only be calibrated against one condition.
    tt/25 matches the flat (no corner/temperature dependence) 100nA design
    point output_amp's own standalone testbenches use; min/max are still
    reported for visibility even though nothing consumes them here.
    Corner/temperature variation of the actual delivered current is still
    observable -- see tb/top's own amp_bias_current test, swept across the
    same PVT grid."""
    spec = outputs[0]
    result = typical_min_max(runs, typical, lambda r: r["current_na"])

    if plot_base and len(runs) > 1:
        _save_plot(runs, spec, typical, f"{plot_base}.png")

    return [{
        "name": spec["description"],
        "typical": result["typical"], "min": result["min"], "max": result["max"],
        "unit": spec["unit"],
        "minimum": spec.get("minimum"),
        "maximum": spec.get("maximum"),
    }]


def _save_plot(runs, spec, typical, path):
    """One column per CORNER (not temperature) -- temperature dependence
    already has its own dedicated view (temp_sweep), so here it would just
    be a distraction: process corner is what actually drives a worst-case
    reading, temperature is secondary spread within each corner. Each
    column spans that corner's own min-max across its swept temperatures
    (an errorbar, not a bar -- there's no meaningful "zero" baseline for a
    min/max range), red/green by whether the WHOLE range stays in spec,
    with the typical-temperature reading marked as a distinct black dot so
    the nominal point is still visible against the worst-case spread
    around it."""
    corners = list(dict.fromkeys(r["conditions"].get("corner") for r in runs))
    fig, ax = plt.subplots(figsize=(max(3, len(corners) * 1.2), 3.5))
    for i, corner in enumerate(corners):
        corner_runs = [r for r in runs if r["conditions"].get("corner") == corner]
        values = [r["current_na"] for r in corner_runs]
        lo, hi = min(values), max(values)
        mid = (lo + hi) / 2
        color = "tab:green" if in_spec(lo, spec) and in_spec(hi, spec) else "tab:red"
        ax.errorbar(
            [i], [mid], yerr=[[mid - lo], [hi - mid]],
            fmt="none", ecolor=color, elinewidth=3, capsize=6, zorder=2,
        )
        typical_run = next((r for r in corner_runs if r["conditions"].get("temperature") == typical.get("temperature")), None)
        if typical_run:
            label = f"{typical['temperature']}°C" if i == 0 else None
            ax.scatter([i], [typical_run["current_na"]], color="black", zorder=3, label=label)
    ax.set_xticks(range(len(corners)))
    ax.set_xticklabels(corners)
    ax.set_xlim(-0.5, len(corners) - 0.5)
    add_spec_bounds(ax, [r["current_na"] for r in runs], spec, orientation="y")
    ax.set_xlabel("corner")
    ax.set_ylabel(f"{spec['description']} ({spec['unit']})")
    legend_if_any(ax, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
