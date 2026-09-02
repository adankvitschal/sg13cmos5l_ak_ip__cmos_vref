"""Parser for tb_top_stability.sch: AC loop-gain measurement of top's own
closed feedback loop (vbg -> R1/R2/R3 divider -> feedback tap -> output_amp's
own inverting input vn -> amp -> vo=vbg, closing the loop), broken at the
divider-tap/amp-input boundary via the standard series L(1e12H)+V(AC 1)
injection technique (sch/top/top_default.sch's own loop_in/loop_out pins,
added specifically for this test -- see that file's own history).

Exists because tb_top_startup.sch showed a genuine, UNDAMPED, sustained
oscillation (~5-10kHz, constant amplitude for the entire simulated window,
not just slow settling) across all 3 process corners -- yet output_amp's
own standalone openloop_ac test reports a healthy 84.8 degree phase margin.
That number doesn't transfer here: openloop_ac tests output_amp alone in a
UNITY-feedback (direct wire vo->vn) configuration, with none of top's own
R1-R8 divider network (large resistors, hundreds of kOhm-MOhm) or trim
switch parasitics in the loop -- exactly the kind of extra pole a real
resistive feedback network can add that a simplified unity-gain bench
test never sees. This test measures the REAL closed-loop stability with
that network actually in place.

Sign convention: with the break defined as V(loop_out) - V(loop_in) =
Vinj (KVL across the near-zero-current L branch), and Va=V(loop_in),
Vb=V(loop_out) related by Va = T(jw)*Vb (T being the transfer around the
WHOLE loop starting from the amp's own input), it follows directly that
T(jw) = V(loop_in)/V(loop_out) -- no extra sign flip needed. Phase margin
is read at T's own 0dB crossing: PM = 180 + phase(T) (degrees) at that
frequency, using the standard "avoid the -1 point" criterion for a T
already carrying whatever inherent sign/phase this negative-feedback loop
has baked in."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import legend_if_any, read_data, typical_min_max


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {
        "freq_hz": [r[0] for r in rows],
        "mag_db": [r[1] for r in rows],
        "phase_deg": [r[2] for r in rows],
    }


def _unity_gain_crossover(run):
    """(frequency, phase) at the first freq where |T| crosses 0dB going
    downward -- None if T never crosses (either always <0dB, i.e. no loop
    gain to speak of, or never drops below 0dB across the whole sweep)."""
    freqs, mags, phases = run["freq_hz"], run["mag_db"], run["phase_deg"]
    for i in range(1, len(mags)):
        if mags[i - 1] >= 0 > mags[i]:
            # linear interpolation in log-frequency for the crossing point
            frac = mags[i - 1] / (mags[i - 1] - mags[i])
            freq_x = freqs[i - 1] * (freqs[i] / freqs[i - 1]) ** frac
            phase_x = phases[i - 1] + frac * (phases[i] - phases[i - 1])
            return freq_x, phase_x
    return None


def _phase_margin_deg(run):
    crossing = _unity_gain_crossover(run)
    if crossing is None:
        return None
    _, phase_x = crossing
    return 180.0 + phase_x


def _crossover_freq(run):
    crossing = _unity_gain_crossover(run)
    return crossing[0] if crossing else None


def _dc_loop_gain_db(run):
    return run["mag_db"][0]


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: one per (corner, temperature) this test's conditions cross."""
    dc_spec, xover_spec, pm_spec = outputs

    dc_gain = typical_min_max(runs, typical, _dc_loop_gain_db)
    xover = typical_min_max(
        runs, typical, lambda r: _crossover_freq(r) or 0.0
    )
    pm = typical_min_max(
        runs, typical, lambda r: _phase_margin_deg(r) if _phase_margin_deg(r) is not None else -999.0
    )

    if plot_base:
        _save_plot(runs, f"{plot_base}.png")

    return [
        {
            "name": dc_spec["description"],
            "typical": dc_gain["typical"], "min": dc_gain["min"], "max": dc_gain["max"],
            "unit": dc_spec["unit"],
            "minimum": dc_spec.get("minimum"), "maximum": dc_spec.get("maximum"),
        },
        {
            "name": xover_spec["description"],
            "typical": xover["typical"], "min": xover["min"], "max": xover["max"],
            "unit": xover_spec["unit"],
            "minimum": xover_spec.get("minimum"), "maximum": xover_spec.get("maximum"),
        },
        {
            "name": pm_spec["description"],
            "typical": pm["typical"], "min": pm["min"], "max": pm["max"],
            "unit": pm_spec["unit"],
            "minimum": pm_spec.get("minimum"), "maximum": pm_spec.get("maximum"),
        },
    ]


def _save_plot(runs, path):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 6), sharex=True)
    for run in runs:
        label = f"{run['conditions'].get('corner')}"
        ax1.semilogx(run["freq_hz"], run["mag_db"], label=label)
        ax2.semilogx(run["freq_hz"], run["phase_deg"], label=label)
    ax1.axhline(0, color="black", linestyle="--", linewidth=1)
    ax2.axhline(-180, color="black", linestyle="--", linewidth=1)
    ax1.set_ylabel("Loop gain |T| (dB)")
    ax2.set_ylabel("Loop gain phase (deg)")
    ax2.set_xlabel("Frequency (Hz)")
    legend_if_any(ax1, fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
