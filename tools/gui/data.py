"""Read-only access to config.json, sim/variations.jsonl, sim/results.jsonl
and sim/<variation>/runs.jsonl. No Tkinter import, no side effects -- safe
to call from any panel or from a background thread."""
import json
from pathlib import Path

from tools import fom as fom_module

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _read_jsonl(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_variations():
    return _read_jsonl(PROJECT_ROOT / "sim" / "variations.jsonl")


def load_results():
    return _read_jsonl(PROJECT_ROOT / "sim" / "results.jsonl")


def load_runs(variation_name):
    return _read_jsonl(PROJECT_ROOT / "sim" / variation_name / "runs.jsonl")


def latest_results(results):
    """Collapse results.jsonl to one row per (variation, test, metric): keep
    only rows whose definition_hash matches the freshest hash seen for that
    (variation, test) -- results.jsonl can hold superseded rows from a
    previous test/schematic/parser definition -- then keep the most recent
    row per (variation, test, metric), since a fresh definition can still be
    re-run more than once (e.g. --force)."""
    freshest_hash = {}
    for row in results:
        key = (row["variation"], row["test"])
        if key not in freshest_hash or row["created"] > freshest_hash[key][0]:
            freshest_hash[key] = (row["created"], row["definition_hash"])

    latest_per_metric = {}
    for row in results:
        key = (row["variation"], row["test"])
        if row["definition_hash"] != freshest_hash[key][1]:
            continue
        metric_key = (row["variation"], row["test"], row["metric"])
        if metric_key not in latest_per_metric or row["created"] > latest_per_metric[metric_key]["created"]:
            latest_per_metric[metric_key] = row

    return list(latest_per_metric.values())


def plot_paths_for(variation, test):
    """[(label, Path), ...] for every plot PNG a parser generated for this
    (variation, test), sorted by filename. A file named exactly
    "{test}.png" gets the generic label "plot"; "{test}__<suffix>.png"
    gets <suffix> prettified (underscores -> spaces, title-cased) as its
    label -- lets a parser generate any number of named views (0, 1, or
    many) without the GUI needing to know in advance which ones exist."""
    test_dir = PROJECT_ROOT / "sim" / variation / test
    if not test_dir.exists():
        return []
    results = []
    for path in sorted(test_dir.glob(f"{test}*.png")):
        rest = path.stem[len(test):]
        label = rest[2:].replace("_", " ").title() if rest.startswith("__") else "plot"
        results.append((label, path))
    return results


def load_config():
    return json.loads((PROJECT_ROOT / "config.json").read_text(encoding="utf-8"))


def variation_summaries():
    """One row per variation, for the top-level table: identity fields from
    variations.jsonl, how many metrics have been measured, and its
    design-profile classification (per config.json blocks.<block>.profiles),
    computed on demand from its latest metrics -- nothing about it is
    stored on disk."""
    variations = load_variations()
    metrics_by_variation = {}
    for row in latest_results(load_results()):
        metrics_by_variation.setdefault(row["variation"], []).append(row)
    config = load_config()

    summaries = []
    for variation in variations:
        rows = metrics_by_variation.get(variation["name"], [])
        block_cfg = config.get("blocks", {}).get(variation["block"], {})
        profiles = fom_module.classify(block_cfg, rows)
        primary_profile = next((p for p in profiles if p["matched"]), None)
        summaries.append({
            "variation": variation["name"],
            "block": variation["block"],
            "topology": variation["topology"],
            "n_total": len(rows),
            "profiles": profiles,
            "primary_profile": primary_profile,
            "metrics_by_description": {r["metric"]: r["value"] for r in rows},
            "created": variation["created"],
        })
    return summaries


def metric_options():
    """Sorted {"description", "unit"} for every distinct metric currently
    in results.jsonl -- for populating the morphospace X/Y dropdowns with
    human-readable labels (slugs stay internal to tools/fom.py)."""
    seen = {}
    for row in latest_results(load_results()):
        seen.setdefault(row["metric"], row.get("unit", ""))
    return [{"description": d, "unit": u} for d, u in sorted(seen.items())]
