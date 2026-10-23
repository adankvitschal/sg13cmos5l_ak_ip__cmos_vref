# Release

One chosen variation per block, exported for review. Schematics: [release/xschem/sch/](xschem/sch/) (requires the ihp-sg13cmos5l-pr1241-pins open-source PDK's xschem device library on XSCHEM_LIBRARY_PATH to render component symbols). Layout GDS, one self-contained file per block: [release/layout/](layout/). LVS evidence -- netgen's own report, both netlists it compared, and a run_lvs.sh that re-runs the comparison with netgen alone: [release/lvs/](lvs/).

| Block | Variation | Exported | Layout | LVS |
|---|---|---|---|---|
| [cmos_vref](doc/cmos_vref/README.md) | `cmos_vref-default-5f7415` | 2026-10-23T07:06:42 | published | mismatch |
| [output_amp](doc/output_amp/README.md) | `output_amp-default-be0d58` | 2026-10-23T07:06:42 | published | clean |
| [top](doc/top/README.md) | `top-default-5997f5` | 2026-10-23T07:06:41 | published | mismatch |
