"""KNOWN ISSUE, RESOLVED VIA XYCE: ngspice-46's `noise` command fails to
converge its own internal bias-point solve on the actual cmos_vref circuit,
even though `.op`/`.ac` converge fine on the identical netlist. Tried and
none fixed it (each attempt failed with a DIFFERENT ngspice error signature
-- "too many iterations", then "doAnalyses: not found" -- suggesting real
numerical fragility, not one bad parameter): .nodeset seeded from the real
op point, .options rshunt=1e9, .options gminsteps=500, dropping the
explicit `op` before `noise`, and forcing PSP103's induced-gate noise off
(SWIGATE=0). A standalone PSP103 NMOS common-source stage (no feedback)
runs `.noise` cleanly in the same container/ngspice build, so the
ngspice+OSDI/.noise path itself works -- this is specific to the
self-biased vref topology (feedback loop + startup branch).

Xyce's `.NOISE` analysis converges cleanly on this exact circuit/topology
(confirmed live: 0 nonlinear convergence failures, 81 successful frequency
points, physically plausible noise values) -- this test now runs via the
"xyce" simulator (see config.json's tests.cmos_vref.noise entry and
run_sim.run_one_xyce()) instead of ngspice. tb_vref_noise.sch's stimuli
block is Xyce-flavored SPICE (.op/.noise/.print, no .control block,
.preprocess replaceground true for this project's named "GND" net
convention) -- see run_one_xyce()'s own comments for why its plugin
loading (-plugin, PSP103 only for now -- loading multiple Xyce plugins
together was confirmed to collide) and output post-processing (Xyce's
.print always prepends a header line + Index column, stripped before this
parser ever sees the file) differ from ngspice's OSDI/wrdata conventions.
extract()/evaluate() below are unchanged and unaware of which simulator
produced the data -- run_one_xyce() normalizes Xyce's output to the exact
same 2-column (freq, onoise) no-header shape ngspice's wrdata would have
produced.

Parser for tb_vref_noise.sch: output-referred voltage noise spectral
density of vref, swept from 'frequency_start' to 'frequency_stop' (.NOISE
analysis, 20 points/decade, both edges set by conditions.frequency_start/
frequency_stop in config.json). Column 1 is FREQ (Hz), column 2 is ONOISE
(V/sqrt(Hz), amplitude spectral density -- Xyce's .print noise ONOISE
convention, matching ngspice's onoise_spectrum convention this parser was
originally written against); rescaled to nV/sqrt(Hz) below for a
human-readable magnitude.

Flicker noise falls with frequency (~1/sqrt(f) in amplitude spectral
density) before flattening onto the thermal floor, so within the swept
band the worst (highest) density is always the value at
frequency_start -- same shape as tb_vref_psrr.py's worst-case-in-band
pick, just max instead of min since higher noise is worse."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import read_data, in_spec, add_spec_bounds, legend_if_any, typical_min_max, range_pass

_V_TO_NV = 1e9


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {
        "freqs": [r[0] for r in rows],
        "onoise_nv_rthz": [r[1] * _V_TO_NV for r in rows],
    }


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: list of {"conditions": {...}, "freqs", "onoise_nv_rthz"}, one
    per corner (temperature is fixed for this test). Each run's own worst
    (maximum) noise density seen at any swept frequency feeds
    {typical, min, max} across corners."""
    spec = outputs[0]
    result = typical_min_max(runs, typical, lambda r: max(r["onoise_nv_rthz"]))

    if plot_base:
        _save_plot(runs, spec, plot_base)

    return [{
        "name": spec["description"],
        "typical": result["typical"], "min": result["min"], "max": result["max"],
        "unit": spec["unit"],
        "minimum": spec.get("minimum"),
        "maximum": spec.get("maximum"),
        "pass": range_pass(result, spec),
    }]


def _save_plot(runs, spec, plot_base):
    all_values = [v for r in runs for v in r["onoise_nv_rthz"]]
    worst = max(
        ({"value": v, "freq": f, "label": _condition_label(r["conditions"])}
         for r in runs for f, v in zip(r["freqs"], r["onoise_nv_rthz"])),
        key=lambda w: w["value"],
    )

    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    for r in runs:
        label = _condition_label(r["conditions"])
        color = "tab:green" if in_spec(max(r["onoise_nv_rthz"]), spec) else "tab:red"
        ax.loglog(r["freqs"], r["onoise_nv_rthz"], label=label, color=color)

    ax.scatter([worst["freq"]], [worst["value"]], color="black", zorder=5)
    ax.annotate(
        # :.4g, not :.0f -- frequency_start is sub-1Hz for this test's own
        # band, and :.0f rounds e.g. 0.1 down to a misleading "0 Hz".
        f"worst: {worst['value']:.1f} nV/√Hz @ {worst['freq']:.4g} Hz ({worst['label']})",
        xy=(worst["freq"], worst["value"]), xytext=(0, 8), textcoords="offset points",
        ha="center", fontsize=7,
    )
    add_spec_bounds(ax, all_values, spec, orientation="y")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel(f"{spec['description']} ({spec['unit']})")
    legend_if_any(ax, fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{plot_base}.png", dpi=150)
    plt.close(fig)


def _condition_label(conditions):
    # Unlike tb_vref_psrr.py's identically-named helper, deliberately shows
    # only corner, not every key in `conditions` (which always also carries
    # temperature -- see run_sim.condition_matrix()) -- this test's own
    # config.json conditions pin temperature to a single value, so
    # "corner=tt,temperature=25" x3 legend entries differ only in the
    # corner term and just repeat the same fixed temperature three times.
    return conditions.get("corner", "default")
