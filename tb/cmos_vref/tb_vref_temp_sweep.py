"""Parser for tb_vref_temp_sweep.sch: Vref vs temperature DC sweep.

outputs[0] is the raw Vref value spec (min/max are a sanity range, not a
tight target -- Vref is going to be rescaled later). outputs[1:] are
temperature-coefficient ranges, each a {"description", "unit",
"range": [lo_C, hi_C]} entry -- one metric per range, in ppm/°C (box
method: (Vmax-Vmin)/(V25*ΔT) * 1e6). Every entry's "minimum"/"maximum"
(if present) is handled generically by in_spec(); an entry with neither
key is purely informative (always passes)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import read_data, in_spec, add_spec_bounds, legend_if_any


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"temps": [r[0] for r in rows], "values": [r[-1] for r in rows]}


def evaluate(runs, outputs, plot_base=None):
    """runs: list of {"conditions": {...}, "temps": [...], "values": [...]},
    one per non-temperature condition (corner, ...) this test ran at -- the
    temperature sweep itself is already inside each run's raw data."""
    voltage_spec = outputs[0]
    range_specs = outputs[1:]
    all_values = [v for r in runs for v in r["values"]]

    if plot_base:
        # mixing corners on one plot forces the Y axis to span their full
        # spread, which can flatten the curve shape when corners diverge a
        # lot -- three views instead: the typical corner alone (full detail,
        # no cross-corner scale distortion), the single worst corner alone
        # (biggest peak-to-peak swing across its own sweep), and everything
        # overlaid (today's original single-plot behavior, for the full
        # picture when the scale distortion isn't a problem).
        typical = [r for r in runs if r["conditions"].get("corner") == "tt"]
        if typical:
            _save_plot(typical, voltage_spec, f"{plot_base}__typical.png")

        worst = max(runs, key=lambda r: max(r["values"]) - min(r["values"]))
        _save_plot([worst], voltage_spec, f"{plot_base}__worst.png")

        _save_plot(runs, voltage_spec, f"{plot_base}__all.png")

    typical_run = next((r for r in runs if r["conditions"].get("corner") == "tt"), None)
    typical_value = None
    if typical_run and typical_run["temps"]:
        ref_idx = min(range(len(typical_run["temps"])), key=lambda i: abs(typical_run["temps"][i] - 25))
        typical_value = typical_run["values"][ref_idx]

    metrics = [
        {
            "name": f"{voltage_spec['description']} (min)",
            "value": min(all_values),
            "unit": voltage_spec["unit"],
            "minimum": voltage_spec.get("minimum"),
            "maximum": voltage_spec.get("maximum"),
            "pass": all(in_spec(v, voltage_spec) for v in all_values),
        },
        {
            "name": f"{voltage_spec['description']} (max)",
            "value": max(all_values),
            "unit": voltage_spec["unit"],
            "minimum": voltage_spec.get("minimum"),
            "maximum": voltage_spec.get("maximum"),
            "pass": all(in_spec(v, voltage_spec) for v in all_values),
        },
        {
            # tt corner, closest sampled point to 25C -- the single "typical"
            # reading cross-block consumers (e.g. top's own rbot_nominal,
            # params/top/default.json) key off of, since (min)/(max) above are
            # a range across the WHOLE temp/corner sweep, not one design point.
            "name": f"{voltage_spec['description']} (typ)",
            "value": typical_value,
            "unit": voltage_spec["unit"],
            "minimum": voltage_spec.get("minimum"),
            "maximum": voltage_spec.get("maximum"),
            "pass": in_spec(typical_value, voltage_spec) if typical_value is not None else True,
        },
    ]

    for spec in range_specs:
        lo, hi = spec["range"]
        per_run = [_temp_coeff_ppm(r["temps"], r["values"], lo, hi) for r in runs]
        per_run = [v for v in per_run if v is not None]
        worst = max(per_run) if per_run else None
        metrics.append({
            "name": spec["description"],
            "value": worst,
            "unit": spec.get("unit", "ppm/°C"),
            "minimum": spec.get("minimum"),
            "maximum": spec.get("maximum"),
            "pass": in_spec(worst, spec) if worst is not None else True,
        })

    return metrics


def _save_plot(runs, voltage_spec, path):
    fig, ax = plt.subplots(figsize=(5, 3.5))
    values = [v for r in runs for v in r["values"]]
    for run in runs:
        label = _condition_label(run["conditions"])
        ax.plot(run["temps"], run["values"], marker="o", markersize=3, label=label)
    add_spec_bounds(ax, values, voltage_spec, orientation="y")
    ax.set_xlabel("Temperature (C)")
    ax.set_ylabel(f"{voltage_spec['description']} ({voltage_spec['unit']})")
    legend_if_any(ax, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _temp_coeff_ppm(temps, values, lo, hi):
    """Worst-case box-method temperature coefficient within [lo, hi] C,
    normalized to this same run's value at (closest to) 25C -- the
    room-temperature reading is the natural reference point for "how much
    does Vref drift from its nominal value over this range". None if the
    run has no points in range."""
    in_range = [v for t, v in zip(temps, values) if lo <= t <= hi]
    if not in_range:
        return None
    ref_idx = min(range(len(temps)), key=lambda i: abs(temps[i] - 25))
    v25 = values[ref_idx]
    return (max(in_range) - min(in_range)) / (v25 * (hi - lo)) * 1e6


def _condition_label(conditions):
    return ",".join(f"{k}={v}" for k, v in conditions.items()) or "default"
