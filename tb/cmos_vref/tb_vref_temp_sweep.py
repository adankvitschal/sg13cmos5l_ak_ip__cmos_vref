"""Parser for tb_vref_temp_sweep.sch: Vref vs temperature DC sweep."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from _common import read_data, in_spec, add_spec_bounds, legend_if_any


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"temps": [r[0] for r in rows], "values": [r[-1] for r in rows]}


def evaluate(runs, outputs, plot_path=None):
    """runs: list of {"conditions": {...}, "temps": [...], "values": [...]},
    one per non-temperature condition (corner, ...) this test ran at -- the
    temperature sweep itself is already inside each run's raw data."""
    spec = outputs[0]
    all_values = [v for r in runs for v in r["values"]]
    passed = all(in_spec(v, spec) for v in all_values)

    if plot_path:
        fig, ax = plt.subplots(figsize=(5, 3.5))
        for run in runs:
            label = _condition_label(run["conditions"])
            ax.plot(run["temps"], run["values"], marker="o", markersize=3, label=label)
        add_spec_bounds(ax, all_values, spec, orientation="y")
        ax.set_xlabel("Temperature (C)")
        ax.set_ylabel(f"{spec['description']} ({spec['unit']})")
        legend_if_any(ax, fontsize=8)
        fig.tight_layout()
        fig.savefig(plot_path, dpi=150)
        plt.close(fig)

    return [
        {
            "name": f"{spec['description']} (min)",
            "value": min(all_values),
            "unit": spec["unit"],
            "minimum": spec.get("minimum"),
            "maximum": spec.get("maximum"),
            "pass": passed,
        },
        {
            "name": f"{spec['description']} (max)",
            "value": max(all_values),
            "unit": spec["unit"],
            "minimum": spec.get("minimum"),
            "maximum": spec.get("maximum"),
            "pass": passed,
        },
    ]


def _condition_label(conditions):
    return ",".join(f"{k}={v}" for k, v in conditions.items()) or "default"
