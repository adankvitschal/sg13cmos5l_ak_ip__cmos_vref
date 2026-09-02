v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 380 -120 380 -60 {lab=#net1}
N 220 -20 340 -20 {lab=vp}
N 220 -20 220 40 {lab=vp}
N 530 0 530 60 {lab=vo}
N 500 0 530 0 {lab=vo}
N 500 0 500 100 {lab=vo}
N 480 0 500 0 {lab=vo}
N 300 100 500 100 {lab=vo}
N 300 20 300 100 {lab=vo}
N 300 20 340 20 {lab=vo}
C {devices/code.sym} 150 -320 0 0 {name=stimuli
only_toplevel=false
value="
.lib 'models_dir'/cornerMOShv.lib 'mos_corner'
.lib 'models_dir'/cornerCAP.lib cap_typ
.option TEMP='temperature'
.option warn=1
.control
save all
op
set wr_singlescale
wrdata 'simpath'/'filename'_'N'.data -I(Vdd)
quit
.endc
"}
C {sch/output_amp.sym} 400 0 0 0 {name=X1}
C {devices/gnd.sym} 440 50 0 0 {name=lsub lab=GND}
C {devices/vdd.sym} 400 -50 0 0 {name=l1 lab=vdd}
C {devices/gnd.sym} 400 50 0 0 {name=l2 lab=GND}
C {devices/lab_pin.sym} 530 0 0 1 {name=l4 sig_type=std_logic lab=vo}
C {devices/lab_pin.sym} 220 -20 0 0 {name=l5 sig_type=std_logic lab=vp}
C {devices/vsource.sym} 0 -200 0 0 {name=Vdd value="dc 'vdd'"}
C {devices/vdd.sym} 0 -230 0 0 {name=l7 lab=vdd}
C {devices/gnd.sym} 0 -170 0 0 {name=l8 lab=GND}
C {devices/vsource.sym} 220 70 0 0 {name=Vvp value="dc 'amp_vcm'"}
C {devices/gnd.sym} 220 100 0 0 {name=l10 lab=GND}
C {devices/isource.sym} 380 -150 0 0 {name=Ibias value='ibias'}
C {devices/capa.sym} 530 90 0 0 {name=C1
m=1
value='Cload'
device="ceramic capacitor"}
C {devices/gnd.sym} 530 120 0 0 {name=l16 lab=GND}
C {devices/vdd.sym} 380 -180 0 0 {name=l11 lab=vdd}
