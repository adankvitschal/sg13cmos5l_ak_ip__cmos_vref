"""Parser for tb_vref_startup.sch: Vref transient after supply power-up,
compared across different Vavdd enable ramp times (config.json's own
conditions.ramp_time list), to check whether a fast power-up spikes Vref
(and, by extension, the 1.2V-rated LV M1/M2 in the lvfet topology) before
the startup circuit brings the reference into regulation.

Vavdd is a PWL ramp from 0V at t=0, rising to nominal over 'ramp_time'
(schematic: PWL(0 0 'ramp_time' 'Vavdd') -- no braces/arithmetic in the
schematic's value= string, xschem uses {} itself for property-block
nesting and mangles anything with literal braces inside a quoted value).

Settling time, peak voltage and overshoot are each reported as ONE
typical/min/max metric pooled across every condition (corner AND
ramp_time together, see match_keys below) -- same shape as every other
test's metrics, rather than one triple per ramp_time -- and every run
(every corner x ramp_time combination) is drawn on one shared plot rather
than split into one panel per ramp_time. "typical" is whichever single
(corner, temperature, ramp_time) point config.json's conditions.typical
names (see typical_min_max()'s match_keys); everything else just widens
the reported min/max range."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import read_data, legend_if_any, typical_min_max, si_to_float

BAND_PCT = 2.0
MATCH_KEYS = ("corner", "temperature", "ramp_time")


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"times": [r[0] for r in rows], "values": [r[-1] for r in rows]}


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: list of {"conditions": {...}, "times": [...], "values": [...]},
    one per (corner, ramp_time) combination -- temperature is fixed for this
    test."""
    settling_spec, peak_spec, overshoot_spec = outputs

    settling = typical_min_max(runs, typical, _settling_time_us, match_keys=MATCH_KEYS)
    peak = typical_min_max(runs, typical, lambda r: max(r["values"]), match_keys=MATCH_KEYS)
    overshoot = typical_min_max(runs, typical, _overshoot_pct, match_keys=MATCH_KEYS)

    metrics = []
    for spec, result in ((settling_spec, settling), (peak_spec, peak), (overshoot_spec, overshoot)):
        metrics.append({
            "name": spec["description"],
            "typical": result["typical"], "min": result["min"], "max": result["max"],
            "unit": spec["unit"],
            "minimum": spec.get("minimum"),
            "maximum": spec.get("maximum"),
        })

    if plot_base:
        fig, ax = plt.subplots(figsize=(6, 4))
        for run in runs:
            times_us = [t * 1e6 for t in run["times"]]
            ax.plot(times_us, run["values"], marker="", label=_condition_label(run["conditions"]))
        ax.set_xlabel("Time (us)")
        ax.set_ylabel("Vref (V)")
        # Cropped to the slowest run's own settling point (+20% margin) --
        # the .tran window (Tstop) is sized for the worst spec bound this
        # metric feeds (low_power's own 1000us max, +50% margin), which is
        # far more than most runs actually need to visibly settle in; a
        # full-window plot would mostly just be flat tail past this point.
        # ax.plot() above already drew the complete data -- this only
        # narrows the VIEW, nothing is dropped from what was measured.
        settle_ends_us = [
            si_to_float(run["conditions"]["ramp_time"]) * 1e6 + _settling_time_us(run)
            for run in runs
        ]
        if settle_ends_us:
            ax.set_xlim(0, max(1.0, max(settle_ends_us) * 1.2))
        legend_if_any(ax, fontsize=8)
        fig.tight_layout()
        fig.savefig(f"{plot_base}.png", dpi=150)
        plt.close(fig)

    return metrics


def _settling_time_us(run):
    """Time from the end of the Vavdd ramp until Vref last strayed outside
    its +-BAND_PCT band -- clamped at 0 rather than going negative, since a
    slow enough ramp (ramp_time comparable to or longer than the circuit's
    own response) lets Vref settle into that band before the ramp itself
    even finishes, which is a fine outcome ("already settled by power-up"),
    not an error condition to report as negative time."""
    times, values = run["times"], run["values"]
    ramp_end_s = si_to_float(run["conditions"]["ramp_time"])
    v_final = values[-1]
    band = BAND_PCT / 100 * abs(v_final)
    outside = [t for t, v in zip(times, values) if abs(v - v_final) > band]
    settle_t = max(outside) if outside else times[0]
    return max(0.0, (settle_t - ramp_end_s) * 1e6)


def _overshoot_pct(run):
    values = run["values"]
    v_final = values[-1]
    if v_final == 0:
        return 0.0
    return (max(values) - v_final) / abs(v_final) * 100


def _condition_label(conditions):
    return ",".join(f"{k}={v}" for k, v in conditions.items()) or "default"
