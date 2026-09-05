"""Parser for tb_amp_noise.sch: output-referred voltage noise spectral
density of vo, swept from 'frequency_start' to 'frequency_stop' (.NOISE
analysis, 20 points/decade), output_amp wired as a unity-gain buffer (vn
tied to vo) with vp held at 'amp_vcm' -- same closed-loop config as
tb_amp_psrr.py, same Xyce path as cmos_vref's tb_vref_noise.py (see that
file for why this test runs via Xyce instead of ngspice: ngspice's own
`.noise` bias-point solve fails to converge on this project's self-biased
analog blocks). Column 1 is FREQ (Hz), column 2 is ONOISE (V/sqrt(Hz)),
rescaled to nV/sqrt(Hz) below.

Flicker noise falls with frequency before flattening onto the thermal
floor, so within the swept band the worst (highest) density is always the
value at frequency_start -- same convention as tb_vref_noise.py."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import read_data, in_spec, add_spec_bounds, legend_if_any, typical_min_max

_V_TO_NV = 1e9


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {
        "freqs": [r[0] for r in rows],
        "onoise_nv_rthz": [r[1] * _V_TO_NV for r in rows],
    }


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: list of {"conditions": {...}, "freqs", "onoise_nv_rthz"}, one
    per corner (temperature is fixed for this test). Each run's own worst
    (maximum) noise density seen at any swept frequency feeds
    {typical, min, max} across corners."""
    spec = outputs[0]
    result = typical_min_max(runs, typical, lambda r: max(r["onoise_nv_rthz"]))

    if plot_base:
        _save_plot(runs, spec, plot_base)

    return [{
        "name": spec["description"],
        "typical": result["typical"], "min": result["min"], "max": result["max"],
        "unit": spec["unit"],
        "minimum": spec.get("minimum"),
        "maximum": spec.get("maximum"),
    }]


def _save_plot(runs, spec, plot_base):
    all_values = [v for r in runs for v in r["onoise_nv_rthz"]]
    worst = max(
        ({"value": v, "freq": f, "label": _condition_label(r["conditions"])}
         for r in runs for f, v in zip(r["freqs"], r["onoise_nv_rthz"])),
        key=lambda w: w["value"],
    )

    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    for r in runs:
        label = _condition_label(r["conditions"])
        color = "tab:green" if in_spec(max(r["onoise_nv_rthz"]), spec) else "tab:red"
        ax.loglog(r["freqs"], r["onoise_nv_rthz"], label=label, color=color)

    ax.scatter([worst["freq"]], [worst["value"]], color="black", zorder=5)
    ax.annotate(
        f"worst: {worst['value']:.1f} nV/√Hz @ {worst['freq']:.4g} Hz ({worst['label']})",
        xy=(worst["freq"], worst["value"]), xytext=(0, 8), textcoords="offset points",
        ha="center", fontsize=7,
    )
    add_spec_bounds(ax, all_values, spec, orientation="y")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel(f"{spec['description']} ({spec['unit']})")
    legend_if_any(ax, fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{plot_base}.png", dpi=150)
    plt.close(fig)


def _condition_label(conditions):
    return conditions.get("corner", "default")
