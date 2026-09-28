v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
L 4 0 -60 770 -60 {}
L 4 0 -700 770 -700 {}
L 4 0 -710 0 -700 {}
L 4 -10 -700 0 -700 {}
L 4 770 -700 770 -0 {}
L 4 -0 -700 -0 0 {}
T {Simple Operational Amplifier for the CMOS Vref
Design by: Adan Kvitschal} 10 -700 0 0 0.4 0.4 {}
N 180 -110 180 -90 {
lab=vss}
N 300 -110 300 -90 {
lab=vss}
N 180 -180 240 -180 {
lab=ibias}
N 300 -470 340 -470 {
lab=#net1}
N 300 -270 380 -270 {
lab=vcm}
N 220 -430 300 -430 {
lab=#net1}
N 300 -470 300 -430 {
lab=#net1}
N 380 -390 460 -390 {
lab=vo_pre}
N 300 -190 300 -170 {
lab=#net2}
N 300 -270 300 -250 {
lab=vcm}
N 220 -290 220 -270 {
lab=vcm}
N 380 -290 380 -270 {
lab=vcm}
N 220 -520 220 -500 {
lab=#net3}
N 380 -520 380 -500 {
lab=#net4}
N 460 -390 500 -390 {
lab=vo_pre}
N 560 -390 620 -390 {
lab=vo}
N 460 -460 580 -460 {
lab=vo_pre}
N 460 -460 460 -390 {
lab=vo_pre}
N 620 -520 620 -490 {
lab=#net5}
N 220 -600 220 -580 {
lab=vdd}
N 380 -600 380 -580 {
lab=vdd}
N 620 -600 620 -580 {
lab=vdd}
N 420 -600 620 -600 {
lab=vdd}
N 240 -140 260 -140 {
lab=ibias}
N 620 -110 620 -90 {
lab=vss}
N 300 -90 620 -90 {
lab=vss}
N 620 -390 710 -390 {
lab=vo}
N 90 -90 180 -90 {
lab=vss}
N 620 -190 620 -170 {
lab=#net6}
N 90 -180 180 -180 {
lab=ibias}
N 180 -600 220 -600 {
lab=vdd}
N 220 -430 220 -350 {
lab=#net1}
N 380 -390 380 -350 {
lab=vo_pre}
N 220 -320 250 -320 {
lab=SUB}
N 350 -320 380 -320 {
lab=SUB}
N 180 -180 180 -170 {
lab=ibias}
N 240 -180 550 -180 {
lab=ibias}
N 550 -180 550 -140 {
lab=ibias}
N 550 -140 580 -140 {
lab=ibias}
N 300 -140 330 -140 {
lab=SUB}
N 150 -140 180 -140 {
lab=SUB}
N 240 -180 240 -140 {
lab=ibias}
N 620 -140 650 -140 {
lab=SUB}
N 180 -470 220 -470 {
lab=vdd}
N 180 -600 180 -470 {
lab=vdd}
N 380 -470 420 -470 {
lab=vdd}
N 420 -600 420 -470 {
lab=vdd}
N 620 -460 660 -460 {
lab=vdd}
N 660 -600 660 -460 {lab=vdd}
N 620 -600 660 -600 {lab=vdd}
N 180 -90 300 -90 {
lab=vss}
N 220 -440 220 -430 {
lab=#net1}
N 260 -470 300 -470 {
lab=#net1}
N 380 -440 380 -390 {
lab=vo_pre}
N 220 -270 300 -270 {
lab=vcm}
N 620 -430 620 -390 {
lab=vo}
N 220 -600 380 -600 {
lab=vdd}
N 160 -320 180 -320 {
lab=vn}
N 420 -320 440 -320 {
lab=vp}
N 220 -140 240 -140 {
lab=ibias}
N 90 -600 180 -600 {
lab=vdd}
N 380 -600 420 -600 {
lab=vdd}
N 90 40 140 40 {lab=SUB}
N 620 -390 620 -250 {lab=vo}
C {devices/ipin.sym} 440 -320 0 1 {name=p2 lab=vp}
C {devices/ipin.sym} 160 -320 0 0 {name=p3 lab=vn}
C {devices/ipin.sym} 90 -180 0 0 {name=p4 lab=ibias
}
C {devices/ammeter.sym} 220 -550 0 0 {name=Vm_b1 savecurrent=true lvs_ignore=short}
C {devices/ammeter.sym} 620 -550 0 0 {name=Vm_op savecurrent=true lvs_ignore=short}
C {devices/ammeter.sym} 300 -220 0 0 {name=Vm_cm savecurrent=true lvs_ignore=short}
C {devices/ammeter.sym} 380 -550 0 0 {name=Vm_b2 savecurrent=true lvs_ignore=short}
C {devices/ammeter.sym} 620 -220 0 0 {name=Vm_on savecurrent=true lvs_ignore=short}
C {devices/opin.sym} 710 -390 0 0 {name=p1 lab=vo
}
C {devices/ipin.sym} 90 -90 0 0 {name=p5 lab=vss
}
C {devices/ipin.sym} 90 -600 0 0 {name=p6 lab=vdd
}
C {devices/ipin.sym} 90 40 0 0 {name=p16 lab=SUB
}
C {devices/lab_pin.sym} 380 -390 0 0 {name=p7 sig_type=std_logic lab=vo_pre}
C {devices/lab_pin.sym} 300 -260 0 0 {name=p8 sig_type=std_logic lab=vcm}
C {devices/lab_pin.sym} 250 -320 0 1 {name=p10 sig_type=std_logic lab=SUB}
C {devices/lab_pin.sym} 350 -320 0 0 {name=p12 sig_type=std_logic lab=SUB}
C {devices/lab_pin.sym} 330 -140 0 1 {name=p13 sig_type=std_logic lab=SUB}
C {devices/lab_pin.sym} 150 -140 0 0 {name=p14 sig_type=std_logic lab=SUB}
C {devices/lab_pin.sym} 650 -140 0 1 {name=p15 sig_type=std_logic lab=SUB}
C {sg13g2_pr/sg13_hv_nmos.sym} 200 -140 0 1 {name=M1
l='nbias_length'
w='m1_width'
ng='m1_ng'
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 280 -140 0 0 {name=M2
l='nbias_length'
w='m2_width'
ng='m2_ng'
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 600 -140 0 0 {name=M3
l='nbias_length'
w='m3_width'
ng='m3_ng'
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 200 -320 0 0 {name=M4
l='m4m5_length'
w='m4m5_width'
ng='m4_ng'
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 400 -320 0 1 {name=M5
l='m4m5_length'
w='m4m5_width'
ng='m5_ng'
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 240 -470 0 1 {name=M8
l='m8m9_length'
w='m8m9_width'
ng='m8_ng'
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 360 -470 0 0 {name=M9
l='m8m9_length'
w='m8m9_width'
ng='m9_ng'
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 600 -460 0 0 {name=M10
l='m10_length'
w='m10_width'
ng='m10_ng'
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 140 40 0 1 {name=p17 sig_type=std_logic lab=SUB}
C {sg13cmos5l_pr/cap_cmomf.sym} 530 -390 3 0 {name=C1
model=cap_cmomf
w='millercap_side'
l='millercap_side'
mmin=1
mmax=4
subblock=0
m='millercap_mult'
mm_ok=1
spiceprefix=X
}
