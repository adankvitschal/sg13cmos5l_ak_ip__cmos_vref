"""Parser for tb_vref_load_reg.sch: Vref vs load-current DC sweep.

The load here is an ideal current sink pulling from the vref node -- a
stand-in for a downstream buffer's input bias current, not a real driven
load (the core is never expected to source real load current; a
downstream opamp buffer with high input impedance does that job). Swept
in the nA range, matching the order of magnitude of a subthreshold
buffer's input bias current.

Load regulation = (Vref_max - Vref_min) / |Vref_nom|, where Vref_nom is the
midpoint of the Vref values seen across the sweep -- same box-method
convention as the sky130_ak_ip__cmos_vref load_reg testbench this was
ported from (`vref_nom = (max+min)/2`), plus an abs() on Vref_nom so a
badly-broken reference (Vref swinging through zero across the sweep) can't
sign-flip the result into a misleadingly small-looking negative percentage --
see _common.regulation_pct()."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import read_data, legend_if_any, regulation_pct, typical_min_max


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"iloads": [r[0] for r in rows], "values": [r[-1] for r in rows]}


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: list of {"conditions": {...}, "iloads": [...], "values": [...]},
    one per non-iload condition (corner, temperature, ...) this test ran at
    -- the load sweep itself is already inside each run's raw data."""
    spec = outputs[0]
    result = typical_min_max(runs, typical, lambda r: regulation_pct(r["values"]))

    if plot_base:
        # overlaying every corner x temperature combination gets cluttered
        # fast -- the typical corner (all its temperatures) keeps the curve
        # readable, worst singles out the single condition with the biggest
        # swing, all keeps the full picture available.
        typical_runs = [r for r in runs if r["conditions"].get("corner") == typical["corner"]]
        if typical_runs:
            # corner is constant across every line here -- drop it from the
            # legend so only the actually-varying condition (temperature) shows
            _save_plot(typical_runs, f"{plot_base}__typical.png", label_key="temperature")

        worst_run = max(runs, key=lambda r: max(r["values"]) - min(r["values"]))
        _save_plot([worst_run], f"{plot_base}__worst.png")

        _save_plot(runs, f"{plot_base}__all.png")

    return [{
        "name": spec["description"],
        "typical": result["typical"], "min": result["min"], "max": result["max"],
        "unit": spec["unit"],
        "minimum": spec.get("minimum"),
        "maximum": spec.get("maximum"),
    }]


def _save_plot(runs, path, label_key=None):
    """label_key: if given, only that one condition varies across `runs`
    (the caller already filtered on everything else), so the legend shows
    just that key instead of every condition -- avoids repeating a
    constant like "corner=tt" on every line."""
    fig, ax = plt.subplots(figsize=(5, 3.5))
    for run in runs:
        if label_key:
            label = f"{label_key}={run['conditions'].get(label_key)}"
        else:
            label = _condition_label(run["conditions"])
        ax.plot([i * 1e9 for i in run["iloads"]], run["values"], marker="o", markersize=3, label=label)
    ax.set_xlabel("Load Current (nA)")
    ax.set_ylabel("Vref (V)")
    legend_if_any(ax, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _condition_label(conditions):
    return ",".join(f"{k}={v}" for k, v in conditions.items()) or "default"
