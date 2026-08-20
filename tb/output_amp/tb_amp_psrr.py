"""Parser for tb_amp_psrr.sch: PSRR vs frequency, output_amp wired as a
unity-gain buffer (vn tied to vo) with vp held at 'amp_vcm'.

Vdd carries a 1V AC small-signal stimulus on top of its DC bias, so
vdb(vo) at each swept frequency is directly the small-signal gain from
supply ripple to vo, in dB. PSRR (rejection, higher is better) is the
negative of that gain. Swept (not single-point like cmos_vref's psrr
test) because a DC buffer's whole job is to keep PSRR good even though
its bandwidth is intentionally low -- the interesting question is where
PSRR starts degrading, not just its value at one frequency."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from _common import read_data, in_spec, legend_if_any


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {
        "freqs": [r[0] for r in rows],
        "psrr_db": [-r[1] for r in rows],
    }


def evaluate(runs, outputs, plot_base=None):
    """runs: list of {"conditions": {...}, "freqs": [...], "psrr_db": [...]},
    one per corner/temperature. Reported metric is the worst-case (minimum)
    PSRR across every swept frequency and every condition."""
    spec = outputs[0]
    per_run_worst = [min(r["psrr_db"]) for r in runs]
    worst = min(per_run_worst)

    if plot_base:
        fig, ax = plt.subplots(figsize=(5, 3.5))
        for run in runs:
            ax.semilogx(run["freqs"], run["psrr_db"], label=_condition_label(run["conditions"]))
        if "minimum" in spec:
            ax.axhline(spec["minimum"], color="black", linestyle="--", linewidth=1, label="minimum")
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel(f"{spec['description']} ({spec['unit']})")
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
