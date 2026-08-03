"""Generic helpers shared by cmos_vref testbench parsers (no test-specific logic)."""


def read_data(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append([float(x) for x in line.split()])
    return rows


def in_spec(value, spec):
    if "minimum" in spec and value < spec["minimum"]:
        return False
    if "maximum" in spec and value > spec["maximum"]:
        return False
    return True


def legend_if_any(ax, **kwargs):
    """ax.legend() warns and draws an empty box when nothing has a label
    (e.g. every spec bound was off-scale and got annotated as text instead)."""
    handles, _ = ax.get_legend_handles_labels()
    if handles:
        ax.legend(**kwargs)


def add_spec_bounds(ax, values, spec, orientation="y"):
    """Draw min/max spec reference lines, but only if they fall within a
    sane margin of the actual plotted data. A spec bound that's orders of
    magnitude away from the data would otherwise force the axis to stretch
    until the real curve/bars are indistinguishable from zero -- in that
    case just note it as text instead of drawing a line."""
    lo, hi = min(values), max(values)
    span = (hi - lo) or abs(hi) or 1.0
    margin = span * 0.15
    view_lo, view_hi = lo - margin, hi + margin

    line_fn = ax.axhline if orientation == "y" else ax.axvline
    styles = {"minimum": "--", "maximum": ":"}
    notes = []
    for key, style in styles.items():
        if key not in spec:
            continue
        bound = spec[key]
        if view_lo <= bound <= view_hi:
            line_fn(bound, color="black", linestyle=style, linewidth=1, label=key)
        else:
            notes.append(f"{key}: {bound} {spec.get('unit', '')} (off scale)")

    if orientation == "y":
        ax.set_ylim(view_lo, view_hi)
    else:
        ax.set_xlim(view_lo, view_hi)

    if notes:
        ax.text(
            0.02, 0.98, "\n".join(notes), transform=ax.transAxes,
            va="top", ha="left", fontsize=7,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.85, edgecolor="gray"),
        )
