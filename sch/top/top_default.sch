v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
L 4 140 20 140 640 {}
L 4 140 640 1020 640 {}
L 4 1020 40 1020 640 {}
L 4 130 40 1020 40 {}
L 4 100 -880 100 670 {}
L 4 100 670 1060 670 {}
L 4 1060 -830 1060 670 {}
L 4 90 -830 1060 -830 {}
T {Trim resistor network} 150 10 0 0 0.4 0.4 {}
T {1.2V CMOS Volatge Reference with buffered and scaled outputs
Design by: Adan Kvitschal} 120 -880 0 0 0.4 0.4 {}
N 440 110 480 110 {
lab=dvdd}
N 440 140 480 140 {
lab=dvss}
N 650 -380 650 -370 {
lab=ibias}
N 650 -470 650 -450 {
lab=#net1}
N 650 -550 650 -530 {
lab=avdd_ena}
N 670 -420 670 -360 {
lab=avdd_ena}
N 650 -550 670 -550 {
lab=avdd_ena}
N 670 -170 670 -140 {
lab=avss}
N 440 230 470 230 {
lab=trim3}
N 440 310 470 310 {
lab=trim2}
N 440 390 470 390 {
lab=trim1}
N 440 470 470 470 {
lab=trim0}
N 650 -420 670 -420 {
lab=avdd_ena}
N 840 600 860 600 {
lab=avss}
N 670 -550 670 -420 {
lab=avdd_ena}
N 860 510 860 600 {
lab=avss}
N 700 430 700 440 {
lab=#net2}
N 700 430 860 430 {
lab=#net2}
N 860 430 860 440 {
lab=#net2}
N 700 350 700 360 {
lab=#net3}
N 700 350 860 350 {
lab=#net3}
N 700 270 700 280 {
lab=#net4}
N 700 270 860 270 {
lab=#net4}
N 700 190 700 200 {
lab=#net5}
N 700 190 860 190 {
lab=#net5}
N 700 500 700 510 {
lab=avss}
N 700 510 860 510 {
lab=avss}
N 820 470 820 530 {
lab=avss}
N 700 230 820 230 {
lab=avss}
N 700 310 820 310 {
lab=avss}
N 700 390 820 390 {
lab=avss}
N 700 470 820 470 {lab=avss}
N 700 420 700 430 {
lab=#net2}
N 700 340 700 350 {
lab=#net3}
N 700 260 700 270 {
lab=#net4}
N 860 500 860 510 {
lab=avss}
N 820 230 820 310 {
lab=avss}
N 820 310 820 390 {
lab=avss}
N 820 390 820 470 {
lab=avss}
N 550 230 660 230 {lab=#net6}
N 550 310 660 310 {lab=#net7}
N 550 390 660 390 {lab=#net8}
N 550 470 660 470 {lab=#net9}
N 540 -420 610 -420 {lab=pbias}
N 670 -260 670 -170 {
lab=avss}
N 200 -170 670 -170 {lab=avss}
N 450 -720 450 -650 {lab=avdd}
N 430 -720 450 -720 {
lab=avdd}
N 200 -390 230 -390 {lab=avdd_ena}
N 200 -330 200 -170 {lab=avss}
N 180 -170 200 -170 {lab=avss}
N 200 -330 230 -330 {lab=avss}
N 480 -390 540 -390 {lab=pbias}
N 540 -420 540 -390 {lab=pbias}
N 480 -330 610 -330 {lab=vref}
N 450 -550 650 -550 {lab=avdd_ena}
N 200 -550 200 -390 {lab=avdd_ena}
N 450 -590 450 -550 {lab=avdd_ena}
N 200 -550 450 -550 {lab=avdd_ena}
N 580 -290 610 -290 {lab=amp_fb}
N 860 -530 940 -530 {lab=vbg}
N 860 -530 860 -510 {lab=vbg}
N 580 -290 580 -230 {lab=amp_fb}
N 580 -230 860 -230 {lab=amp_fb}
N 860 -430 940 -430 {lab=vbgtg}
N 860 -430 860 -410 {lab=vbgtg}
N 860 -450 860 -430 {lab=vbgtg}
N 860 -330 860 -310 {lab=vbgsc}
N 860 -330 940 -330 {lab=vbgsc}
N 860 -350 860 -330 {lab=vbgsc}
N 860 -230 860 -210 {lab=amp_fb}
N 860 -250 860 -230 {lab=amp_fb}
N 860 -150 860 190 {lab=#net5}
N 750 -310 800 -310 {lab=vbg}
N 800 -530 800 -310 {lab=vbg}
N 800 -530 860 -530 {lab=vbg}
N 860 420 860 430 {lab=#net2}
N 860 350 860 360 {lab=#net3}
N 860 340 860 350 {lab=#net3}
N 860 270 860 280 {lab=#net4}
N 860 260 860 270 {lab=#net4}
N 860 190 860 200 {lab=#net5}
N 620 -380 650 -380 {lab=ibias}
N 650 -390 650 -380 {
lab=ibias}
C {devices/opin.sym} 940 -530 0 0 {name=p2 lab=vbg
}
C {devices/iopin.sym} 180 -170 0 1 {name=p9 lab=avss}
C {devices/iopin.sym} 440 110 0 1 {name=p7 lab=dvdd}
C {devices/iopin.sym} 440 140 0 1 {name=p8 lab=dvss}
C {devices/opin.sym} 940 -330 0 0 {name=p20 lab=vbgsc
}
C {devices/opin.sym} 940 -430 0 0 {name=p21 lab=vbgtg
}
C {devices/lab_pin.sym} 480 110 0 1 {name=p28 sig_type=std_logic lab=dvdd}
C {devices/lab_pin.sym} 480 140 0 1 {name=p30 sig_type=std_logic lab=dvss}
C {sch/output_amp.sym} 670 -310 0 0 {name=x2}
C {devices/ammeter.sym} 650 -500 0 0 {name=Vm_b3 savecurrent=true lvs_ignore=short}
C {devices/ipin.sym} 440 230 0 0 {name=p4 lab=trim3}
C {devices/ipin.sym} 440 310 0 0 {name=p5 lab=trim2}
C {devices/ipin.sym} 440 390 0 0 {name=p6 lab=trim1}
C {devices/ipin.sym} 440 470 0 0 {name=p11 lab=trim0}
C {devices/lab_pin.sym} 670 -140 0 0 {name=p18 sig_type=std_logic lab=avss}
C {sg13g2_pr/sg13_hv_pmos.sym} 630 -420 0 0 {name=M1
l='pbias_length'
w='amp_bias_width'
ng='m1_ng'
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13cmos5l_stdcells/sg13cmos5l_buf_1.sym} 510 230 0 0 {name=x5 VDD=dvdd VSS=dvss prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_buf_1.sym} 510 310 0 0 {name=x6 VDD=dvdd VSS=dvss prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_buf_1.sym} 510 390 0 0 {name=x7 VDD=dvdd VSS=dvss prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_buf_1.sym} 510 470 0 0 {name=x8 VDD=dvdd VSS=dvss prefix=sg13cmos5l_ }
C {sg13g2_pr/sg13_hv_nmos.sym} 680 470 0 0 {name=M6
l='trim_switch_length'
w='trim_switch_width'
ng='m6_ng'
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 680 390 0 0 {name=M7
l='trim_switch_length'
w='trim_switch_width'
ng='m7_ng'
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 680 310 0 0 {name=M8
l='trim_switch_length'
w='trim_switch_width'
ng='m8_ng'
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 680 230 0 0 {name=M9
l='trim_switch_length'
w='trim_switch_width'
ng='m9_ng'
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sch/cmos_vref.sym} 360 -360 0 0 {name=X1}
C {devices/lab_pin.sym} 540 -420 0 0 {name=p31 sig_type=std_logic lab=pbias}
C {devices/lab_pin.sym} 840 600 0 0 {name=p1 sig_type=std_logic lab=avss}
C {devices/iopin.sym} 430 -720 0 1 {name=p10 lab=avdd}
C {devices/ipin.sym} 330 -620 0 0 {name=p14 lab=ena}
C {sg13cmos5l_stdcells/sg13cmos5l_buf_1.sym} 370 -620 0 0 {name=x4 VDD=dvdd VSS=dvss prefix=sg13cmos5l_ }
C {sg13g2_pr/sg13_hv_pmos.sym} 430 -620 0 0 {name=M2
l='ena_length'
w='ena_width'
ng='m2_ng'
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 820 530 0 0 {name=p12 sig_type=std_logic lab=avss}
C {devices/lab_pin.sym} 800 -230 1 1 {name=pseg6 sig_type=std_logic lab=amp_fb}
C {devices/lab_pin.sym} 540 -330 1 1 {name=p3 sig_type=std_logic lab=vref}
C {sch/res_wrap/rhigh_s2.sym} 860 -480 0 0 {name=XRF1
w='base_width'
l='r1_length'
body=avss
}
C {sch/res_wrap/rhigh_s1.sym} 860 -380 0 0 {name=XRF2
w='base_width'
l='r2_length'
body=avss
}
C {sch/res_wrap/rhigh_s4.sym} 860 -280 0 0 {name=XRF3
w='base_width'
l='r3_length'
body=avss
}
C {sch/res_wrap/rhigh_s8.sym} 860 -180 0 0 {name=XRF4
w='base_width'
l='r4_length'
body=avss
}
C {sch/res_wrap/rhigh_s1.sym} 860 470 0 0 {name=XRT1
w='base_width'
l='r_trim_unit_length'
body=avss
}
C {sch/res_wrap/rhigh_s2.sym} 860 390 0 0 {name=XRT2
w='base_width'
l='r_trim_unit_length'
body=avss
}
C {sch/res_wrap/rhigh_s4.sym} 860 310 0 0 {name=XRT3
w='base_width'
l='r_trim_unit_length'
body=avss
}
C {sch/res_wrap/rhigh_s8.sym} 860 230 0 0 {name=XRT4
w='base_width'
l='r_trim_unit_length'
body=avss
}
C {devices/lab_pin.sym} 620 -380 0 0 {name=p13 sig_type=std_logic lab=ibias}
C {devices/lab_pin.sym} 670 -550 0 1 {name=p15 sig_type=std_logic lab=avdd_ena}
