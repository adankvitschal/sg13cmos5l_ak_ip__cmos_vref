"""Parser for tb_top_amp_bias.sch: single-point (.op) real bias current
delivered to output_amp's ibias pin once cmos_vref (X1) and output_amp
(x2) are composed together inside top -- v.x1.vm_b3#branch, the ammeter
already wired in sch/top/top_default.sch in series with M1's source
(originally tagged lvs_ignore=short, placed for LVS purposes, never read
by any parser before this test). The ngspice vector name for a branch
current through a hierarchical subcircuit instance is
"v.<instance>.<source>#branch", not "i(<instance>.<source>)" (confirmed
empirically -- the latter raises "no such function as i"). Compares this
real, mirror-derived current against the
100nA output_amp was actually designed/verified against standalone (see
config.json defaults.ibias and tb/output_amp's own testbenches).

params/top/default.json's amp_bias_width is computed automatically
(cross_block "scale_to_target") from cmos_vref's own measured
reference_current test, but that's a single-shot, open-loop estimate, NOT
a guarantee -- KNOWN LIMITATION, measured on the default parameter set:
cmos_vref's reference_current test measures M3 on a clean, directly-set
1.8V supply, while inside top the same core is fed through the M2
enable-switch PMOS (a several-tens-of-mV drop); combined with this mirror
apparently running in weak/moderate inversion (VSG close to Vth), that
supply difference alone was observed to cause roughly a 3x mismatch
between the calculated target and what this test actually measures at the
nominal corner/temperature -- this test is expected to FAIL until that gap
is closed by hand (e.g. tuning `target` in params/top/default.json against
this test's own result) or the calibration environment is improved. This
test is the ground truth for that gap; don't assume amp_bias_width's
calculation is exact just because it's automatic."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import read_data, in_spec, add_spec_bounds, legend_if_any, typical_min_max, range_pass


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"current_na": abs(rows[-1][-1]) * 1e9}


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: list of {"conditions": {...}, "current_na": ...}, one per
    condition (temperature, corner, ...) this test was simulated at.
    Returns one named metric: {typical, min, max} across all conditions."""
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
        "pass": range_pass(result, spec),
    }]


def _save_plot(runs, spec, typical, path):
    """One column per CORNER (not temperature) -- temperature dependence
    already has its own dedicated view (temp_sweep), so here it would just
    be a distraction: process corner is what actually drives a worst-case
    bias-current reading, temperature is secondary spread within each
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
