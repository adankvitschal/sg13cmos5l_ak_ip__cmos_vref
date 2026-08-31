"""Parser for tb_vref_mismatch.sch: single-point (.op) Vref + core reference
current, repeated across N independent random draws (see this test's own
conditions.mc_seed list in config.json) at a FIXED corner/temperature --
"corner" here is either "tt_mismatch" (local, intra-die device mismatch:
per-instance agauss() on Vt/mobility/W/L, layered on the tt process point)
or "tt_stat" (global, inter-die process variation: all devices shift
together per random draw, no per-instance mismatch) depending on which
config.json test entry (vref_mismatch vs vref_stat) runs this same
schematic/parser pair.

Each of the N conditions.mc_seed values doesn't correspond to any real
testbench token -- it exists purely to make condition_matrix() spawn N
separate ngspice processes, each of which draws its own fresh
agauss()/gauss() sample automatically (confirmed empirically: ngspice
reseeds its RNG per process, but NOT between two .op reruns inside the
SAME process -- see run_sim.py's own MOS_CORNER_SECTION/RES_CORNER_SECTION
docstrings for the corner-selection half of this).

cmos_vref's own core has no resistor devices (never .lib-includes
cornerRES.lib in any of its testbenches) -- unlike top's own tb_top_mismatch.sch,
this test only needs the MOS mismatch/stat corner, not a resistor one."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import add_spec_bounds, mc_stats, range_pass, read_data


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement.
    wrdata's own wr_singlescale duplicates the FIRST requested vector as a
    leading "scale" column (confirmed empirically), so a 2-vector wrdata
    (v(vref), the M3-branch current) yields 3 columns: [v(vref) again,
    v(vref), branch_current] -- the same "grab from the end" convention
    tb_vref_ref_current.py's own single-vector extract() already uses."""
    rows = read_data(data_path)
    row = rows[-1]
    return {"vref_v": row[-2], "current_na": abs(row[-1]) * 1e9}


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: N independent random draws at the same fixed conditions --
    see this module's own docstring. Unlike every other parser, this one
    does NOT use parser_common.typical_min_max() (which assumes exactly
    one run is "the" typical one, matched by conditions) -- every run here
    is equally representative, so mc_stats() reports {typical=None, mean,
    std, min, max} instead. `typical` (the resolved nominal-conditions
    dict every other parser matches against) is accepted for signature
    compatibility but unused."""
    vref_spec, current_spec = outputs[0], outputs[1]
    vref = mc_stats(runs, lambda r: r["vref_v"])
    current = mc_stats(runs, lambda r: r["current_na"])

    if plot_base:
        _save_histogram([r["vref_v"] for r in runs], vref_spec, f"{plot_base}__vref.png")
        _save_histogram([r["current_na"] for r in runs], current_spec, f"{plot_base}__reference_current.png")

    return [
        {
            "name": vref_spec["description"],
            "typical": vref["typical"], "mean": vref["mean"], "std": vref["std"],
            "min": vref["min"], "max": vref["max"],
            "unit": vref_spec["unit"],
            "minimum": vref_spec.get("minimum"), "maximum": vref_spec.get("maximum"),
            "pass": range_pass(vref, vref_spec),
        },
        {
            "name": current_spec["description"],
            "typical": current["typical"], "mean": current["mean"], "std": current["std"],
            "min": current["min"], "max": current["max"],
            "unit": current_spec["unit"],
            "minimum": current_spec.get("minimum"), "maximum": current_spec.get("maximum"),
            "pass": range_pass(current, current_spec),
        },
    ]


def _save_histogram(values, spec, path):
    """Distribution of one metric across every Monte Carlo draw -- the
    natural view for a mismatch/stat sweep (shape, outliers, how tight the
    spread is), unlike every other parser's condition-labeled line/bar
    plots since there's no "condition" here worth labeling (every run
    shares the same corner/temperature, only the random seed differs)."""
    fig, ax = plt.subplots(figsize=(5, 3.5))
    n_bins = max(5, min(20, len(values) // 3))
    ax.hist(values, bins=n_bins, color="tab:blue", edgecolor="white")
    add_spec_bounds(ax, values, spec, orientation="x")
    ax.set_xlabel(f"{spec['description']} ({spec['unit']})")
    ax.set_ylabel("count")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
