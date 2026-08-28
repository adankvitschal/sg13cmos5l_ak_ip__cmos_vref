"""Parser for tb_vref_power.sch: single-point current consumption (.op)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import read_data, in_spec, add_spec_bounds, legend_if_any


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"current_ua": abs(rows[-1][-1]) * 1e6}


def evaluate(runs, outputs, plot_base=None):
    """runs: list of {"conditions": {...}, "current_ua": ...}, one per
    condition (temperature, corner, ...) this test was simulated at.
    Returns a list with one named metric: the worst-case value across all
    conditions."""
    spec = outputs[0]
    values = [r["current_ua"] for r in runs]
    passed = all(in_spec(v, spec) for v in values)

    # a single value doesn't need a chart -- only worth plotting once there's
    # more than one condition to compare against each other.
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

    return [{
        "name": spec["description"],
        "value": _worst_case(values, spec),
        "unit": spec["unit"],
        "minimum": spec.get("minimum"),
        "maximum": spec.get("maximum"),
        "pass": passed,
    }]


def _worst_case(values, spec):
    def violation(v):
        over = v - spec["maximum"] if "maximum" in spec else 0
        under = spec["minimum"] - v if "minimum" in spec else 0
        return max(over, under, 0)
    return max(values, key=lambda v: (violation(v), v))


def _condition_label(conditions):
    return ",".join(f"{k}={v}" for k, v in conditions.items()) or "default"
