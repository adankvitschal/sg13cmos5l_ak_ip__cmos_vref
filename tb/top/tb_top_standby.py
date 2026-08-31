"""Parser for tb_top_power.sch reused with 'ena' forced HIGH (disabled/
standby) via this test's own conditions.ena override -- config.json's
defaults.ena="0" (enabled, active-low per the datasheet) is what every
OTHER top test uses instead. Reports the same total supply current
tb_top_power.py does, just scaled to pA instead of uA -- this current is
expected to be sub-nA, per the datasheet's own 750pA standby-current
spec."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import read_data, in_spec, add_spec_bounds, legend_if_any, typical_min_max


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"current_pa": abs(rows[-1][-1]) * 1e12}


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: list of {"conditions": {...}, "current_pa": ...}, one per
    condition (temperature, corner, ...) this test was simulated at.
    Returns one named metric: {typical, min, max} across all conditions."""
    spec = outputs[0]
    result = typical_min_max(runs, typical, lambda r: r["current_pa"])

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
    standby-current reading, temperature is secondary spread within each
    corner. Each column spans that corner's own min-max across its swept
    temperatures (an errorbar, not a bar -- there's no meaningful "zero"
    baseline for a min/max range), red/green by whether the WHOLE range
    stays in spec, with the typical-temperature reading marked as a
    distinct black dot so the nominal point is still visible against the
    worst-case spread around it."""
    corners = list(dict.fromkeys(r["conditions"].get("corner") for r in runs))
    fig, ax = plt.subplots(figsize=(max(3, len(corners) * 1.2), 3.5))
    for i, corner in enumerate(corners):
        corner_runs = [r for r in runs if r["conditions"].get("corner") == corner]
        values = [r["current_pa"] for r in corner_runs]
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
            ax.scatter([i], [typical_run["current_pa"]], color="black", zorder=3, label=label)
    ax.set_xticks(range(len(corners)))
    ax.set_xticklabels(corners)
    ax.set_xlim(-0.5, len(corners) - 0.5)
    add_spec_bounds(ax, [r["current_pa"] for r in runs], spec, orientation="y")
    ax.set_xlabel("corner")
    ax.set_ylabel(f"{spec['description']} ({spec['unit']})")
    legend_if_any(ax, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
