"""Parser for tb_top_startup.sch: vbg transient after supply power-up,
across different avdd ramp times and process corners (config.json's own
conditions.ramp_time/corner lists) -- top's own equivalent of
tb/cmos_vref/tb_vref_startup.py, at the regulated bandgap output (vbg)
instead of cmos_vref's raw vref, with trim0-3 fixed at their config.json
defaults (code 8, the centered code rbot_nominal/rbot_full are sized
around -- see params/top/default.json's own trim_factor description)
throughout.

Exists to answer a question tb/top's other .op/transient-based tests can't:
does top's own power-up settle to the SAME final vbg regardless of HOW it
gets there? tb_top_trim.py's own Gray-code trim staircase, at the exact
same (trim=0, tt corner, 25C) starting point this test's own typical
condition named AT THE TIME (config.json's own trim0-3 defaults have since
moved to code 8, see this docstring's own opening paragraph -- the ~1.14V
finding below is a historical record of that investigation, not a claim
about current behavior), was found to settle to a stable, smoothly-converged, but
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
import numpy as np

from parser_common import read_data, legend_if_any, typical_min_max, si_to_float

BAND_PCT = 2.0
MATCH_KEYS = ("corner", "temperature", "ramp_time")
# Fraction of the transient (by index, from the end) analyzed for ringing --
# excludes the initial power-up excursion/overshoot, whose broadband edge
# would otherwise swamp a real sustained oscillation's own spectral peak.
FFT_TAIL_FRACTION = 0.5
FFT_POINTS = 4096


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"times": [r[0] for r in rows], "values": [r[-1] for r in rows]}


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: list of {"conditions": {...}, "times": [...], "values": [...]},
    one per (corner, ramp_time) combination -- temperature is fixed for
    this test."""
    settled_spec, settling_spec, peak_spec, overshoot_spec, freq_spec = outputs

    settled = typical_min_max(runs, typical, lambda r: r["values"][-1], match_keys=MATCH_KEYS)
    settling = typical_min_max(runs, typical, _settling_time_us, match_keys=MATCH_KEYS)
    peak = typical_min_max(runs, typical, lambda r: max(r["values"]), match_keys=MATCH_KEYS)
    overshoot = typical_min_max(runs, typical, _overshoot_pct, match_keys=MATCH_KEYS)
    freq = typical_min_max(
        runs, typical, lambda r: (_dominant_oscillation(r) or (0.0, 0.0))[0] / 1e6, match_keys=MATCH_KEYS
    )

    metrics = []
    for spec, result in (
        (settled_spec, settled), (settling_spec, settling),
        (peak_spec, peak), (overshoot_spec, overshoot), (freq_spec, freq),
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

        _save_spectrum_plot(runs, f"{plot_base}__spectrum.png")

    return metrics


def _tail_spectrum(run):
    """(freqs_hz, magnitudes) of the FFT of the LAST FFT_TAIL_FRACTION of
    this run's own transient -- excludes the initial power-up excursion (a
    broadband edge, not a periodic signal) so a real sustained/ringing
    tail's own frequency isn't swamped by it. Detrends (removes the tail's
    own linear settling slope) before the FFT so a still-decaying-but-not-
    yet-flat tail doesn't leak huge low-frequency energy into the spectrum.
    (None, None) if the tail has too few points to bother (e.g. a very
    short ramp_time's total sim window)."""
    times, values = np.asarray(run["times"]), np.asarray(run["values"])
    n = len(times)
    start = int(n * (1 - FFT_TAIL_FRACTION))
    t_tail, v_tail = times[start:], values[start:]
    if len(t_tail) < 8 or t_tail[-1] <= t_tail[0]:
        return None, None

    # resample onto a uniform grid (raw transient timepoints are adaptive-
    # step, not evenly spaced -- FFT needs uniform sampling) at a rate set
    # by the tail's own median step, oversampled 2x as margin.
    dt = np.median(np.diff(t_tail))
    if dt <= 0:
        return None, None
    t_uniform = np.linspace(t_tail[0], t_tail[-1], min(FFT_POINTS, max(8, int((t_tail[-1] - t_tail[0]) / (dt / 2)))))
    v_uniform = np.interp(t_uniform, t_tail, v_tail)

    slope, intercept = np.polyfit(t_uniform, v_uniform, 1)
    v_detrended = v_uniform - (slope * t_uniform + intercept)

    sample_dt = t_uniform[1] - t_uniform[0]
    spectrum = np.abs(np.fft.rfft(v_detrended))
    freqs = np.fft.rfftfreq(len(v_uniform), d=sample_dt)
    return freqs, spectrum


def _dominant_oscillation(run):
    """(freq_hz, magnitude) of the strongest non-DC bin in _tail_spectrum's
    own FFT -- None if there's no usable spectrum."""
    freqs, spectrum = _tail_spectrum(run)
    if freqs is None or len(spectrum) < 2:
        return None
    peak_idx = 1 + int(np.argmax(spectrum[1:]))  # skip the DC bin (index 0)
    return float(freqs[peak_idx]), float(spectrum[peak_idx])


def _save_spectrum_plot(runs, path):
    fig, ax = plt.subplots(figsize=(6, 4))
    for run in runs:
        freqs, spectrum = _tail_spectrum(run)
        if freqs is None:
            continue
        ax.plot(freqs[1:] / 1e6, spectrum[1:], label=_condition_label(run["conditions"]))
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("|FFT(vbg tail, detrended)| (V)")
    ax.set_yscale("log")
    legend_if_any(ax, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _settling_time_us(run):
    """Time from the end of the avdd ramp until vbg last strayed outside
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
