# top — default

**Variation ID:** `top-default-8d8c0c`  
**Exported:** 2026-08-31T14:52:56

Vref core + output buffer amp integration: cmos_vref (X1) generates vref/pbias/vbg*, output_amp (x2) buffers it, plus a PMOS bias mirror (M1, sized off cmos_vref's own M3), an enable switch (M2), and trim resistors/switches (R1-R8/M6-M9).

**Sub-block dependencies:** X1 (cmos_vref): `cmos_vref-default-d813dd`, x2 (output_amp): `output_amp-default-6a5d00` — their materialized schematics (and, for a real registered variation, their own release/doc/ page) are kept in sync with these exact choices every time this block is exported.

## Parameters

| Parameter | Value | Description |
|---|---|---|
| X1_variation | cmos_vref-default-d813dd | Which cmos_vref/default variation composes X1 in this top variation -- a real registered variation name, or the reserved value "defaults" (cmos_vref/default's own config.json defaults, no variation needs to be registered first). |
| x2_variation | output_amp-default-6a5d00 | Which output_amp/default variation composes x2 in this top variation -- same convention as X1_variation. |
| ena_length | 0.45u | Channel Length of M2 (PMOS enable switch, avdd18 -> the vref core's own supply). The sky130_ak_ip__cmos_vref sibling project's equivalent (M20) uses L=0.3u, but that's below this PDK's own sg13_hv_pmos minimum (see cmos_vref's own pbias_length/m2_length, both min=0.40-0.45u) -- clamped up to 0.45u, the smallest value actually valid for this device on this PDK. |
| ena_width | 10u | Channel Width of M2 (PMOS enable switch). Matches the sky130_ak_ip__cmos_vref sibling project's equivalent (M20, W=10u). |
| trim_switch_length | 2u | Channel Length of the M6-M9 trim network switches (NMOS, gate driven by trim0-trim3 via a sg13g2_buf_1 buffer). Matches the sky130_ak_ip__cmos_vref sibling project's equivalent (trim_res.sch's M1-M4, L=2u). |
| trim_switch_width | 10u | Channel Width of the M6-M9 trim network switches. Matches the sky130_ak_ip__cmos_vref sibling project's equivalent (trim_res.sch's M1-M4, W=10u). |
| base_width | 0.5u | Shared width of R1-R8 (the vbg/vbgtg/vbgsc feedback divider + its R5-R8 binary trim network, sch/top/top_default.sch). IHP's sg13g2 rhigh model doesn't document a fixed/DRC-mandated width the way sg13_hv_pmos/nmos do for length (see ena_length's own note) -- this is exposed as a free parameter rather than pinned, so if a real width-fixing design rule turns up later this can be clamped to it (min=max) without touching the resistor formulas themselves, which only ever reference 'base_width' symbolically. |
| rfeedback_total | 2Meg | Target sum of the whole R1..R8 series chain (vbg down to avss) -- the feedback network's total impedance around output_amp. Every resistor's length is a fixed or vref-dependent FRACTION of this single knob (see rbot_nominal below and the l= expressions in sch/top/top_default.sch), so raising it lowers the network's loading current 1:1 without touching the vbg/vbgtg/vbgsc voltage ratios. min=1Meg is a current-limit floor, not an arbitrary round number: output_amp's own config.json exposes no verified max-drive-current spec for its output stage (M10, a common-source PMOS driver biased at ~100nA quiescent -- the 80-120nA bias_matched profile constraint is that stage's OWN quiescent bias, not its large-signal drive capability), so 1.2uA was picked as a conservative, unverified placeholder for the most current the stage can source into this network before its output sags enough to miss vbg's 1200mV target -- in the same spirit as amp_bias_width's own flagged KNOWN LIMITATION, not a datasheet number. min=1Meg is exactly vbg_target/that placeholder (1.2V/1.2uA): lowering this min without re-deriving it from a real drive-current spec would silently let rfeedback_total draw more current than the amp is assumed able to source. |
| trim_factor | 0.1 | Fraction of rbot_nominal (see derived_parameters.cross_block below) given to the removable R5-R8 binary trim network (weights 1:2:4:8, matching M6-M9/trim0-3) instead of to the fixed floor R4. trim_factor=0 collapses R5-R8 to 0 ohm each (M6-M9 switching becomes a no-op, Rbot is permanently R4=rbot_nominal); trim_factor=1 collapses R4 to 0 ohm (every bit of Rbot is removable, down to a 0-ohm floor with all of trim0-3 asserted). All 4 switches open (trim0-3=0) always gives Rbot=rbot_nominal regardless of trim_factor, since R4+R5+R6+R7+R8 = rbot_nominal*((1-trim_factor)+trim_factor) by construction -- trim_factor only sets how much of that nominal value the 4-bit code can trim AWAY, not the untrimmed operating point itself. |
| amp_bias_width (ƒx) | 35.21u | M1's mirrored bias width, calculated (not free) -- scaled from cmos_vref's own m3_width so that M1's mirrored current (M1 and M3 share gate 'pbias', length 'pbias_length', and source rail -- a matched current mirror) is INTENDED to land on output_amp's 100nA design point, REGARDLESS of what m3_width the optimizer picks for cmos_vref's own, unrelated specs (Vref accuracy/TC/consumption) and regardless of which cmos_vref variation X1_variation selects. Replaces an earlier free 'amp_bias_factor' parameter (integer, 1-10) that could only scale the mirrored current UP relative to cmos_vref's own core current, never down. KNOWN LIMITATION (measured, not fixed): this is a single-shot, open-loop estimate -- cmos_vref's reference_current test measures M3 on a clean, directly-set 1.8V supply, but inside `top` the same core is fed through the M2 enable-switch PMOS, which drops tens of mV; combined with this mirror apparently running in weak/moderate inversion (VSG close to Vth), that supply difference alone was observed to cause a ~3x mismatch between the calculated target and the actual delivered current at the default parameter set (see tb/top's own amp_bias_current test, which measures the real thing and is expected to fail until this is revisited -- e.g. by hand-tuning `target` below against that test's own result, or by improving the calibration environment). Treat this as a best-effort starting point, not a guarantee. |
| pbias_length (ƒx) | 10u | X1.pbias_length |
| rbot_nominal (ƒx) | 1.299Meg | R4+R5+R6+R7+R8 combined (the 'de baixo' resistors, both electrically -- from the amp's own feedback tap down to avss -- and spatially, at the bottom of sch/top/top_default.sch), sized as rfeedback_total * (X1's own actual measured typical vref DC output / 1.2V). This is what makes the amp's non-inverting gain (vbg = vref_core * rfeedback_total/rbot_nominal) land on vbg=1200mV REGARDLESS of what vref_core voltage cmos_vref's own X1_variation actually produces, exactly like amp_bias_width already does for M1's mirrored current one row above -- 'invert': true is required here (unlike amp_bias_width) because rbot_nominal must grow WITH the measured vref_core (a bigger core voltage needs a bigger feedback fraction to reach the same 1200mV, i.e. measured/target), not shrink to correct for a metric that's already supposed to be near its target. Uses scale_to_target's 'stat': 'typical' (tt corner, sample closest to 25C -- see tb/cmos_vref/tb_vref_temp_sweep.py's evaluate() and tb/_shared/parser_common.typical_min_max()) rather than 'min'/'max', which are a range across the WHOLE temperature/corner sweep, not a single design-point reading -- sizing off either extreme would size the divider for a corner X1 isn't even necessarily run at. R1/R2/R3 (the 'de cima' resistors, splitting rfeedback_total-rbot_nominal to hit the vbgtg=1048mV/vbgsc=1024mV taps) and the R4 vs. R5-R8 trim split are pure arithmetic on rfeedback_total/rbot_nominal/trim_factor/base_width -- see derived_parameters.formulas below (r1_length..r8_length) -- the 1200/1048/1024mV targets themselves are fixed circuit constants baked into those formulas (0.1266667, 0.02, 0.8533333 = (1200-1048)/1200, (1048-1024)/1200, 1024/1200), not free parameters. |
| r1_length (ƒx) | 85.58u | R1's length (sch/top/top_default.sch, w='base_width'): inverts the rhigh model's own R(w,l) formula (value=expr_eng(...) on the symbol itself: R = 1.6e-4/w + 1360*l/(w-0.04e-6) at b=0,m=1) to hit a target R = 0.1266667*rfeedback_total ohm -- the fixed fraction of the total feedback chain between vbg (1200mV) and vbgtg (1048mV): (1200-1048)/1200. Independent of rbot_nominal/trim_factor -- this segment sits entirely above the amp's own feedback tap, so it never changes with X1's measured vref or the trim code. |
| r2_length (ƒx) | 13.42u | R2's length, same construction as r1_length, targeting R = 0.02*rfeedback_total ohm -- the vbgtg (1048mV) to vbgsc (1024mV) fraction: (1048-1024)/1200. |
| r3_length (ƒx) | 137.8u | R3's length, targeting R = 0.8533333*rfeedback_total - rbot_nominal ohm -- the vbgsc (1024mV) down to the amp's own feedback tap (which sits at X1's measured vref_core, NOT a fixed voltage): 1024/1200 of the total chain, minus whatever rbot_nominal already accounts for below that tap. This is the one 'de cima' resistor that depends on X1's measured vref (through rbot_nominal), since it bridges the gap between a FIXED tap voltage and the VARIABLE vref_core node. |
| r4_length (ƒx) | 395.3u | R4's length -- the fixed floor of the 'de baixo' network (M6-M9 all open still leaves R4 in circuit), targeting R = (1-trim_factor)*rbot_nominal ohm. Combined with r5_length..r8_length (which together add up to trim_factor*rbot_nominal, see each one's own description), R4+R5+R6+R7+R8 = rbot_nominal always, regardless of trim_factor -- trim_factor only decides the FIXED/removable split, not the untrimmed total. |
| r5_length (ƒx) | 2.821u | R5's length -- weight 1 of the 1:2:4:8 binary trim network (M6/trim0 shorts it out when asserted), targeting R = trim_factor*rbot_nominal/15 ohm (1 of the 1+2+4+8=15 total removable parts). |
| r6_length (ƒx) | 5.75u | R6's length -- weight 2 of the trim network (M7/trim1), targeting R = 2*trim_factor*rbot_nominal/15 ohm. |
| r7_length (ƒx) | 11.61u | R7's length -- weight 4 of the trim network (M8/trim2), targeting R = 4*trim_factor*rbot_nominal/15 ohm. |
| r8_length (ƒx) | 23.32u | R8's length -- weight 8 of the trim network (M9/trim3), targeting R = 8*trim_factor*rbot_nominal/15 ohm. |

## Design profile

Closest profile (not fully matched): **low_power** (1/5 constraints) — FOM: <1

| Profile | Score | FOM | Description |
|---|---|---|---|
| bias_matched | 0/1 | <1 | Output stage bias current lands close to the 100nA output_amp was verified against standalone |
| low_power | 1/5 | <1 | Notably lower current consumption (enabled and standby) than the Chipalooza #2 target spec requires, while still meeting the area/TC/PSRR targets (ihp_mh_ip__cmos_vref_proposal.pdf, Table 2) |

## Test results

| Test | Metric | Typical | Min | Max | Mean | Std | Unit | Spec | Pass |
|---|---|---|---|---|---|---|---|---|---|
| amp_bias_current | Output stage bias current | 940.5 | 90.6 | 1495 |  |  | nA | 80–120 nA |  |
| area | Estimated layout area | 7262 | 7262 | 7262 |  |  | µm² | ≤ 50000 µm² | PASS |
| current_consumption | Top current consumption | 1.363 | 0.8675 | 2.585 |  |  | uA |  | FAIL |
| psrr | PSRR @ 1kHz | 50.31 | 45.57 | 58.88 |  |  | dB | ≥ 50 dB | FAIL |
| standby_current | Standby current (disabled) | 1.496e+06 | 1.01e+06 | 3.695e+06 |  |  | pA | ≤ 750 pA | FAIL |
| temp_sweep | Temperature coefficient (commercial 0-70C) | 59.02 | 55.29 | 62.53 |  |  | ppm/°C |  |  |
| temp_sweep | Temperature coefficient (full -40-125C) | 102.5 | 99.63 | 104.1 |  |  | ppm/°C |  |  |
| temp_sweep | Temperature coefficient (industrial -40-85C) | 55 | 55 | 60.86 |  |  | ppm/°C |  | FAIL |
| temp_sweep | vbg output voltage | 1.2 | 1.112 | 1.267 |  |  | V |  |  |
| vbg_mismatch | vbg output voltage (mismatch) |  | 1.045 | 1.641 | 1.312 | 0.1847 | V |  |  |
| vbg_stat | vbg output voltage (stat) |  | 1.002 | 1.569 | 1.278 | 0.165 | V |  |  |

## Plots

### amp_bias_current — plot

![plot](plots/amp_bias_current.png)

### current_consumption — plot

![plot](plots/current_consumption.png)

### psrr — plot

![plot](plots/psrr.png)

### standby_current — plot

![plot](plots/standby_current.png)

### temp_sweep — All

![All](plots/temp_sweep__all.png)

### temp_sweep — Typical

![Typical](plots/temp_sweep__typical.png)

### temp_sweep — Worst

![Worst](plots/temp_sweep__worst.png)

### vbg_mismatch — plot

![plot](plots/vbg_mismatch.png)

### vbg_stat — plot

![plot](plots/vbg_stat.png)
