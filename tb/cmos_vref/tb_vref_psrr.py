"""Parser for tb_vref_psrr.sch: PSRR swept from 'frequency_start' to
'frequency_stop' (.ac analysis, 20 points/decade, both edges set by
conditions.frequency_start/frequency_stop in config.json).

Vavdd carries a 1V AC small-signal stimulus on top of its DC bias, so
vdb(vref) at each swept frequency is directly the small-signal gain from
supply ripple to Vref, in dB. PSRR (rejection, higher is better) is the
negative of that gain. The reported spec value is the single worst-case
PSRR across the whole swept band, since a supply rejection spec needs to
hold everywhere in-band, not just at the band's upper edge."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import read_data, in_spec, add_spec_bounds, legend_if_any, typical_min_max, range_pass


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {
        "freqs": [r[0] for r in rows],
        "psrr_db": [-r[1] for r in rows],
    }


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: list of {"conditions": {...}, "freqs", "psrr_db"}, one per
    corner (temperature is fixed for this test). Each run's own worst
    (minimum) PSRR seen at any swept frequency feeds {typical, min, max}
    across corners -- min is the worst PSRR seen anywhere, matching a
    supply-rejection spec that needs to hold everywhere in-band."""
    spec = outputs[0]
    result = typical_min_max(runs, typical, lambda r: min(r["psrr_db"]))

    if plot_base:
        _save_plot(runs, spec, plot_base)

    return [{
        "name": spec["description"],
        "typical": result["typical"], "min": result["min"], "max": result["max"],
        "unit": spec["unit"],
        "minimum": spec.get("minimum"),
        "maximum": spec.get("maximum"),
        "pass": range_pass(result, spec),
    }]


def _save_plot(runs, spec, plot_base):
    all_values = [v for r in runs for v in r["psrr_db"]]
    worst = min(
        ({"value": v, "freq": f, "label": _condition_label(r["conditions"])}
         for r in runs for f, v in zip(r["freqs"], r["psrr_db"])),
        key=lambda w: w["value"],
    )

    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    for r in runs:
        label = _condition_label(r["conditions"])
        color = "tab:green" if in_spec(min(r["psrr_db"]), spec) else "tab:red"
        ax.semilogx(r["freqs"], r["psrr_db"], label=label, color=color)

    ax.scatter([worst["freq"]], [worst["value"]], color="black", zorder=5)
    ax.annotate(
        f"worst: {worst['value']:.1f} dB @ {worst['freq']:.0f} Hz ({worst['label']})",
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
    return ",".join(f"{k}={v}" for k, v in conditions.items()) or "default"
