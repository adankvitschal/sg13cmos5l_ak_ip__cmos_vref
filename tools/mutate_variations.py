#!/usr/bin/env python3
"""Generate new cmos_vref/default variations from an existing one, instead of
tools/gen_variations.py's independent full-range sampling:

  generate BASE N --pct PCT   -- N variations perturbing BASE's own 21
      parameter values by +/-PCT% each (percent of the parameter's current
      value, not of its configured range -- the usual analog "+/-X%
      mismatch" Monte Carlo convention), clipped to config.json's min/max.
  combine A B N --mode pick|average [--pct PCT]
      -- N variations from two parent variations: "pick" draws each of the
      21 parameters independently from one parent or the other; "average"
      takes the per-parameter mean of both parents and then applies the
      same +/-PCT% jitter as generate. Parameter correlation is ignored
      (no cross-parameter constraints exist in config.json -- the only two
      mechanically-coupled pairs, M6/M7 and M8/M9, are already collapsed
      into single shared parameters).

Each generated parameter set is simulated through tools/run_sim.py's
existing per-variation pipeline (materialize -> netlist -> simulate ->
parse -> store), same sequential single-writer assumption as
gen_variations.py (sch/cmos_vref.sch and sim/results.jsonl are shared
state).

Usage (from the repo root):
  python -m tools.mutate_variations generate BASE_VARIATION N --pct PCT [--force] [--seed SEED]
  python -m tools.mutate_variations combine VARIATION_A VARIATION_B N --mode pick|average [--pct PCT] [--force] [--seed SEED]
"""
import argparse
import json
import random
import sys

from tools.gen_variations import _match, format_spice_value, parse_spice_value
from tools.run_sim import BLOCK, PROJECT_ROOT, TOPOLOGY, _read_jsonl, run_variation, setup_container, variation_name


def _load_variation_params(name):
    for row in _read_jsonl(PROJECT_ROOT / "sim" / "variations.jsonl"):
        if row["name"] == name:
            return row["parameters"]
    sys.exit(f"no such variation in sim/variations.jsonl: {name!r}")


def _clip(value, pdef):
    lo = parse_spice_value(pdef["min"])
    hi = parse_spice_value(pdef["max"])
    return min(max(value, lo), hi)


def _render(value, pdef):
    _, default_suffix = _match(pdef["default"])
    return format_spice_value(value, default_suffix)


def perturb_params(base_params, param_defs, pct, rng):
    """base_params, each value scaled by (1 +/- pct/100), clipped to that
    parameter's configured [min, max]."""
    params = {}
    for name, pdef in param_defs.items():
        base = parse_spice_value(base_params[name])
        value = base * (1 + rng.uniform(-pct, pct) / 100)
        params[name] = _render(_clip(value, pdef), pdef)
    return params


def combine_params(params_a, params_b, param_defs, mode, pct, rng):
    """Per parameter, either pick one parent's value outright ("pick") or
    average both parents and apply the same +/-pct% jitter perturb_params
    uses ("average"). Both clipped to [min, max]."""
    params = {}
    for name, pdef in param_defs.items():
        a = parse_spice_value(params_a[name])
        b = parse_spice_value(params_b[name])
        if mode == "pick":
            value = rng.choice([a, b])
        else:
            value = (a + b) / 2 * (1 + rng.uniform(-pct, pct) / 100)
        params[name] = _render(_clip(value, pdef), pdef)
    return params


def _run_batch(param_sets, block_cfg, tests, defaults, force):
    container_ctx = setup_container()
    any_error = False
    existing_names = {r["name"] for r in _read_jsonl(PROJECT_ROOT / "sim" / "variations.jsonl")}
    for i, params in enumerate(param_sets):
        name = variation_name(BLOCK, TOPOLOGY, params)
        if name in existing_names:
            print(f"\n=== variation {i + 1}/{len(param_sets)}: {name} already exists, re-checking freshness ===")
        else:
            print(f"\n=== variation {i + 1}/{len(param_sets)} ===")
        outcome = run_variation(block_cfg, tests, defaults, params, force=force, container_ctx=container_ctx)
        existing_names.add(outcome["variation"])
        any_error = any_error or outcome["any_error"]
    return any_error


def cmd_generate(args, config):
    block_cfg = config["blocks"][BLOCK]["topologies"][TOPOLOGY]
    defaults = config["defaults"]
    tests = config["tests"][BLOCK]
    rng = random.Random(args.seed)

    base_params = _load_variation_params(args.base)
    param_sets = [
        perturb_params(base_params, block_cfg["parameters"], args.pct, rng)
        for _ in range(args.count)
    ]
    any_error = _run_batch(param_sets, block_cfg, tests, defaults, args.force)
    sys.exit(1 if any_error else 0)


def cmd_combine(args, config):
    block_cfg = config["blocks"][BLOCK]["topologies"][TOPOLOGY]
    defaults = config["defaults"]
    tests = config["tests"][BLOCK]
    rng = random.Random(args.seed)

    params_a = _load_variation_params(args.variation_a)
    params_b = _load_variation_params(args.variation_b)
    param_sets = [
        combine_params(params_a, params_b, block_cfg["parameters"], args.mode, args.pct, rng)
        for _ in range(args.count)
    ]
    any_error = _run_batch(param_sets, block_cfg, tests, defaults, args.force)
    sys.exit(1 if any_error else 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen = subparsers.add_parser("generate", help="perturb a base variation's parameters by +/-pct%% each")
    gen.add_argument("base", help="name of the base variation (from sim/variations.jsonl)")
    gen.add_argument("count", type=int, help="number of variations to generate and simulate")
    gen.add_argument("--pct", type=float, required=True, help="+/- percent to perturb each parameter's value by")
    gen.add_argument("--force", action="store_true", help="re-run tests even if a fresh result already exists")
    gen.add_argument("--seed", type=int, default=None, help="random seed, for reproducible batches")
    gen.set_defaults(func=cmd_generate)

    comb = subparsers.add_parser("combine", help="combine two parent variations' parameters")
    comb.add_argument("variation_a", help="name of parent A")
    comb.add_argument("variation_b", help="name of parent B")
    comb.add_argument("count", type=int, help="number of variations to generate and simulate")
    comb.add_argument("--mode", choices=["pick", "average"], required=True)
    comb.add_argument(
        "--pct", type=float, default=0.0,
        help="mode=average only: +/- percent jitter applied to each parameter's parent-average",
    )
    comb.add_argument("--force", action="store_true", help="re-run tests even if a fresh result already exists")
    comb.add_argument("--seed", type=int, default=None, help="random seed, for reproducible batches")
    comb.set_defaults(func=cmd_combine)

    args = parser.parse_args()
    if args.command == "combine" and args.mode == "average" and args.pct == 0.0:
        print("note: --mode average with --pct 0 produces the exact parent-average, no jitter", file=sys.stderr)

    config = json.loads((PROJECT_ROOT / "config.json").read_text(encoding="utf-8"))
    args.func(args, config)


if __name__ == "__main__":
    main()
