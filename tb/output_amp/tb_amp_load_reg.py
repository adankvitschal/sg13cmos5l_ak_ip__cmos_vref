"""Parser for tb_amp_load_reg.sch: vo vs load-current DC sweep, output_amp
wired as a unity-gain buffer (vn tied to vo) with vp held at 'amp_vcm'.

Iload sweeps through zero, both sinking (positive) and sourcing (negative)
current at vo -- deliberately, since the output stage is asymmetric (a
class-A PMOS pull-up, M10, vs. a fixed-current NMOS pull-down, M3), so
regulation is expected to differ between the two directions and both need
covering, not just one.

Load regulation = (vo_max - vo_min) / |vo_nom|, vo_nom = midpoint of the
values seen across the sweep -- same box-method convention as
cmos_vref's load_reg test, see _common.regulation_pct()."""
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
    one per non-iload condition (corner, temperature, ...) -- the load
    sweep itself is already inside each run's raw data."""
    spec = outputs[0]
    result = typical_min_max(runs, typical, lambda r: regulation_pct(r["values"]), match_keys=("corner", "temperature", "ibias"))

    if plot_base:
        typical_runs = [r for r in runs if r["conditions"].get("corner") == typical["corner"]]
        if typical_runs:
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
    fig, ax = plt.subplots(figsize=(5, 3.5))
    for run in runs:
        if label_key:
            label = f"{label_key}={run['conditions'].get(label_key)}"
        else:
            label = _condition_label(run["conditions"])
        ax.plot([i * 1e6 for i in run["iloads"]], run["values"], marker="o", markersize=3, label=label)
    ax.axvline(0, color="black", linestyle=":", linewidth=1)
    ax.set_xlabel("Load Current (uA, +sink/-source)")
    ax.set_ylabel("Vo (V)")
    legend_if_any(ax, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _condition_label(conditions):
    return ",".join(f"{k}={v}" for k, v in conditions.items()) or "default"
