"""Parser for tb_top_mismatch.sch: single-point (.op) vbg, repeated across
N independent random draws (this test's own conditions.mc_seed list) at a
FIXED corner/temperature/res_corner -- captures BOTH cmos_vref's own core
mismatch (M6/M7 mirror, M8/M9 cascode) AND output_amp's own differential-
pair (M1/M2) input-offset mismatch AND top's own R1-R8 feedback-divider
mismatch in the SAME simulated circuit, since all three sub-circuits are
instantiated together here -- unlike cmos_vref's own tb_vref_mismatch.py,
which only sees the core in isolation.

"corner" is "tt_mismatch" (local, intra-die device mismatch) or "tt_stat"
(global, inter-die process variation) depending on which config.json test
entry (vbg_mismatch vs vbg_stat) runs this same schematic/parser pair --
see run_sim.py's MOS_CORNER_SECTION. "res_corner" is the matching resistor
(rhigh, R1-R8's own device) corner -- "typ_mismatch"/"typ_stat" -- kept as
an INDEPENDENT axis from "corner" (see run_sim.py's RES_CORNER_SECTION) so
a future study can decouple them (e.g. "typical MOS, worst-case resistor")
via plain conditions{} list edits, no code change."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import add_spec_bounds, mc_stats, range_pass, read_data


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement.
    wrdata's own wr_singlescale duplicates a single requested vector
    (v(vbg)) into 2 columns -- same "grab the last column" convention every
    other single-quantity .op parser in this project already uses."""
    rows = read_data(data_path)
    return {"vbg_v": rows[-1][-1]}


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: N independent random draws at the same fixed conditions -- see
    this module's own docstring. Like tb/cmos_vref/tb_vref_mismatch.py,
    this does NOT use parser_common.typical_min_max() (no single run here
    is more "typical" than another) -- mc_stats() reports {typical=None,
    mean, std, min, max} instead. `typical` is accepted for signature
    compatibility but unused."""
    vbg_spec = outputs[0]
    vbg = mc_stats(runs, lambda r: r["vbg_v"])

    if plot_base:
        _save_histogram([r["vbg_v"] for r in runs], vbg_spec, f"{plot_base}.png")

    return [{
        "name": vbg_spec["description"],
        "typical": vbg["typical"], "mean": vbg["mean"], "std": vbg["std"],
        "min": vbg["min"], "max": vbg["max"],
        "unit": vbg_spec["unit"],
        "minimum": vbg_spec.get("minimum"), "maximum": vbg_spec.get("maximum"),
        "pass": range_pass(vbg, vbg_spec),
    }]


def _save_histogram(values, spec, path):
    """Distribution of vbg across every Monte Carlo draw -- see
    tb/cmos_vref/tb_vref_mismatch.py's own _save_histogram() for why this
    is the natural view here (no per-condition label worth drawing, every
    run shares the same corner/temperature/res_corner, only the seed
    differs)."""
    fig, ax = plt.subplots(figsize=(5, 3.5))
    n_bins = max(5, min(20, len(values) // 3))
    ax.hist(values, bins=n_bins, color="tab:blue", edgecolor="white")
    add_spec_bounds(ax, values, spec, orientation="x")
    ax.set_xlabel(f"{spec['description']} ({spec['unit']})")
    ax.set_ylabel("count")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
