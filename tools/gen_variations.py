#!/usr/bin/env python3
"""Generate N random cmos_vref/default variations -- each of the 21
parameters independently sampled uniformly between its config.json min/max
-- and simulate each one through tools/run_sim.py's existing per-variation
pipeline (materialize -> netlist -> simulate -> parse -> store).

Sequential, one variation fully simulated before the next starts:
sch/cmos_vref.sch (the materialized schematic) and sim/results.jsonl are
shared single-writer state, same assumption tools/run_sim.py's own CLI
already makes.

Usage (from the repo root): python -m tools.gen_variations N [--force] [--seed SEED]
"""
import argparse
import json
import random
import re
import sys

from tools.run_sim import BLOCK, PROJECT_ROOT, TOPOLOGY, run_variation, setup_container

_SUFFIX_MULT = {
    "f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3,
    "k": 1e3, "meg": 1e6, "g": 1e9, "t": 1e12,
}
_VALUE_RE = re.compile(r"^([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s*([a-zA-Z]*)$")


def _match(text):
    m = _VALUE_RE.match(text.strip())
    if not m:
        raise ValueError(f"cannot parse SPICE value: {text!r}")
    return m.groups()


def parse_spice_value(text):
    number, suffix = _match(text)
    suffix = suffix.lower()
    if suffix == "":
        return float(number)
    if suffix not in _SUFFIX_MULT:
        raise ValueError(f"unknown SPICE suffix in {text!r}: {suffix!r}")
    return float(number) * _SUFFIX_MULT[suffix]


def format_spice_value(base_value, unit_suffix):
    suffix = unit_suffix.lower()
    mult = 1.0 if suffix == "" else _SUFFIX_MULT[suffix]
    return f"{base_value / mult:.4g}{unit_suffix}"


def random_params(param_defs, rng):
    """One parameter set: each parameter independently sampled uniform(min,
    max), rendered back with the same unit suffix as its config.json
    default (min/max can use a different suffix, e.g. min='500n' next to
    default='1u' -- parse_spice_value handles that, format_spice_value
    keeps the rendered value in the default's units for readability)."""
    params = {}
    for name, pdef in param_defs.items():
        lo = parse_spice_value(pdef["min"])
        hi = parse_spice_value(pdef["max"])
        _, default_suffix = _match(pdef["default"])
        params[name] = format_spice_value(rng.uniform(lo, hi), default_suffix)
    return params


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("count", type=int, help="number of random variations to generate and simulate")
    parser.add_argument(
        "--force", action="store_true",
        help="re-run a generated variation's tests even if (by hash coincidence) a fresh result already exists",
    )
    parser.add_argument("--seed", type=int, default=None, help="random seed, for reproducible batches")
    args = parser.parse_args()

    config = json.loads((PROJECT_ROOT / "config.json").read_text(encoding="utf-8"))
    defaults = config["defaults"]
    block_cfg = config["blocks"][BLOCK]["topologies"][TOPOLOGY]
    tests = config["tests"][BLOCK]
    rng = random.Random(args.seed)

    container_ctx = setup_container()

    any_error = False
    for i in range(args.count):
        params = random_params(block_cfg["parameters"], rng)
        print(f"\n=== variation {i + 1}/{args.count} ===")
        outcome = run_variation(
            block_cfg, tests, defaults, params, force=args.force, container_ctx=container_ctx,
        )
        any_error = any_error or outcome["any_error"]

    sys.exit(1 if any_error else 0)


if __name__ == "__main__":
    main()
