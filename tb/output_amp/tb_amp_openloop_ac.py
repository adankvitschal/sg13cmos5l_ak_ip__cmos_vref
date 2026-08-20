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

from _common import read_data, in_spec


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {
        "freqs": [r[0] for r in rows],
        "vdb": [r[1] for r in rows],
        "phase_deg": [r[2] for r in rows],
    }


def evaluate(runs, outputs, plot_base=None):
    """runs: list of {"conditions": {...}, "freqs", "vdb", "phase_deg"},
    one per corner/temperature. Reports the worst (minimum) DC gain, GBW
    and phase margin seen across all conditions -- GBW has no pass/fail
    spec (a low bandwidth is expected and acceptable for a DC buffer), it's
    reported for visibility only."""
    gain_spec, gbw_spec, pm_spec = outputs[0], outputs[1], outputs[2]
    per_run = [_characterize(r["freqs"], r["vdb"], r["phase_deg"]) for r in runs]
    dc_gain = min(r["dc_gain_db"] for r in per_run)
    gbw_mhz = min(r["gbw_hz"] for r in per_run) / 1e6
    phase_margin = min(r["phase_margin_deg"] for r in per_run)

    if plot_base:
        worst = min(zip(runs, per_run), key=lambda rp: rp[1]["phase_margin_deg"])[0]
        _save_bode(worst, f"{plot_base}__worst_case.png")

    return [
        {
            "name": gain_spec["description"], "value": dc_gain,
            "unit": gain_spec["unit"],
            "minimum": gain_spec.get("minimum"), "maximum": gain_spec.get("maximum"),
            "pass": in_spec(dc_gain, gain_spec),
        },
        {
            "name": gbw_spec["description"], "value": gbw_mhz,
            "unit": gbw_spec["unit"],
            "minimum": gbw_spec.get("minimum"), "maximum": gbw_spec.get("maximum"),
            "pass": in_spec(gbw_mhz, gbw_spec),
        },
        {
            "name": pm_spec["description"], "value": phase_margin,
            "unit": pm_spec["unit"],
            "minimum": pm_spec.get("minimum"), "maximum": pm_spec.get("maximum"),
            "pass": in_spec(phase_margin, pm_spec),
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


def _save_bode(run, path):
    fig, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(5, 5), sharex=True)
    ax_mag.semilogx(run["freqs"], run["vdb"])
    ax_mag.axhline(0, color="black", linestyle=":", linewidth=1)
    ax_mag.set_ylabel("Gain (dB)")
    ax_phase.semilogx(run["freqs"], run["phase_deg"])
    ax_phase.set_ylabel("Phase (deg)")
    ax_phase.set_xlabel("Frequency (Hz)")
    fig.suptitle(_condition_label(run["conditions"]), fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _condition_label(conditions):
    return ",".join(f"{k}={v}" for k, v in conditions.items()) or "default"
