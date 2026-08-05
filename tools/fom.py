"""Figure-of-merit: classifies a variation into named design profiles (per
a block's config.json `blocks.<block>.profiles`) and evaluates each
profile's own FoM formula against the variation's metrics from
results.jsonl. Generic infrastructure -- no per-block/per-test logic lives
here, unlike the testbench parsers under tb/<block>/.

Tests report raw values only -- there is no absolute per-test pass/fail
spec (deliberately removed: it duplicated and sometimes conflicted with
profile-level judgment). A profile has its own `constraints` dict (metric
slug -> {"minimum"?, "maximum"?}) which is simultaneously the gate for
"does this variation qualify" and the source of that profile's own
`<slug>_min`/`<slug>_max` normalization terms -- e.g.:
    "pow(vref_core_current_consumption/vref_core_current_consumption_max, -1)"
evaluated with a restricted AST walker (no attribute access, no
subscripting, no arbitrary calls) -- config.json is trusted local input, but
there's no reason to run a full eval() over it.

Variables available to a formula:
  <slug>       -- each metric's value, keyed by slugify(metric description)
  <slug>_min   -- this profile's own constraint minimum, if it declared one
  <slug>_max   -- this profile's own constraint maximum, if it declared one
"""
import ast
import operator
import re

_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
}
_UNARYOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCS = {"abs": abs, "min": min, "max": max, "round": round, "pow": pow}


def slugify(text):
    return re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")


def metrics_to_variables(metrics):
    """<slug>: value, one per metric. No _min/_max here -- those are
    profile-specific (see classify()), since there's no absolute per-test
    spec to derive a single global bound from anymore."""
    return {slugify(m["metric"]): float(m["value"]) for m in metrics}


def _eval_node(node, variables):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, variables)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name):
        if node.id not in variables:
            raise KeyError(f"unknown variable {node.id!r} (no metric produced this name for this variation)")
        return variables[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        return _BINOPS[type(node.op)](_eval_node(node.left, variables), _eval_node(node.right, variables))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARYOPS:
        return _UNARYOPS[type(node.op)](_eval_node(node.operand, variables))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS:
        return _FUNCS[node.func.id](*(_eval_node(a, variables) for a in node.args))
    raise ValueError(f"unsupported expression syntax: {ast.dump(node)}")


def safe_eval(expr, variables):
    return _eval_node(ast.parse(expr, mode="eval"), variables)


def constraint_satisfied(slug, bounds, variables):
    """Whether variables[slug] (from metrics_to_variables()) satisfies one
    {"minimum"?, "maximum"?} bound. Public -- the GUI reuses this to show
    per-metric pass/fail relative to whichever profile is selected, since
    there's no absolute spec to check against anymore."""
    if slug not in variables:
        return False  # no data for this metric yet -- counts against it, not skipped
    value = variables[slug]
    if "minimum" in bounds and value < bounds["minimum"]:
        return False
    if "maximum" in bounds and value > bounds["maximum"]:
        return False
    return True


def classify(block_cfg, metrics):
    """block_cfg: config.json blocks.<block> dict (profiles lives as a
    sibling of "topologies", not inside it). metrics: latest_results()
    rows for one variation. Returns one entry per profile declared in
    block_cfg["profiles"], in config declaration order -- NOT filtered to
    full matches, so callers can see how close an unmatched profile got.
        [{"profile": name, "description": ..., "constraints": {...},
          "n_satisfied": int, "n_constraints": int, "matched": bool,
          "fom": float|None, "fom_error": str|None}, ...]
    A missing metric counts as an unsatisfied constraint (not skipped).
    fom is attempted regardless of match status; a formula referencing a
    metric this variation lacks (or that isn't one of this profile's own
    constraints, so has no _min/_max) surfaces as fom_error."""
    base_variables = metrics_to_variables(metrics)
    results = []
    for name, profile in block_cfg.get("profiles", {}).items():
        constraints = profile.get("constraints", {})
        n_satisfied = sum(
            1 for slug, bounds in constraints.items()
            if constraint_satisfied(slug, bounds, base_variables)
        )
        n_constraints = len(constraints)

        variables = dict(base_variables)
        for slug, bounds in constraints.items():
            if "minimum" in bounds:
                variables[f"{slug}_min"] = bounds["minimum"]
            if "maximum" in bounds:
                variables[f"{slug}_max"] = bounds["maximum"]

        fom, fom_error = None, None
        formula = profile.get("figure_of_merit")
        if formula:
            try:
                fom = safe_eval(formula, variables)
            except Exception as exc:
                fom_error = str(exc)

        results.append({
            "profile": name,
            "description": profile.get("description", ""),
            "constraints": constraints,
            "n_satisfied": n_satisfied,
            "n_constraints": n_constraints,
            "matched": n_satisfied == n_constraints,
            "fom": fom,
            "fom_error": fom_error,
        })
    return results
