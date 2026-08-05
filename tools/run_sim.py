#!/usr/bin/env python3
"""Materialize cmos_vref/default with its config.json default parameters and
run every test declared under config.json["tests"]["cmos_vref"] through
xschem + ngspice inside the EDA docker container.

Three separate logs, different granularity, don't confuse them:
  sim/variations.jsonl        - identity registry. One line per unique
      (block, topology, parameters) tuple, written once, never duplicated.
  sim/<variation>/runs.jsonl  - raw execution history for that variation.
      One line per (test, condition) simulation attempt. Expected to grow
      every time you run something, including reruns. Kept per-variation
      (not global) so parallel execution across variations -- the plan for
      large parameter sweeps -- never contends writing to the same file.
  sim/results.jsonl           - final answer table. One line per
      (variation, test, metric), tagged with a definition_hash so a stale
      result (test/schematic/parser changed since it was computed) is
      detectable without needing git.

Phase "default" only: fixed block=cmos_vref, topology=default, parameter
values = config.json defaults. No sweeps, no CLI-selectable topology yet
(that's the "genparams" phase).
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONTAINER_IMAGE = "eda-env-designer:ihp-sg13g2"
# The container mounts the host's project directories under /home/moduhub/work/<name>,
# same name as the host folder. Adjust here if the container's mount layout changes.
CONTAINER_PROJECT_ROOT = f"/home/moduhub/work/{PROJECT_ROOT.name}"

BLOCK = "cmos_vref"
TOPOLOGY = "default"

PARAM_TOKEN_RE = re.compile(r"'([A-Za-z_][A-Za-z0-9_]*)'")

# Maps a config.json conditions[] key to the tb parameter name prefix a
# testbench uses for sweeping it internally in one ngspice run (e.g.
# `dc TEMP 'temp_min' 'temp_max' 5`) instead of it being a separate
# per-run condition. 'temperature' predates this table and kept its
# historical 'temp' prefix; any other key defaults to itself as the
# prefix (see internal_sweep_axis()).
INTERNAL_SWEEP_AXES = {"temperature": "temp"}


def internal_sweep_axis(test_cfg, tb_text):
    """(conditions_key, tb_param_prefix) for the axis this testbench
    sweeps internally via its own ngspice .dc directive -- one run then
    covers the whole conditions[] list for that key, so it's excluded
    from the outer per-run condition grid. Detected by an actual
    '<prefix>_min'/'<prefix>_max' parameter pair in the schematic's
    stimuli code, not just by the key's presence in conditions{}, so a
    conditions entry that ISN'T swept internally (e.g. a fixed vdd value)
    still gets treated as a plain fixed default. None if this testbench
    doesn't sweep anything internally."""
    for key in test_cfg.get("conditions", {}):
        prefix = INTERNAL_SWEEP_AXES.get(key, key)
        if f"'{prefix}_min'" in tb_text and f"'{prefix}_max'" in tb_text:
            return key, prefix
    return None


# conditions{} keys already covered elsewhere (global defaults or the
# internal-sweep-axis machinery), so fixed_tb_params() never re-derives them.
_NON_FIXED_CONDITION_KEYS = {"corner", "temperature", "vdd", "Cload", "Rload"}


def fixed_tb_params(test_cfg, tb_text, sweep_axis):
    """Fixed (non-swept) testbench parameters pulled straight from this
    test's own conditions{} -- e.g. a PSRR testbench's single-point
    'frequency'. Only keys whose exact '<key>' token appears in the
    testbench text are pulled, and only when conditions[key] holds exactly
    one value (a list there would mean it's meant to vary, which only the
    internal-sweep-axis mechanism or corner/temperature support)."""
    skip = set(_NON_FIXED_CONDITION_KEYS)
    if sweep_axis:
        skip.add(sweep_axis[0])
    params = {}
    for key, values in test_cfg.get("conditions", {}).items():
        if key in skip or f"'{key}'" not in tb_text:
            continue
        if len(values) != 1:
            sys.exit(f"conditions.{key} must have exactly one value for a fixed testbench parameter, got {values}")
        params[key] = values[0]
    return params


def find_container():
    out = subprocess.run(
        ["docker", "ps", "--filter", f"ancestor={CONTAINER_IMAGE}", "--format", "{{.Names}}"],
        capture_output=True, text=True, check=True,
    )
    names = [n for n in out.stdout.splitlines() if n.strip()]
    if not names:
        sys.exit(f"No running container found for image {CONTAINER_IMAGE}")
    return names[0]


def docker_exec(container, script, timeout=120):
    return subprocess.run(
        ["docker", "exec", container, "bash", "-lc", script],
        capture_output=True, text=True, timeout=timeout,
    )


def get_pdk_dir(container, subpath):
    result = docker_exec(container, f'echo "$PDK_ROOT/$PDK/{subpath}"')
    path = result.stdout.strip()
    if result.returncode != 0 or not path:
        sys.exit(f"Could not resolve PDK path {subpath}:\n{result.stderr}")
    return path


def ensure_xschemrc(container):
    rc_path = PROJECT_ROOT / "xschemrc"
    if rc_path.exists():
        return
    result = docker_exec(container, 'cat "$PDK_ROOT/$PDK/libs.tech/xschem/xschemrc"')
    if result.returncode != 0 or not result.stdout.strip():
        sys.exit(f"Could not fetch default xschemrc from container:\n{result.stderr}")
    rc_path.write_text(result.stdout)
    print(f"created {rc_path}")


def substitute_params(text, params):
    for name, value in params.items():
        text = text.replace(f"'{name}'", str(value))
    return text


def check_unresolved(text, label):
    leftover = sorted(set(PARAM_TOKEN_RE.findall(text)))
    if leftover:
        sys.exit(
            f"{label}: unresolved parameter placeholder(s) left after substitution: "
            f"{', '.join(leftover)} -- add them to config.json or check the schematic."
        )


def variation_name(block, topology, params):
    digest = hashlib.sha1(json.dumps(params, sort_keys=True).encode()).hexdigest()[:6]
    return f"{block}-{topology}-{digest}"


def _read_jsonl(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _append_jsonl(path, row):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def ensure_variation_registered(name, block, topology, params):
    """sim/variations.jsonl is an identity registry, not a run log: write
    once per unique (block, topology, parameters), never duplicate."""
    path = PROJECT_ROOT / "sim" / "variations.jsonl"
    if any(r["name"] == name for r in _read_jsonl(path)):
        return
    _append_jsonl(path, {
        "name": name,
        "block": block,
        "topology": topology,
        "parameters": params,
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
    })


def append_run(variation, test_name, label, conditions, outcome):
    """sim/<variation>/runs.jsonl: raw execution history, one line per
    simulation attempt. Per-variation (not a single global file) so
    parallel workers running different variations never write to the same
    file."""
    _append_jsonl(PROJECT_ROOT / "sim" / variation / "runs.jsonl", {
        "variation": variation,
        "test": test_name,
        "condition": label,
        "conditions": conditions,
        "status": outcome["status"],
        "ngspice_exit_code": outcome.get("ngspice_exit_code"),
        "error": outcome.get("error"),
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
    })


def compute_definition_hash(block_cfg, test_cfg):
    """Hash of everything that defines HOW this test is run and measured --
    independent of which parameter VALUES were simulated (that's the
    variation hash). Changes when: the test's own config.json subtree
    changes, the testbench .sch changes, the parser .py (or its _common.py)
    changes, or the topology .sch template changes (catches structural
    schematic edits, like a body-tie fix, that don't touch any parameter
    value but do change what gets simulated)."""
    parts = [json.dumps(test_cfg, sort_keys=True)]
    topology_sch = PROJECT_ROOT / "sch" / block_cfg["schematic"]
    parts.append(topology_sch.read_text(encoding="utf-8"))
    parts.append((PROJECT_ROOT / test_cfg["testbench"]).read_text(encoding="utf-8"))
    parser_path = PROJECT_ROOT / test_cfg["parser"]
    parts.append(parser_path.read_text(encoding="utf-8"))
    common_path = parser_path.parent / "_common.py"
    if common_path.exists():
        parts.append(common_path.read_text(encoding="utf-8"))
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:12]


def git_info():
    """Informational only -- NOT the staleness mechanism (that's
    definition_hash, which works with or without git). Returns
    (commit_hash_or_None, dirty_bool_or_None)."""
    commit = subprocess.run(
        ["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"],
        capture_output=True, text=True,
    )
    if commit.returncode != 0:
        return None, None
    status = subprocess.run(
        ["git", "-C", str(PROJECT_ROOT), "status", "--porcelain"],
        capture_output=True, text=True,
    )
    return commit.stdout.strip(), bool(status.stdout.strip())


def load_results():
    return _read_jsonl(PROJECT_ROOT / "sim" / "results.jsonl")


def is_test_fresh(results, name, test_name, definition_hash):
    return any(
        r["variation"] == name and r["test"] == test_name and r["definition_hash"] == definition_hash
        for r in results
    )


def append_results(name, block, topology, test_name, definition_hash, metrics, git_commit, git_dirty):
    path = PROJECT_ROOT / "sim" / "results.jsonl"
    created = datetime.datetime.now().isoformat(timespec="seconds")
    for metric in metrics:
        _append_jsonl(path, {
            "variation": name,
            "block": block,
            "topology": topology,
            "test": test_name,
            "metric": metric["name"],
            "value": metric["value"],
            "unit": metric.get("unit"),
            "minimum": metric.get("minimum"),
            "maximum": metric.get("maximum"),
            "pass": metric.get("pass"),
            "definition_hash": definition_hash,
            "git_commit": git_commit,
            "git_dirty": git_dirty,
            "created": created,
        })


def load_parser(relpath):
    module_path = PROJECT_ROOT / relpath
    module_dir = str(module_path.parent)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MOS_CORNER_SECTION = {"tt": "mos_tt", "ss": "mos_ss", "ff": "mos_ff"}


def condition_matrix(test_cfg, defaults, sweep_axis):
    """Cartesian product of the conditions this test needs a separate run
    for. sweep_axis, if given as (conditions_key, tb_param_prefix) from
    internal_sweep_axis(), names the axis this testbench already sweeps
    internally in one ngspice run -- when that axis is 'temperature' it's
    excluded from this outer grid (only corner varies per run); any other
    internally-swept axis doesn't affect this grid, since corner x
    temperature is the only outer combination currently supported."""
    conditions = test_cfg.get("conditions", {})
    corners = conditions.get("corner", [defaults["corner"]])
    if sweep_axis and sweep_axis[0] == "temperature":
        for corner in corners:
            yield {"corner": corner}
    else:
        temperatures = conditions.get("temperature", [defaults["temperature"]])
        for corner in corners:
            for temperature in temperatures:
                yield {"corner": corner, "temperature": temperature}


def condition_label(conditions):
    return "_".join(f"{k}-{v}" for k, v in conditions.items())


def run_one_ngspice(container, test_name, tb_source, conditions, tb_params_base,
                     run_dir, container_run_dir, container_rcfile, spiceinit_text):
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / ".spiceinit").write_text(spiceinit_text, encoding="utf-8")

    tb_params = dict(tb_params_base)
    tb_params["mos_corner"] = MOS_CORNER_SECTION[conditions["corner"]]
    if "temperature" in conditions:
        tb_params["temperature"] = conditions["temperature"]
    tb_params["simpath"] = container_run_dir

    tb_text = substitute_params(tb_source.read_text(encoding="utf-8"), tb_params)
    check_unresolved(tb_text, f"{test_name} {condition_label(conditions)} ({tb_source.name})")
    (run_dir / tb_source.name).write_text(tb_text, encoding="utf-8")

    netlist_cmd = (
        f'export DISPLAY=:1; '
        f'/usr/local/share/xschem/bin/xschem --rcfile "{container_rcfile}" '
        f'-n -x -q -o "{container_run_dir}" "{container_run_dir}/{tb_source.name}"'
    )
    result = docker_exec(container, netlist_cmd)
    netlist_path = run_dir / f"{tb_source.stem}.spice"
    if not netlist_path.exists():
        return {"status": "error", "error": f"netlist failed, no .spice produced.\n{result.stdout}\n{result.stderr}"}
    netlist_text = netlist_path.read_text(encoding="utf-8")
    if "IS MISSING" in netlist_text:
        missing = [l for l in netlist_text.splitlines() if "IS MISSING" in l]
        return {"status": "error", "error": "netlist has unresolved symbols:\n" + "\n".join(missing)}

    sim_cmd = f'cd "{container_run_dir}" && ngspice -b {tb_source.stem}.spice'
    sim_result = docker_exec(container, sim_cmd, timeout=300)
    (run_dir / "ngspice.log").write_text(sim_result.stdout + "\n" + sim_result.stderr, encoding="utf-8")
    data_file = run_dir / f"{test_name}_0.data"
    if sim_result.returncode != 0 or not data_file.exists():
        return {
            "status": "error",
            "ngspice_exit_code": sim_result.returncode,
            "error": (sim_result.stdout + "\n" + sim_result.stderr)[-2000:],
        }
    return {"status": "success", "ngspice_exit_code": sim_result.returncode, "data_file": data_file}


SIMULATOR_RUNNERS = {"ngspice": run_one_ngspice}


def run_test(container, variation, test_name, test_cfg, defaults, models_dir,
             sim_dir, container_sim_dir, container_rcfile, spiceinit_text):
    simulator = test_cfg.get("simulator", "ngspice")
    runner = SIMULATOR_RUNNERS.get(simulator)
    if runner is None:
        sys.exit(
            f"{test_name}: simulator {simulator!r} is not implemented "
            f"(available: {sorted(SIMULATOR_RUNNERS)})"
        )

    tb_source = PROJECT_ROOT / test_cfg["testbench"]
    tb_text = tb_source.read_text(encoding="utf-8")
    sweep_axis = internal_sweep_axis(test_cfg, tb_text)

    tb_params_base = {
        "Vavdd": defaults["vdd"],
        "temperature": defaults["temperature"],
        "Cload": defaults["Cload"],
        "Rload": defaults["Rload"],
        "filename": test_name,
        "N": "0",
        "models_dir": models_dir,
    }
    if sweep_axis:
        key, prefix = sweep_axis
        values = [float(v) for v in test_cfg.get("conditions", {}).get(key, [])]
        if not values:
            sys.exit(f"{test_name}: testbench sweeps '{prefix}' internally but config.json has no conditions.{key} list")
        tb_params_base[f"{prefix}_min"] = min(values)
        tb_params_base[f"{prefix}_max"] = max(values)
    tb_params_base.update(fixed_tb_params(test_cfg, tb_text, sweep_axis))

    test_dir = sim_dir / test_name
    runs = []
    n_conditions = 0
    n_ok = 0
    for conditions in condition_matrix(test_cfg, defaults, sweep_axis):
        label = condition_label(conditions)
        run_dir = test_dir / label
        outcome = runner(
            container, test_name, tb_source, conditions, tb_params_base,
            run_dir, f"{container_sim_dir}/{test_name}/{label}", container_rcfile, spiceinit_text,
        )
        append_run(variation, test_name, label, conditions, outcome)
        n_conditions += 1
        if outcome["status"] != "success":
            continue
        n_ok += 1
        parser_module = load_parser(test_cfg["parser"])
        raw = parser_module.extract(outcome["data_file"])
        runs.append({"conditions": conditions, **raw})

    if not runs:
        return {"status": "error", "error": f"every condition failed to simulate, see sim/{variation}/runs.jsonl"}

    parser_module = load_parser(test_cfg["parser"])
    # a stale plot (or set of plots, under a since-changed naming convention)
    # from a previous run shouldn't look current
    for stale in test_dir.glob(f"{test_name}*.png"):
        stale.unlink()
    plot_base = test_dir / test_name
    outcome = parser_module.evaluate(runs, test_cfg["outputs"], plot_base=plot_base)
    return {
        "status": "success" if n_ok == n_conditions else "partial",
        "result": outcome,
    }


def print_metrics(test_name, metrics, note=""):
    flag = "PASS" if all(m["pass"] for m in metrics) else "FAIL"
    print(f"  {test_name}: {flag}{note}")
    for m in metrics:
        print(f"    {m['name']}: {m['value']} {m.get('unit', '')} ({'PASS' if m['pass'] else 'FAIL'})")


def setup_container():
    """One-time container discovery + PDK path resolution. Reusable across
    however many variations get simulated in this process (see
    tools/gen_variations.py, which calls this once for a whole batch instead
    of once per variation)."""
    container = find_container()
    ensure_xschemrc(container)
    models_dir = get_pdk_dir(container, "libs.tech/ngspice/models")
    osdi_dir = get_pdk_dir(container, "libs.tech/ngspice/osdi")
    spiceinit_text = "\n".join([
        f"osdi {osdi_dir}/psp103.osdi",
        f"osdi {osdi_dir}/psp103_nqs.osdi",
        "",
    ])
    return container, models_dir, spiceinit_text


def run_variation(block_cfg, tests, defaults, params, force=False, container_ctx=None):
    """Materialize + simulate one (BLOCK, TOPOLOGY, params) variation:
    registers it in variations.jsonl, skips whichever tests already have a
    fresh result in results.jsonl (unless force), runs the rest and appends
    their metrics. container_ctx is an optional pre-resolved
    (container, models_dir, spiceinit_text) tuple from setup_container() --
    if omitted, resolved lazily here, and NOT resolved at all when every
    test is already fresh (so a `run_sim.py` invocation with nothing new to
    simulate never has to touch docker). Returns
    {"variation": name, "any_error": bool}."""
    name = variation_name(BLOCK, TOPOLOGY, params)
    ensure_variation_registered(name, BLOCK, TOPOLOGY, params)

    existing_results = load_results()
    definition_hashes = {t: compute_definition_hash(block_cfg, cfg) for t, cfg in tests.items()}
    fresh = {
        t for t in tests
        if not force and is_test_fresh(existing_results, name, t, definition_hashes[t])
    }
    to_run = {t: cfg for t, cfg in tests.items() if t not in fresh}

    print(f"variation: {name}")
    any_error = False

    for test_name in sorted(fresh):
        rows = [
            r for r in existing_results
            if r["variation"] == name and r["test"] == test_name
            and r["definition_hash"] == definition_hashes[test_name]
        ]
        print_metrics(test_name, [
            {"name": r["metric"], "value": r["value"], "unit": r["unit"], "pass": r["pass"]}
            for r in rows
        ], note=" (SKIPPED, fresh result already in sim/results.jsonl)")

    if not to_run:
        return {"variation": name, "any_error": any_error}

    container, models_dir, spiceinit_text = container_ctx or setup_container()

    # materialize the chosen topology into sch/cmos_vref.sch (co-located with cmos_vref.sym)
    topology_sch = PROJECT_ROOT / "sch" / block_cfg["schematic"]
    materialized = substitute_params(topology_sch.read_text(encoding="utf-8"), params)
    check_unresolved(materialized, "cmos_vref.sch")
    (PROJECT_ROOT / "sch" / "cmos_vref.sch").write_text(materialized, encoding="utf-8")

    sim_dir = PROJECT_ROOT / "sim" / name
    sim_dir.mkdir(parents=True, exist_ok=True)
    container_sim_dir = f"{CONTAINER_PROJECT_ROOT}/sim/{name}"
    container_rcfile = f"{CONTAINER_PROJECT_ROOT}/xschemrc"

    git_commit, git_dirty = git_info()
    for test_name, test_cfg in to_run.items():
        tb_text = (PROJECT_ROOT / test_cfg["testbench"]).read_text(encoding="utf-8")
        n_conditions = len(list(condition_matrix(
            test_cfg, defaults, internal_sweep_axis(test_cfg, tb_text),
        )))
        print(f"running {test_name} ({test_cfg['testbench']}, {n_conditions} condition(s)) ...")
        result = run_test(
            container, name, test_name, test_cfg, defaults, models_dir,
            sim_dir, container_sim_dir, container_rcfile, spiceinit_text,
        )
        if result["status"] == "error":
            print(f"  {test_name}: ERROR ({result['error']})")
            any_error = True
            continue
        append_results(name, BLOCK, TOPOLOGY, test_name, definition_hashes[test_name], result["result"], git_commit, git_dirty)
        note = f" (some conditions failed to simulate, see sim/{name}/runs.jsonl)" if result["status"] == "partial" else ""
        print_metrics(test_name, result["result"], note)

    return {"variation": name, "any_error": any_error}


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument(
        "--force", action="store_true",
        help="re-run every test even if results.jsonl already has a fresh (matching definition_hash) result",
    )
    args = arg_parser.parse_args()

    config = json.loads((PROJECT_ROOT / "config.json").read_text(encoding="utf-8"))
    defaults = config["defaults"]
    block_cfg = config["blocks"][BLOCK]["topologies"][TOPOLOGY]
    params = {n: pdef["default"] for n, pdef in block_cfg["parameters"].items()}
    tests = config["tests"][BLOCK]

    outcome = run_variation(block_cfg, tests, defaults, params, force=args.force)
    if outcome["any_error"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
