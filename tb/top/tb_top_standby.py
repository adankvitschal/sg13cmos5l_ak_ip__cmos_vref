"""Parser for tb_top_power.sch reused with 'ena' forced HIGH (disabled/
standby) via this test's own conditions.ena override -- config.json's
defaults.ena="0" (enabled, active-low per the datasheet) is what every
OTHER top test uses instead. Unlike tb_top_power.py (which sums the
analog+digital columns into one total), this reports the ANALOG (avdd)
rail alone: the digital (dvdd) rail only ever feeds the enable/trim glue
logic's own static buffers (sg13cmos5l_buf_1, an LV-domain stdcell run at the
HV dvdd level to fully gate the HV switches they drive), whose leakage
swamps the analog core's own standby draw (~2.4nA vs ~0.35nA measured at
tt/25C) and isn't something choosing a different cmos_vref/output_amp
sub-block variation can affect. Working assumption -- not confirmed against
ihp_mh_ip__cmos_vref_proposal.pdf's own Table 2, which wasn't available to
check -- is that the datasheet's 750pA standby spec targets the analog
reference core alone, not this glue logic's own budget; revisit this split
if that turns out wrong."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import read_data, in_spec, add_spec_bounds, legend_if_any, typical_min_max


def extract(data_path):
    """Raw reduction of one simulation run's .data file: columns are
    [scale, analog(avdd) current, digital(dvdd) current] -- see this
    module's own docstring for why only the analog column is read here."""
    rows = read_data(data_path)
    _, ana_i, _dig_i = rows[-1]
    return {"current_pa": abs(ana_i) * 1e12}


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
