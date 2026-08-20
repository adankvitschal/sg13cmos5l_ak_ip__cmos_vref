"""Parser for tb_amp_psrr.sch: PSRR at a single frequency (.ac analysis),
output_amp wired as a unity-gain buffer (vn tied to vo) with vp held at
'amp_vcm' -- same single-point convention as cmos_vref's own psrr test
(tb/cmos_vref/tb_vref_psrr.py).

Vdd carries a 1V AC small-signal stimulus on top of its DC bias, so a
single-point .ac analysis' vdb(vo) is directly the small-signal gain from
supply ripple to vo, in dB. PSRR (rejection, higher is better) is the
negative of that gain."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from _common import read_data, in_spec, add_spec_bounds, legend_if_any


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"psrr_db": -rows[-1][-1]}


def evaluate(runs, outputs, plot_base=None):
    """runs: list of {"conditions": {...}, "psrr_db": ...}, one per corner
    (frequency and temperature are fixed for this test)."""
    spec = outputs[0]
    values = [r["psrr_db"] for r in runs]
    worst = min(values)

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
        "value": worst,
        "unit": spec["unit"],
        "minimum": spec.get("minimum"),
        "maximum": spec.get("maximum"),
        "pass": in_spec(worst, spec),
    }]


def _condition_label(conditions):
    return ",".join(f"{k}={v}" for k, v in conditions.items()) or "default"
