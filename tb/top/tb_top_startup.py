"""Parser for tb_top_startup.sch: vbg transient after supply power-up,
across different avdd18 ramp times and process corners (config.json's own
conditions.ramp_time/corner lists) -- top's own equivalent of
tb/cmos_vref/tb_vref_startup.py, at the regulated bandgap output (vbg)
instead of cmos_vref's raw vref, with trim0-3 fixed at their config.json
defaults ("0", untrimmed) throughout.

Exists to answer a question tb/top's other .op/transient-based tests can't:
does top's own power-up settle to the SAME final vbg regardless of HOW it
gets there? tb_top_trim.py's own Gray-code trim staircase, at the exact
same (trim=0, tt corner, 25C) starting point this test's own typical
condition names, was found to settle to a stable, smoothly-converged, but
WRONG value (~1.14V, 60mV off the ~1.20V this project's temp_sweep/
per-code-transient references already agree on) -- not noise or
non-convergence, a genuinely different equilibrium reached because of
something about that staircase's own long PWL breakpoint list (not
because top's startup is inherently chaotic with a PLAIN, non-staircase
trim source, which is what THIS test uses). settled_v below is the direct
diagnostic: if it agrees across every ramp_time/corner here, the
staircase's own breakpoint list is the culprit and needs a narrower fix;
if it DOESN'T, top's own power-up genuinely has more than one reachable
equilibrium and every dynamic top-level test (vbg_mismatch/vbg_stat/
amp_bias_current included, all bare .op, all with their own unexamined
cold-start point) needs to be revisited."""
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
    one per (corner, ramp_time) combination -- temperature is fixed for
    this test."""
    settled_spec, settling_spec, peak_spec, overshoot_spec = outputs

    settled = typical_min_max(runs, typical, lambda r: r["values"][-1], match_keys=MATCH_KEYS)
    settling = typical_min_max(runs, typical, _settling_time_us, match_keys=MATCH_KEYS)
    peak = typical_min_max(runs, typical, lambda r: max(r["values"]), match_keys=MATCH_KEYS)
    overshoot = typical_min_max(runs, typical, _overshoot_pct, match_keys=MATCH_KEYS)

    metrics = []
    for spec, result in (
        (settled_spec, settled), (settling_spec, settling),
        (peak_spec, peak), (overshoot_spec, overshoot),
    ):
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
        ax.set_ylabel("vbg (V)")
        legend_if_any(ax, fontsize=8)
        fig.tight_layout()
        fig.savefig(f"{plot_base}.png", dpi=150)
        plt.close(fig)

    return metrics


def _settling_time_us(run):
    """Time from the end of the avdd18 ramp until vbg last strayed outside
    its +-BAND_PCT band -- see tb/cmos_vref/tb_vref_startup.py's own
    identical convention."""
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
