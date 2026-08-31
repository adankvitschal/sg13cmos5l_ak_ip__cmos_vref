"""Parser for tb_top_temp_sweep.sch: vbg vs temperature DC sweep -- same
box-method temperature-coefficient convention as cmos_vref's own
tb_vref_temp_sweep.py, measured at "top"'s own regulated bandgap output
(vbg) instead of cmos_vref's raw vref.

outputs[0] is the raw vbg value spec (min/max are a sanity range, not a
tight target). outputs[1:] are temperature-coefficient ranges, each a
{"description", "unit", "range": [lo_C, hi_C]} entry -- one metric per
range, in ppm/°C (box method: (Vmax-Vmin)/(V_typ*ΔT) * 1e6). Every entry's
"minimum"/"maximum" (if present) is handled generically by range_pass();
an entry with neither key is purely informative (always passes).

Temperature is swept INTERNALLY within each run (one run per corner), so
"typical" here means "the sample closest to conditions.typical.temperature,
within the conditions.typical.corner run" -- see cmos_vref's own
tb_vref_temp_sweep.py for the identical convention this mirrors."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import add_spec_bounds, legend_if_any, range_pass, read_data, value_at


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"temps": [r[0] for r in rows], "values": [r[-1] for r in rows]}


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: list of {"conditions": {...}, "temps": [...], "values": [...]},
    one per non-temperature condition (corner, ...) this test ran at -- the
    temperature sweep itself is already inside each run's raw data."""
    voltage_spec = outputs[0]
    range_specs = outputs[1:]
    all_values = [v for r in runs for v in r["values"]]
    ref_temp = float(typical["temperature"])

    if plot_base:
        typical_runs = [r for r in runs if r["conditions"].get("corner") == typical["corner"]]
        if typical_runs:
            _save_plot(typical_runs, voltage_spec, f"{plot_base}__typical.png")

        worst = max(runs, key=lambda r: max(r["values"]) - min(r["values"]))
        _save_plot([worst], voltage_spec, f"{plot_base}__worst.png")

        _save_plot(runs, voltage_spec, f"{plot_base}__all.png")

    typical_run = next((r for r in runs if r["conditions"].get("corner") == typical["corner"]), None)
    typical_value = value_at(typical_run["temps"], typical_run["values"], ref_temp) if typical_run and typical_run["temps"] else None
    voltage_result = {"typical": typical_value, "min": min(all_values), "max": max(all_values)}

    metrics = [{
        "name": voltage_spec["description"],
        "typical": voltage_result["typical"], "min": voltage_result["min"], "max": voltage_result["max"],
        "unit": voltage_spec["unit"],
        "minimum": voltage_spec.get("minimum"),
        "maximum": voltage_spec.get("maximum"),
        "pass": range_pass(voltage_result, voltage_spec),
    }]

    for spec in range_specs:
        lo, hi = spec["range"]
        per_run = [v for v in (_temp_coeff_ppm(r["temps"], r["values"], lo, hi, ref_temp) for r in runs) if v is not None]
        typical_coeff = (
            _temp_coeff_ppm(typical_run["temps"], typical_run["values"], lo, hi, ref_temp)
            if typical_run else None
        )
        coeff_result = {
            "typical": typical_coeff,
            "min": min(per_run) if per_run else None,
            "max": max(per_run) if per_run else None,
        }
        metrics.append({
            "name": spec["description"],
            "typical": coeff_result["typical"], "min": coeff_result["min"], "max": coeff_result["max"],
            "unit": spec.get("unit", "ppm/°C"),
            "minimum": spec.get("minimum"),
            "maximum": spec.get("maximum"),
            "pass": range_pass(coeff_result, spec) if per_run else True,
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


def _temp_coeff_ppm(temps, values, lo, hi, ref_temp):
    """Worst-case box-method temperature coefficient within [lo, hi] C,
    normalized to this same run's value at (closest to) ref_temp."""
    in_range = [v for t, v in zip(temps, values) if lo <= t <= hi]
    if not in_range:
        return None
    v_ref = value_at(temps, values, ref_temp)
    return (max(in_range) - min(in_range)) / (v_ref * (hi - lo)) * 1e6


def _condition_label(conditions):
    return ",".join(f"{k}={v}" for k, v in conditions.items()) or "default"
