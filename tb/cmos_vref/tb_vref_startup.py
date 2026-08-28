"""Parser for tb_vref_startup.sch: Vref transient after supply power-up.

Vavdd is a PWL ramp from 0V, flat until t=1us, then rising to nominal
over 100ns (done in t=1.1us) -- RAMP_END_S below must stay in sync with
that schematic's PWL breakpoints. Startup/settling time is measured from
the end of that ramp to the last moment Vref is outside a +-BAND_PCT band
around its own final (end-of-simulation) value -- if the circuit hasn't
actually settled by the end of the tran window, this under-reports the
true settling time rather than flagging it, since there's no ground
truth "final value" beyond what was simulated."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import read_data, in_spec, legend_if_any

RAMP_END_S = 1.1e-6
BAND_PCT = 2.0


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"times": [r[0] for r in rows], "values": [r[-1] for r in rows]}


def evaluate(runs, outputs, plot_base=None):
    """runs: list of {"conditions": {...}, "times": [...], "values": [...]},
    one per corner (temperature is fixed for this test)."""
    spec = outputs[0]
    per_run = [_settling_time_us(r["times"], r["values"]) for r in runs]
    worst = max(per_run)

    if plot_base:
        fig, ax = plt.subplots(figsize=(5, 3.5))
        for run in runs:
            label = _condition_label(run["conditions"])
            times_us = [(t - RAMP_END_S) * 1e6 for t in run["times"]]
            ax.plot(times_us, run["values"], marker="", label=label)
        ax.axvline(0, color="black", linestyle=":", linewidth=1, label="supply settled")
        ax.set_xlabel("Time since supply settled (us)")
        ax.set_ylabel("Vref (V)")
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


def _settling_time_us(times, values):
    v_final = values[-1]
    band = BAND_PCT / 100 * abs(v_final)
    outside = [t for t, v in zip(times, values) if abs(v - v_final) > band]
    settle_t = max(outside) if outside else times[0]
    return (settle_t - RAMP_END_S) * 1e6


def _condition_label(conditions):
    return ",".join(f"{k}={v}" for k, v in conditions.items()) or "default"
