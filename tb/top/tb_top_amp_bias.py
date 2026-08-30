"""Parser for tb_top_amp_bias.sch: single-point (.op) real bias current
delivered to output_amp's ibias pin once cmos_vref (X1) and output_amp
(x2) are composed together inside top -- v.x1.vm_b3#branch, the ammeter
already wired in sch/top/top_default.sch in series with M1's source
(originally tagged lvs_ignore=short, placed for LVS purposes, never read
by any parser before this test). The ngspice vector name for a branch
current through a hierarchical subcircuit instance is
"v.<instance>.<source>#branch", not "i(<instance>.<source>)" (confirmed
empirically -- the latter raises "no such function as i"). Compares this
real, mirror-derived current against the
100nA output_amp was actually designed/verified against standalone (see
config.json defaults.ibias and tb/output_amp's own testbenches).

params/top/default.json's amp_bias_width is computed automatically
(cross_block "scale_to_target") from cmos_vref's own measured
reference_current test, but that's a single-shot, open-loop estimate, NOT
a guarantee -- KNOWN LIMITATION, measured on the default parameter set:
cmos_vref's reference_current test measures M3 on a clean, directly-set
1.8V supply, while inside top the same core is fed through the M2
enable-switch PMOS (a several-tens-of-mV drop); combined with this mirror
apparently running in weak/moderate inversion (VSG close to Vth), that
supply difference alone was observed to cause roughly a 3x mismatch
between the calculated target and what this test actually measures at the
nominal corner/temperature -- this test is expected to FAIL until that gap
is closed by hand (e.g. tuning `target` in params/top/default.json against
this test's own result) or the calibration environment is improved. This
test is the ground truth for that gap; don't assume amp_bias_width's
calculation is exact just because it's automatic."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_common import read_data, in_spec, add_spec_bounds, legend_if_any


def extract(data_path):
    """Raw reduction of one simulation run's .data file. No spec judgement."""
    rows = read_data(data_path)
    return {"current_na": abs(rows[-1][-1]) * 1e9}


def evaluate(runs, outputs, plot_base=None):
    """runs: list of {"conditions": {...}, "current_na": ...}, one per
    condition (temperature, corner, ...) this test was simulated at.
    Returns one named metric: the worst-case value across all conditions."""
    spec = outputs[0]
    values = [r["current_na"] for r in runs]
    passed = all(in_spec(v, spec) for v in values)

    if plot_base and len(runs) > 1:
        labels = [_condition_label(r["conditions"]) for r in runs]
        colors = ["tab:green" if in_spec(v, spec) else "tab:red" for v in values]
        fig, ax = plt.subplots(figsize=(max(4, len(runs) * 0.6), 3))
        ax.bar(labels, values, color=colors)
        add_spec_bounds(ax, values, spec, orientation="y")
        ax.set_ylabel(f"{spec['description']} ({spec['unit']})")
        ax.tick_params(axis="x", rotation=45)
        legend_if_any(ax, fontsize=8)
        fig.tight_layout()
        fig.savefig(f"{plot_base}.png", dpi=150)
        plt.close(fig)

    return [{
        "name": spec["description"],
        "value": _worst_case(values, spec),
        "unit": spec["unit"],
        "minimum": spec.get("minimum"),
        "maximum": spec.get("maximum"),
        "pass": passed,
    }]


def _worst_case(values, spec):
    def violation(v):
        over = v - spec["maximum"] if "maximum" in spec else 0
        under = spec["minimum"] - v if "minimum" in spec else 0
        return max(over, under, 0)
    return max(values, key=lambda v: (violation(v), v))


def _condition_label(conditions):
    return ",".join(f"{k}={v}" for k, v in conditions.items()) or "default"
