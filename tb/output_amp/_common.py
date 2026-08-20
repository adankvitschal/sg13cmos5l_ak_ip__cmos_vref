"""Generic helpers shared by output_amp testbench parsers (no test-specific logic),
plus regulation_pct() below -- an exception kept here because it's byte-identical
to the cmos_vref version, not because it's generic."""
import re

_SI_SUFFIXES = {"": 1, "f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6,
                "m": 1e-3, "k": 1e3, "meg": 1e6, "g": 1e9}


def read_data(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append([float(x) for x in line.split()])
    return rows


def regulation_pct(values):
    """Box-method regulation: (max-min)/|nominal| * 100, nominal = midpoint of the
    swept values. abs() on the midpoint keeps this a magnitude -- without it, an
    output that's off badly enough to swing through zero across the sweep gets a
    negative nominal, which sign-flips the result into a small-looking negative
    percentage instead of the large one that swing actually represents."""
    nom = abs((max(values) + min(values)) / 2)
    return (max(values) - min(values)) / nom * 100


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


def _si_to_float(text):
    m = re.fullmatch(r"([0-9.eE+-]+)([a-zA-Z]*)", text)
    if not m or m.group(2).lower() not in _SI_SUFFIXES:
        raise ValueError(f"not a SPICE numeric literal: {text!r}")
    return float(m.group(1)) * _SI_SUFFIXES[m.group(2).lower()]


def parse_sized_devices(netlist_text):
    """Every X-instance line in an xschem-expanded netlist that carries both
    w= and l= parameters -- i.e. a sized primitive device (MOS, MiM cap,
    poly resistor, ...) as opposed to a pure subcircuit-wiring X-line (no
    w=/l=), which is skipped. Line shape: `X<name> <pin> ... <model>
    <key>=<value> ...` -- the model name is whatever token sits right
    before the first key=value pair. Returns [{"instance", "model", "w",
    "l" (meters), "m", "ng" (default 1 when absent)}, ...]."""
    devices = []
    for line in netlist_text.splitlines():
        line = line.strip()
        if not line.startswith("X"):
            continue
        tokens = line.split()
        first_param = next((i for i, t in enumerate(tokens) if "=" in t), None)
        if first_param is None or first_param < 2:
            continue
        params = {}
        for tok in tokens[first_param:]:
            if "=" not in tok:
                continue
            key, val = tok.split("=", 1)
            try:
                params[key.lower()] = _si_to_float(val)
            except ValueError:
                continue
        if "w" not in params or "l" not in params:
            continue
        devices.append({
            "instance": tokens[0],
            "model": tokens[first_param - 1],
            "w": params["w"],
            "l": params["l"],
            "m": params.get("m", 1),
            "ng": params.get("ng", params.get("nf", 1)),
        })
    return devices


def estimate_area_um2(netlist_text, overhead_factor):
    """Schematic-only area proxy, no layout involved: sum(w*l*ng*m) over
    every sized device in the netlist gives raw active/plate area; ng is
    assumed to multiply like BSIM's nf (w = per-finger width) -- correct
    this if a given device model's convention differs. overhead_factor
    scales that up to approximate what wells, guard rings and routing add
    in a real placed-and-routed layout. Only meaningful for RANKING
    variations of the same topology against each other -- not a substitute
    for an actual layout's mm^2 figure."""
    devices = parse_sized_devices(netlist_text)
    active_area_um2 = sum(d["w"] * d["l"] * d["ng"] * d["m"] for d in devices) * 1e12
    return {
        "device_count": len(devices),
        "active_area_um2": active_area_um2,
        "estimated_area_um2": active_area_um2 * overhead_factor,
    }


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
