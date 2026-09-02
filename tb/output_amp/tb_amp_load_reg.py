"""Parser for tb_amp_load_reg.sch: vo vs load-current DC sweep, output_amp
wired as a unity-gain buffer (vn tied to vo) with vp held at 'amp_vcm'.

Iload sweeps through zero, both sinking (positive) and sourcing (negative)
current at vo -- deliberately, since the output stage is asymmetric (a
class-A PMOS pull-up, M10, vs. a fixed-current NMOS pull-down, M3), so
regulation is expected to differ between the two directions and both need
covering, not just one.

Sweep amplitude (config.json's "iload": -1.5e-7..2e-6) is deliberately
asymmetric, matching the output stage's own asymmetry (see above): the
source direction (negative iload, current flowing INTO vo from the load)
is absorbed by M3's fixed pull-down mirror, so it's capped well below M3's
mirrored sink current (ibias * m3_width/m1_width, ~250-380nA at nominal
sizing) -- push past that ceiling (as an earlier +-1e-6 symmetric sweep
did) and M3 can't sink the extra current, vo rises, M10 cuts off with
nowhere left for the excess current to go except M10's own drain-bulk
parasitic diode (drain=vo, bulk=vdd), which forward-biases once vo exceeds
vdd+~0.5V -- vo then rails there instead of the loop regulating, swamping
the box-method regulation_pct() with a diode-clamp artifact instead of a
real small-signal number. Confirmed in an earlier
release/doc/output_amp/plots/load_reg__worst.png (ss/-40C/ibias=80n, the
smallest mirrored sink current) before this direction was capped.

The sink direction (positive iload, current flowing OUT of vo to the load)
is answered by M10 sourcing more current as a common-source class-A driver
-- it isn't tied to a fixed mirror ceiling the way M3 is, only to M10's own
sizing/gate drive, so it regulates over a much wider range (out to 2uA
here) before anything similar happens on that side.

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
        typical_run = next(
            (r for r in runs if all(r["conditions"].get(k) == typical.get(k) for k in ("corner", "temperature", "ibias"))),
            None,
        )
        if typical_run:
            _save_plot([typical_run], f"{plot_base}__typical.png")

        worst_run = max(runs, key=lambda r: max(r["values"]) - min(r["values"]))
        _save_plot([worst_run], f"{plot_base}__worst.png")

        _save_plot(runs, f"{plot_base}__all.png", label_key="corner")

    return [{
        "name": spec["description"],
        "typical": result["typical"], "min": result["min"], "max": result["max"],
        "unit": spec["unit"],
        "minimum": spec.get("minimum"),
        "maximum": spec.get("maximum"),
    }]


def _save_plot(runs, path, label_key=None):
    """label_key: group lines by this condition, giving each distinct value
    its own color and exactly one legend entry -- used for __all (label_key
    ="corner") so the legend stays at 3 entries instead of one per
    corner x temperature x ibias combination (up to 27, unreadable). Without
    label_key (__worst, single run) every line gets its own full-condition
    label as before."""
    fig, ax = plt.subplots(figsize=(5, 3.5))
    if label_key:
        keys = sorted({run["conditions"].get(label_key) for run in runs}, key=str)
        colors = {k: c for k, c in zip(keys, plt.cm.tab10.colors)}
        labeled = set()
        for run in runs:
            key = run["conditions"].get(label_key)
            label = f"{label_key}={key}" if key not in labeled else None
            labeled.add(key)
            ax.plot([i * 1e6 for i in run["iloads"]], run["values"], marker="o", markersize=3,
                    label=label, color=colors[key])
    else:
        for run in runs:
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
