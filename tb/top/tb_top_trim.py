"""Parser for tb_top_trim.sch: single-point (.op) vbg, one independent
condition per trim code (this test's own conditions.trim0..trim3 lists,
each ["0", "1.8"]) crossed with corner/temperature -- answers "do the 16
trim words actually reach 1200mV somewhere in their range, at every corner
top is expected to operate at", as opposed to tb_top_mismatch.py's
vbg_mismatch/vbg_stat (fixed at config.json's own trim0-3 default, code 8,
with random device draws instead of a code sweep).

This is a bare .op, same convention as every other top-level test
(current_consumption, amp_bias_current, vbg_mismatch/vbg_stat) -- earlier
attempts at this exact test (a first bare-.op version, then a `.nodeset`+
`reset`+`alter`+`op` loop mirroring the sky130_ak_ip__cmos_vref sibling
project, then a Gray-code PWL staircase inside a settled transient) all
produced non-monotonic or outright non-convergent (`Warning: singular
matrix: check node x1.sub!`, silently falling back to an unreliable
pseudo-transient every time) results -- root-caused to sch/top/
top_default.sch's own trim/ena gate-drive buffers being bound to a
dangling VDD/VSS instead of dvdd/dvss, AND (found afterward, see
sch/cmos_vref.sym's own history) cmos_vref/output_amp's NMOS bulk
connections never having an explicit, hierarchically-wired SUB
(substrate) pin -- both now fixed. With that root cause gone, the
simplest/cheapest methodology (independent bare .op per code, matching
every other top-level test) converges cleanly with zero singular-matrix
warnings across all 16 codes x 3 corners x 3 temperatures -- confirmed
before writing this version, see this project's own memory notes."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import add_spec_bounds, legend_if_any, read_data

VBG_TARGET_V = 1.2
WITHIN_SPEC_V = 0.012  # +/-1% of 1200mV -- a placeholder tolerance, not yet
                       # confirmed against the proposal's own trimmed-accuracy spec.


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"vbg_v": rows[-1][-1]}


def _trim_code(conditions):
    bits = (conditions["trim0"], conditions["trim1"], conditions["trim2"], conditions["trim3"])
    return sum((1 << i) for i, bit in enumerate(bits) if bit != "0")


def _group_key(conditions):
    return (conditions["corner"], conditions["temperature"])


def evaluate(runs, outputs, typical, plot_base=None):
    """runs: one per (corner, temperature, trim0, trim1, trim2, trim3)
    combination -- grouped here by (corner, temperature) into 16-code
    trim sweeps, each reduced to its own best-achievable error and in-spec
    code count before being reported as a {typical, min, max} across every
    group, like typical_min_max() but with a per-group reduction step
    first instead of a bare per-run value."""
    err_spec, count_spec = outputs

    groups = {}
    for r in runs:
        groups.setdefault(_group_key(r["conditions"]), []).append(r)

    per_group = {}
    for key, group_runs in groups.items():
        by_code = {_trim_code(r["conditions"]): r["vbg_v"] for r in group_runs}
        errors_v = {code: abs(v - VBG_TARGET_V) for code, v in by_code.items()}
        best_code = min(errors_v, key=errors_v.get)
        per_group[key] = {
            "by_code": by_code,
            "best_code": best_code,
            "best_err_mv": errors_v[best_code] * 1e3,
            "within_spec_count": sum(1 for e in errors_v.values() if e <= WITHIN_SPEC_V),
        }

    typical_key = (typical["corner"], typical["temperature"])
    typical_group = per_group.get(typical_key)

    best_errs = [g["best_err_mv"] for g in per_group.values()]
    counts = [g["within_spec_count"] for g in per_group.values()]

    if plot_base:
        _save_plot(per_group, f"{plot_base}.png")

    return [
        {
            "name": err_spec["description"],
            "typical": typical_group["best_err_mv"] if typical_group else None,
            "min": min(best_errs), "max": max(best_errs),
            "unit": err_spec["unit"],
            "minimum": err_spec.get("minimum"), "maximum": err_spec.get("maximum"),
        },
        {
            "name": count_spec["description"],
            "typical": typical_group["within_spec_count"] if typical_group else None,
            "min": min(counts), "max": max(counts),
            "unit": count_spec["unit"],
            "minimum": count_spec.get("minimum"), "maximum": count_spec.get("maximum"),
        },
    ]


def _save_plot(per_group, path):
    """One line per (corner, temperature) group, vbg vs trim code 0-15 --
    a group whose line never crosses 1200mV has no code that fixes it,
    which is exactly the failure mode this test exists to catch."""
    fig, ax = plt.subplots(figsize=(6, 4))
    all_values = [v for g in per_group.values() for v in g["by_code"].values()]
    for (corner, temperature), g in sorted(per_group.items()):
        codes = sorted(g["by_code"])
        values = [g["by_code"][c] for c in codes]
        ax.plot(codes, values, marker="o", markersize=3, label=f"{corner}, {temperature}C")
    ax.axhline(VBG_TARGET_V, color="black", linestyle="--", linewidth=1, label="1200mV target")
    add_spec_bounds(ax, all_values, {}, orientation="y")
    ax.set_xlabel("trim code (0-15)")
    ax.set_ylabel("vbg (V)")
    legend_if_any(ax, fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
