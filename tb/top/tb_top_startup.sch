v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
C {sch/top.sym} 0 0 0 0 {name=X1}
N -30 170 30 170 {lab=loop_bridge}
C {devices/gnd.sym} 0 140 0 0 {name=lsub lab=GND}
C {devices/lab_pin.sym} -130 -60 0 0 {name=l1 sig_type=std_logic lab=avdd18}
C {devices/gnd.sym} 120 -60 0 0 {name=l2 lab=GND}
C {devices/lab_pin.sym} -130 0 0 0 {name=l3 sig_type=std_logic lab=trim0_net}
C {devices/lab_pin.sym} 120 0 0 0 {name=l4 sig_type=std_logic lab=vbg}
C {devices/lab_pin.sym} -130 30 0 0 {name=l5 sig_type=std_logic lab=trim1_net}
C {devices/lab_pin.sym} -130 60 0 0 {name=l6 sig_type=std_logic lab=trim2_net}
C {devices/lab_pin.sym} -130 90 0 0 {name=l7 sig_type=std_logic lab=trim3_net}
C {devices/lab_pin.sym} -130 -90 0 0 {name=l8 sig_type=std_logic lab=dvdd}
C {devices/gnd.sym} 120 -90 0 0 {name=l9 lab=GND}
C {devices/lab_pin.sym} -130 -30 0 0 {name=l10 sig_type=std_logic lab=ena_net}
C {devices/vsource.sym} -250 -270 0 0 {name=Vavdd18 value="PWL(0 0 'ramp_time' 'avdd18')"}
C {devices/ammeter.sym} -250 -330 0 0 {name=Vmeas_ana savecurrent=true}
C {devices/vdd.sym} -250 -360 0 0 {name=l20 lab=avdd18}
C {devices/gnd.sym} -250 -240 0 0 {name=l22 lab=GND}
C {devices/vsource.sym} -350 -270 0 0 {name=Vdvdd value="dc 'dvdd'"}
C {devices/ammeter.sym} -350 -330 0 0 {name=Vmeas_dig savecurrent=true}
C {devices/vdd.sym} -350 -360 0 0 {name=l23 lab=dvdd}
C {devices/gnd.sym} -350 -240 0 0 {name=l25 lab=GND}
C {devices/vsource.sym} -450 -30 0 0 {name=Vena value="dc 'ena'"}
C {devices/vdd.sym} -450 -60 0 0 {name=l26 lab=ena_net}
C {devices/gnd.sym} -450 0 0 0 {name=l27 lab=GND}
C {devices/vsource.sym} -550 -30 0 0 {name=Vtrim0 value="dc 'trim0'"}
C {devices/vdd.sym} -550 -60 0 0 {name=l28 lab=trim0_net}
C {devices/gnd.sym} -550 0 0 0 {name=l29 lab=GND}
C {devices/vsource.sym} -650 -30 0 0 {name=Vtrim1 value="dc 'trim1'"}
C {devices/vdd.sym} -650 -60 0 0 {name=l30 lab=trim1_net}
C {devices/gnd.sym} -650 0 0 0 {name=l31 lab=GND}
C {devices/vsource.sym} -750 -30 0 0 {name=Vtrim2 value="dc 'trim2'"}
C {devices/vdd.sym} -750 -60 0 0 {name=l32 lab=trim2_net}
C {devices/gnd.sym} -750 0 0 0 {name=l33 lab=GND}
C {devices/vsource.sym} -850 -30 0 0 {name=Vtrim3 value="dc 'trim3'"}
C {devices/vdd.sym} -850 -60 0 0 {name=l34 lab=trim3_net}
C {devices/gnd.sym} -850 0 0 0 {name=l35 lab=GND}
C {devices/capa.sym} 270 30 0 0 {name=C1
m=1
value='Cload'
device="ceramic capacitor"}
C {devices/lab_pin.sym} 270 0 0 0 {name=l36 sig_type=std_logic lab=vbg}
C {devices/gnd.sym} 270 60 0 0 {name=l37 lab=GND}
C {devices/code.sym} 150 -450 0 0 {name=stimuli
only_toplevel=false
value="
.lib 'models_dir'/cornerMOShv.lib 'mos_corner'
.lib 'models_dir'/cornerMOSlv.lib 'mos_corner'
.lib 'models_dir'/cornerCAP.lib cap_typ
.lib 'models_dir'/cornerRES.lib res_typ
.include 'stdcell_dir'/sg13g2_stdcell.spice
.option TEMP='temperature'
.option warn=1
.options rshunt=1e12
.control
save vbg
tran 10n 1500u 0 100n
set wr_singlescale
wrdata 'simpath'/'filename'_'N'.data v(vbg)
quit
.endc
"}
