v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
L 4 0 0 770 0 {}
L 4 0 -700 770 -700 {}
L 4 0 -710 0 -700 {}
L 4 -10 -700 0 -700 {}
L 4 770 -700 770 -0 {}
L 4 -0 -700 -0 0 {}
T {Simple Operational Amplifier for the CMOS Vref
Design by: Adan Kvitschal} 10 -700 0 0 0.4 0.4 {}
N 180 -50 180 -30 {
lab=vss}
N 300 -50 300 -30 {
lab=vss}
N 180 -120 240 -120 {
lab=ibias}
N 300 -470 340 -470 {
lab=#net1}
N 300 -210 380 -210 {
lab=vcm}
N 220 -430 300 -430 {
lab=#net1}
N 300 -470 300 -430 {
lab=#net1}
N 170 -260 180 -260 {
lab=vn}
N 430 -260 440 -260 {
lab=vp}
N 380 -390 460 -390 {
lab=vo_pre}
N 300 -130 300 -110 {
lab=#net2}
N 300 -210 300 -190 {
lab=vcm}
N 220 -230 220 -210 {
lab=vcm}
N 380 -230 380 -210 {
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
N 240 -80 260 -80 {
lab=ibias}
N 620 -50 620 -30 {
lab=vss}
N 300 -30 620 -30 {
lab=vss}
N 620 -390 710 -390 {
lab=vo}
N 90 -30 180 -30 {
lab=vss}
N 620 -130 620 -110 {
lab=#net6}
N 90 -120 180 -120 {
lab=ibias}
N 180 -600 220 -600 {
lab=vdd}
N 170 -340 170 -260 {
lab=vn}
N 170 -340 180 -340 {
lab=vn}
N 220 -310 220 -290 {
lab=#net7}
N 380 -310 380 -290 {
lab=#net8}
N 420 -340 430 -340 {
lab=vp}
N 430 -340 430 -260 {
lab=vp}
N 220 -430 220 -370 {
lab=#net1}
N 380 -390 380 -370 {
lab=vo_pre}
N 620 -390 620 -190 {
lab=vo}
N 220 -340 250 -340 {
lab=SUB}
N 220 -260 250 -260 {
lab=SUB}
N 350 -340 380 -340 {
lab=SUB}
N 350 -260 380 -260 {
lab=SUB}
N 180 -120 180 -110 {
lab=ibias}
N 240 -120 550 -120 {
lab=ibias}
N 550 -120 550 -80 {
lab=ibias}
N 550 -80 580 -80 {
lab=ibias}
N 300 -80 330 -80 {
lab=SUB}
N 150 -80 180 -80 {
lab=SUB}
N 240 -120 240 -80 {
lab=ibias}
N 620 -80 650 -80 {
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
N 180 -30 300 -30 {
lab=vss}
N 220 -440 220 -430 {
lab=#net1}
N 260 -470 300 -470 {
lab=#net1}
N 380 -440 380 -390 {
lab=vo_pre}
N 220 -210 300 -210 {
lab=vcm}
N 620 -430 620 -390 {
lab=vo}
N 220 -600 380 -600 {
lab=vdd}
N 160 -260 170 -260 {
lab=vn}
N 420 -260 430 -260 {
lab=vp}
N 220 -80 240 -80 {
lab=ibias}
N 90 -600 180 -600 {
lab=vdd}
N 380 -600 420 -600 {
lab=vdd}
N 90 40 140 40 {lab=SUB}
C {devices/ipin.sym} 440 -260 0 1 {name=p2 lab=vp}
C {devices/ipin.sym} 160 -260 0 0 {name=p3 lab=vn}
C {devices/ipin.sym} 90 -120 0 0 {name=p4 lab=ibias
}
C {devices/ammeter.sym} 220 -550 0 0 {name=Vm_b1 savecurrent=true lvs_ignore=short}
C {devices/ammeter.sym} 620 -550 0 0 {name=Vm_op savecurrent=true lvs_ignore=short}
C {devices/ammeter.sym} 300 -160 0 0 {name=Vm_cm savecurrent=true lvs_ignore=short}
C {devices/ammeter.sym} 380 -550 0 0 {name=Vm_b2 savecurrent=true lvs_ignore=short}
C {devices/ammeter.sym} 620 -160 0 0 {name=Vm_on savecurrent=true lvs_ignore=short}
C {devices/opin.sym} 710 -390 0 0 {name=p1 lab=vo
}
C {devices/ipin.sym} 90 -30 0 0 {name=p5 lab=vss
}
C {devices/ipin.sym} 90 -600 0 0 {name=p6 lab=vdd
}
C {devices/ipin.sym} 90 40 0 0 {name=p16 lab=SUB
}
C {devices/lab_pin.sym} 380 -390 0 0 {name=p7 sig_type=std_logic lab=vo_pre}
C {devices/lab_pin.sym} 300 -200 0 0 {name=p8 sig_type=std_logic lab=vcm}
C {devices/lab_pin.sym} 250 -340 0 1 {name=p9 sig_type=std_logic lab=SUB}
C {devices/lab_pin.sym} 250 -260 0 1 {name=p10 sig_type=std_logic lab=SUB}
C {devices/lab_pin.sym} 350 -340 0 0 {name=p11 sig_type=std_logic lab=SUB}
C {devices/lab_pin.sym} 350 -260 0 0 {name=p12 sig_type=std_logic lab=SUB}
C {devices/lab_pin.sym} 330 -80 0 1 {name=p13 sig_type=std_logic lab=SUB}
C {devices/lab_pin.sym} 150 -80 0 0 {name=p14 sig_type=std_logic lab=SUB}
C {devices/lab_pin.sym} 650 -80 0 1 {name=p15 sig_type=std_logic lab=SUB}
C {sg13g2_pr/sg13_hv_nmos.sym} 200 -80 0 1 {name=M1
l=1u
w=2.5u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 280 -80 0 0 {name=M2
l=1u
w=5u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 600 -80 0 0 {name=M3
l=1u
w=8u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 200 -260 0 0 {name=M4
l=2u
w=10u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 400 -260 0 1 {name=M5
l=2u
w=10u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/cap_cmim.sym} 530 -390 1 0 {name=C1
model=cap_cmim
w=5u
l=5u
m=1
spiceprefix=X}
C {sg13g2_pr/sg13_hv_nmos.sym} 200 -340 0 0 {name=M6
l=2u
w=20u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 400 -340 0 1 {name=M7
l=2u
w=20u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 240 -470 0 1 {name=M8
l=10u
w=5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 360 -470 0 0 {name=M9
l=10u
w=5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 600 -460 0 0 {name=M10
l=5u
w=40u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 140 40 0 1 {name=p17 sig_type=std_logic lab=SUB}
