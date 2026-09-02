v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 380 -100 380 -60 {lab=#net1}
N 560 0 560 40 {lab=vo}
N 480 0 560 0 {lab=vo}
N 150 -100 150 -80 {lab=vp}
N 150 -100 280 -100 {lab=vp}
N 280 -100 300 -20 {lab=vp}
N 300 -20 340 -20 {lab=vp}
N 300 20 340 20 {lab=vn}
N 280 120 300 20 {lab=vn}
N 150 120 280 120 {lab=vn}
N 150 120 150 150 {lab=vn}
C {devices/code.sym} 150 -320 0 0 {name=stimuli
only_toplevel=false
value="
.lib 'models_dir'/cornerMOShv.lib 'mos_corner'
.lib 'models_dir'/cornerCAP.lib cap_typ
.option TEMP='temperature'
.option warn=1
.control
save all
ac dec 20 10 100Meg
set wr_singlescale
wrdata 'simpath'/'filename'_'N'.data vdb(vo) vp(vo)
quit
.endc
"}
C {sch/output_amp.sym} 400 0 0 0 {name=X1}
C {devices/gnd.sym} 440 50 0 0 {name=lsub lab=GND}
C {devices/vdd.sym} 400 -50 0 0 {name=l1 lab=vdd}
C {devices/gnd.sym} 400 50 0 0 {name=l2 lab=GND}
C {devices/lab_pin.sym} 300 -20 0 0 {name=l5 sig_type=std_logic lab=vp}
C {devices/lab_pin.sym} 300 20 0 0 {name=l6 sig_type=std_logic lab=vn}
C {devices/vsource.sym} 0 -200 0 0 {name=Vdd value="dc 'vdd'"}
C {devices/vdd.sym} 0 -230 0 0 {name=l7 lab=vdd}
C {devices/gnd.sym} 0 -170 0 0 {name=l8 lab=GND}
C {devices/vsource.sym} 150 -50 0 0 {name=Vvp value="dc 'amp_vcm' ac 1"}
C {devices/lab_pin.sym} 150 -80 0 0 {name=l9 sig_type=std_logic lab=vp}
C {devices/gnd.sym} 150 -20 0 0 {name=l10 lab=GND}
C {devices/vsource.sym} 150 180 0 0 {name=Vvn value="dc 'amp_vcm'"}
C {devices/lab_pin.sym} 150 150 0 0 {name=l11 sig_type=std_logic lab=vn}
C {devices/gnd.sym} 150 210 0 0 {name=l12 lab=GND}
C {devices/isource.sym} 380 -130 0 0 {name=Ibias value='ibias'}
C {devices/lab_pin.sym} 250 -130 0 0 {name=l13 sig_type=std_logic lab=ibias}
C {devices/capa.sym} 560 70 0 0 {name=C1
m=1
value='Cload'
device="ceramic capacitor"}
C {devices/lab_pin.sym} 560 0 0 1 {name=l15 sig_type=std_logic lab=vo}
C {devices/gnd.sym} 560 100 0 0 {name=l16 lab=GND}
C {devices/vdd.sym} 380 -160 0 0 {name=l3 lab=vdd}
