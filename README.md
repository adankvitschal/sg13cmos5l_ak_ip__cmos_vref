# sg13g2_mh_ip__cmos_vref

Analog IP for the IHP **SG13G2** (130nm SiGe BiCMOS) open PDK, designed and
simulated through the [mh-analog-designer](https://gitlab.kvitschal.dev/adankvitschal/mh-analog-designer)
tool: schematic capture in xschem, simulation via ngspice or Xyce, and a
`config.json`-driven pipeline for generating/exploring parameter variations,
scoring them against named design profiles, and training surrogate models.

## Blocks

| Block | Topologies | Profiles | What it is |
| --- | --- | --- | --- |
| `cmos_vref` | `default`, `lvfet` | `low_power`, `high_performance` | Self-biased CMOS voltage reference: PTAT current mirror compensating the FET V_TH's CTAT behavior. `lvfet` swaps the vptat cascode (M1/M2) for low-voltage NMOS. |
| `output_amp` | `default` | `low_power` | Two-stage Miller-compensated op-amp (NMOS diff pair + cascode, active PMOS mirror load, CS PMOS output driver) — unity-feedback DC buffer for `cmos_vref`. |
| `top` | `default` | `bias_matched`, `low_power` | `cmos_vref` + `output_amp` + digital trim/enable, integrated as one hierarchical block. |

Each topology's tests, metrics and pass/fail-relevant design profiles are
declared in [`config.json`](config.json). There is no absolute per-test
spec anymore — a profile's own `constraints` (and its figure-of-merit
formula) are what actually judge a variation.

## Toolchain

- **xschem** — schematic capture/netlisting.
- **ngspice** and **Xyce** — simulation (per-test, declared in `config.json`).
- **IHP SG13G2** open PDK (models, standard cells).
- Everything above runs inside a docker container managed by
  mh-analog-designer's `run_sim.py` — nothing needs installing locally
  beyond docker and Python.

## Layout

| Dir | Contents |
| --- | --- |
| `config.json` | Blocks, topologies, tests, profiles — the single source of truth the whole pipeline reads. |
| `sch/` | Topology schematics (`.sch`/`.sym`), one per block/topology. |
| `tb/` | Testbenches + their Python parsers (`tb/<block>/tb_*.py`, shared helpers in `tb/_shared/`). |
| `params/` | Declared parameter sets per block/topology. |
| `sim/` | Simulation output — netlists, raw data, plots, `results.jsonl`/`variations.jsonl`. Gitignored, fully regenerable. |
| `models/` | Trained surrogate models (mh-analog-designer "pro" feature). Gitignored. |
| `release/` | Exported snapshot (materialized schematics + a results writeup) for sharing a variation outside this pipeline — see [`release/README.md`](release/README.md). |

## Reproducing

With mh-analog-designer installed and docker running:

```
python -m analog_designer.sim.run_sim --project-root . --block cmos_vref
```

re-simulates whichever tests are stale for the default-parameter variation.
Or open the GUI for the full Create/Update/Generate/Train workflow:

```
python -m analog_designer.gui.app .
```
