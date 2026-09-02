"""Parser for tb_amp_openloop_ac.sch: open-loop AC characterization.

vp carries a 1V AC differential stimulus (on top of 'amp_vcm' DC), vn is
held at pure DC 'amp_vcm' -- no feedback, so vdb(vo) directly is the
open-loop transfer function. The testbench's `.control` block sets
`wr_singlescale` before `wrdata ... vdb(vo) vp(vo)`, so ngspice writes the
frequency column once (not once per vector): each row is
[freq, vdb, phase_deg] (3 columns) -- see _common.read_data.

Since vp (non-inverting) drives the stimulus directly with no inversion in
the path up to vo, phase starts near 0 deg at low frequency and rolls off
towards -180 deg as the two internal poles (first-stage cascode/mirror
node, second-stage vo_pre/vo Miller node) kick in. Phase margin is defined
here as `180 - abs(phase at the 0dB crossing)`, which is only meaningful
under that starting-near-0-deg assumption -- if a design revision inverts
the sign convention (e.g. by swapping vp/vn), this must be revisited."""
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import read_data, typical_min_max


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement.
    ngspice's vp() reports phase in RADIANS (not degrees despite the name
    suggesting otherwise) -- converted here so every downstream consumer of
    "phase_deg" can assume degrees. Before this conversion, _characterize's
    `180 - abs(phase_at_unity)` silently treated a radian-scale number
    (~0 to pi) as degrees, always landing near 180 regardless of the real
    margin."""
    rows = read_data(data_path)
    return {
        "freqs": [r[0] for r in rows],
        "vdb": [r[1] for r in rows],
        "phase_deg": [math.degrees(r[2]) for r in rows],
    }


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: list of {"conditions": {...}, "freqs", "vdb", "phase_deg"},
    one per corner/temperature. Reports {typical, min, max} DC gain, GBW
    and phase margin across all conditions -- GBW has no pass/fail spec (a
    low bandwidth is expected and acceptable for a DC buffer), it's
    reported for visibility only. GBW is reported in kHz, not MHz -- this
    buffer's bandwidth is deliberately unambitious (tens of kHz), so an MHz
    figure was reading as an awkward 0.0X."""
    gain_spec, gbw_spec, pm_spec = outputs[0], outputs[1], outputs[2]
    for r in runs:
        c = _characterize(r["freqs"], r["vdb"], r["phase_deg"])
        r["_dc_gain_db"] = c["dc_gain_db"]
        r["_gbw_hz"] = c["gbw_hz"]
        r["_gbw_khz"] = c["gbw_hz"] / 1e3
        r["_phase_margin_deg"] = c["phase_margin_deg"]

    match_keys = ("corner", "temperature", "ibias")
    gain = typical_min_max(runs, typical, lambda r: r["_dc_gain_db"], match_keys=match_keys)
    gbw = typical_min_max(runs, typical, lambda r: r["_gbw_khz"], match_keys=match_keys)
    pm = typical_min_max(runs, typical, lambda r: r["_phase_margin_deg"], match_keys=match_keys)

    if plot_base:
        typical_run = next(
            (r for r in runs if all(r["conditions"].get(k) == typical.get(k) for k in match_keys)),
            None,
        )
        if typical_run:
            _save_bode(typical_run, f"{plot_base}__typical.png")

        worst = min(runs, key=lambda r: r["_phase_margin_deg"])
        _save_bode(worst, f"{plot_base}__worst_case.png")

    return [
        {
            "name": gain_spec["description"],
            "typical": gain["typical"], "min": gain["min"], "max": gain["max"],
            "unit": gain_spec["unit"],
            "minimum": gain_spec.get("minimum"), "maximum": gain_spec.get("maximum"),
        },
        {
            "name": gbw_spec["description"],
            "typical": gbw["typical"], "min": gbw["min"], "max": gbw["max"],
            "unit": gbw_spec["unit"],
            "minimum": gbw_spec.get("minimum"), "maximum": gbw_spec.get("maximum"),
        },
        {
            "name": pm_spec["description"],
            "typical": pm["typical"], "min": pm["min"], "max": pm["max"],
            "unit": pm_spec["unit"],
            "minimum": pm_spec.get("minimum"), "maximum": pm_spec.get("maximum"),
        },
    ]


def _characterize(freqs, vdb, phase_deg):
    dc_gain_db = vdb[0]
    f_unity, phase_at_unity = _interp_crossing(freqs, vdb, phase_deg)
    phase_margin_deg = 180 - abs(phase_at_unity)
    return {"dc_gain_db": dc_gain_db, "gbw_hz": f_unity, "phase_margin_deg": phase_margin_deg}


def _interp_crossing(freqs, vdb, phase_deg):
    """First frequency (log-interpolated) where vdb crosses below 0dB. If
    the sweep never crosses -- gain stays above 0dB throughout (bandwidth
    exceeds the swept range) or starts below 0dB (essentially no gain) --
    falls back to the last/first point respectively rather than raising,
    since "off the edge of the sweep" is itself a valid (if imprecise)
    result to report."""
    for i in range(1, len(freqs)):
        if vdb[i - 1] >= 0 > vdb[i]:
            frac = vdb[i - 1] / (vdb[i - 1] - vdb[i])
            log_f = _lerp(_log10(freqs[i - 1]), _log10(freqs[i]), frac)
            phase = _lerp(phase_deg[i - 1], phase_deg[i], frac)
            return 10 ** log_f, phase
    if vdb[0] < 0:
        return freqs[0], phase_deg[0]
    return freqs[-1], phase_deg[-1]


def _lerp(a, b, frac):
    return a + (b - a) * frac


def _log10(x):
    return math.log10(x)


_DEFAULT_VIEW_CAP_HZ = 10e6


def _save_bode(run, path):
    """View defaults to a 10MHz-wide window -- plenty past this DC buffer's
    expected tens-of-kHz GBW, and far more readable than the full 10Hz-100MHz
    sweep .control asks for (see the .sch's `ac dec 20 10 100Meg` -- that
    full range is still simulated every time, only the plotted VIEW shrinks
    here). If a particular run's own GBW lands close to or past that cap
    (an unexpectedly fast sample), the view widens to 10x that run's GBW
    instead of silently cropping its 0dB crossing and phase-margin region
    off screen -- capped at the actual simulated top frequency either way."""
    fig, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(5, 5), sharex=True)
    ax_mag.semilogx(run["freqs"], run["vdb"])
    ax_mag.axhline(0, color="black", linestyle=":", linewidth=1)
    ax_mag.set_ylabel("Gain (dB)")
    ax_phase.semilogx(run["freqs"], run["phase_deg"])
    ax_phase.set_ylabel("Phase (deg)")
    ax_phase.set_xlabel("Frequency (Hz)")

    view_max = min(run["freqs"][-1], max(_DEFAULT_VIEW_CAP_HZ, run["_gbw_hz"] * 10))
    ax_phase.set_xlim(run["freqs"][0], view_max)

    fig.suptitle(_condition_label(run["conditions"]), fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _condition_label(conditions):
    return ",".join(f"{k}={v}" for k, v in conditions.items()) or "default"
