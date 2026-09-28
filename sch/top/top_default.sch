v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 90 280 130 280 {
lab=dvdd}
N 90 310 130 310 {
lab=dvss}
N 650 -390 650 -370 {
lab=#net1}
N 650 -470 650 -450 {
lab=#net2}
N 650 -550 650 -530 {
lab=#net3}
N 670 -420 670 -360 {
lab=#net3}
N 650 -550 670 -550 {
lab=#net3}
N 670 -170 670 -140 {
lab=avss}
N 330 170 360 170 {
lab=trim3}
N 330 250 360 250 {
lab=trim2}
N 330 330 360 330 {
lab=trim1}
N 330 410 360 410 {
lab=trim0}
N 890 -390 890 -380 {
lab=vbgtg}
N 890 -390 910 -390 {
lab=vbgtg}
N 890 -310 910 -310 {
lab=vbgsc}
N 580 -220 890 -220 {
lab=loop_in}
N 750 -310 810 -310 {
lab=vbg}
N 810 -480 810 -310 {
lab=vbg}
N 810 -480 910 -480 {
lab=vbg}
N 650 -420 670 -420 {
lab=#net3}
N 730 540 750 540 {
lab=avss}
N 890 -320 890 -310 {
lab=vbgsc}
N 670 -550 670 -420 {
lab=#net3}
N 750 450 750 540 {
lab=avss}
N 590 370 590 380 {
lab=trim_t0}
N 590 370 750 370 {
lab=trim_t0}
N 750 370 750 380 {
lab=trim_t0}
N 590 290 590 300 {
lab=trim_t1}
N 590 290 750 290 {
lab=trim_t1}
N 590 210 590 220 {
lab=trim_t2}
N 590 210 750 210 {
lab=trim_t2}
N 590 130 590 140 {
lab=trim_t3}
N 590 130 750 130 {
lab=trim_t3}
N 590 440 590 450 {
lab=avss}
N 590 450 750 450 {
lab=avss}
N 710 410 710 470 {
lab=SUB}
N 590 170 710 170 {
lab=SUB}
N 590 250 710 250 {
lab=SUB}
N 590 330 710 330 {
lab=SUB}
N 590 410 710 410 {lab=SUB}
N 590 360 590 370 {
lab=trim_t0}
N 590 280 590 290 {
lab=trim_t1}
N 590 200 590 210 {
lab=trim_t2}
N 750 440 750 450 {
lab=avss}
N 710 170 710 250 {
lab=SUB}
N 710 250 710 330 {
lab=SUB}
N 710 330 710 410 {
lab=SUB}
N 440 170 550 170 {lab=#net5}
N 440 250 550 250 {lab=#net6}
N 440 330 550 330 {lab=#net7}
N 440 410 550 410 {lab=#net8}
N 540 -420 610 -420 {lab=#net9}
N 670 -260 670 -170 {
lab=avss}
N 200 -170 670 -170 {lab=avss}
N 450 -720 450 -650 {lab=avdd}
N 430 -720 450 -720 {
lab=avdd}
N 200 -390 230 -390 {lab=#net3}
N 200 -330 200 -170 {lab=avss}
N 180 -170 200 -170 {lab=avss}
N 180 -110 240 -110 {lab=SUB}
N 200 -330 230 -330 {lab=avss}
N 480 -390 540 -390 {lab=#net9}
N 540 -420 540 -390 {lab=#net9}
N 480 -330 610 -330 {lab=#net10}
N 450 -550 650 -550 {lab=#net3}
N 200 -550 200 -390 {lab=#net3}
N 450 -590 450 -550 {lab=#net3}
N 200 -550 450 -550 {lab=#net3}
N 580 -290 610 -290 {lab=loop_in}
N 710 -260 710 -250 {lab=SUB}
N 580 -290 580 -220 {lab=loop_in}
C {devices/opin.sym} 910 -480 0 0 {name=p2 lab=vbg
}
C {devices/iopin.sym} 180 -170 0 1 {name=p9 lab=avss}
C {devices/iopin.sym} 180 -110 0 1 {name=p33 lab=SUB}
C {devices/iopin.sym} 130 280 0 0 {name=p7 lab=dvdd}
C {devices/iopin.sym} 130 310 0 0 {name=p8 lab=dvss}
C {devices/opin.sym} 910 -310 0 0 {name=p20 lab=vbgsc
}
C {devices/opin.sym} 910 -390 0 0 {name=p21 lab=vbgtg
}
C {devices/lab_pin.sym} 90 280 0 0 {name=p28 sig_type=std_logic lab=dvdd}
C {devices/lab_pin.sym} 90 310 0 0 {name=p30 sig_type=std_logic lab=dvss}
C {sch/output_amp.sym} 670 -310 0 0 {name=x2}
C {devices/lab_pin.sym} 710 -250 0 1 {name=p32 sig_type=std_logic lab=SUB}
C {devices/ammeter.sym} 650 -500 0 0 {name=Vm_b3 savecurrent=true lvs_ignore=short}
C {devices/ipin.sym} 330 170 0 0 {name=p4 lab=trim3}
C {devices/ipin.sym} 330 250 0 0 {name=p5 lab=trim2}
C {devices/ipin.sym} 330 330 0 0 {name=p6 lab=trim1}
C {devices/ipin.sym} 330 410 0 0 {name=p11 lab=trim0}
C {devices/lab_pin.sym} 670 -140 0 0 {name=p18 sig_type=std_logic lab=avss}
C {sg13g2_pr/sg13_hv_pmos.sym} 630 -420 0 0 {name=M1
l='pbias_length'
w='amp_bias_width'
ng='m1_ng'
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13cmos5l_stdcells/sg13cmos5l_buf_1.sym} 400 170 0 0 {name=x5 VDD=dvdd VSS=dvss prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_buf_1.sym} 400 250 0 0 {name=x6 VDD=dvdd VSS=dvss prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_buf_1.sym} 400 330 0 0 {name=x7 VDD=dvdd VSS=dvss prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_buf_1.sym} 400 410 0 0 {name=x8 VDD=dvdd VSS=dvss prefix=sg13cmos5l_ }
C {sg13g2_pr/rhigh.sym} 890 -430 0 0 {name=R1[1:0]
w='base_width'
l='r1_length'
model=rhigh
body=SUB
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sg13g2_pr/rhigh.sym} 890 -350 0 0 {name=R2
w='base_width'
l='r2_length'
model=rhigh
body=SUB
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sg13g2_pr/rhigh.sym} 890 -270 0 0 {name=R3[1:0]
w='base_width'
l='r3_length'
model=rhigh
body=SUB
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sg13g2_pr/rhigh.sym} 890 -190 0 0 {name=R4[7:0]
w='base_width'
l='r4_length'
model=rhigh
body=SUB
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sg13g2_pr/sg13_hv_nmos.sym} 570 410 0 0 {name=M6
l='trim_switch_length'
w='trim_switch_width'
ng='m6_ng'
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 570 330 0 0 {name=M7
l='trim_switch_length'
w='trim_switch_width'
ng='m7_ng'
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 570 250 0 0 {name=M8
l='trim_switch_length'
w='trim_switch_width'
ng='m8_ng'
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 570 170 0 0 {name=M9
l='trim_switch_length'
w='trim_switch_width'
ng='m9_ng'
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/rhigh.sym} 750 410 0 0 {name=R5
w='base_width'
l='r_trim_unit_length'
model=rhigh
body=SUB
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sg13g2_pr/rhigh.sym} 750 330 0 0 {name=R6[1:0]
w='base_width'
l='r_trim_unit_length'
model=rhigh
body=SUB
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sg13g2_pr/rhigh.sym} 750 250 0 0 {name=R7[3:0]
w='base_width'
l='r_trim_unit_length'
model=rhigh
body=SUB
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sg13g2_pr/rhigh.sym} 750 170 0 0 {name=R8[7:0]
w='base_width'
l='r_trim_unit_length'
model=rhigh
body=SUB
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sch/cmos_vref.sym} 360 -360 0 0 {name=X1}
C {devices/lab_pin.sym} 360 -280 0 0 {name=p31 sig_type=std_logic lab=SUB}
C {devices/lab_pin.sym} 730 540 0 0 {name=p1 sig_type=std_logic lab=avss}
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
C {devices/lab_pin.sym} 240 -110 0 1 {name=p3 sig_type=std_logic lab=SUB}
C {devices/lab_pin.sym} 710 470 0 0 {name=p12 sig_type=std_logic lab=SUB}
C {devices/lab_pin.sym} 750 140 0 1 {name=ptrim0 sig_type=std_logic lab=trim_t3,trim_r8[6:0]}
C {devices/lab_pin.sym} 750 200 0 1 {name=ptrim1 sig_type=std_logic lab=trim_r8[6:0],trim_t2}
C {devices/lab_pin.sym} 750 220 0 1 {name=ptrim2 sig_type=std_logic lab=trim_t2,trim_r7[2:0]}
C {devices/lab_pin.sym} 750 280 0 1 {name=ptrim3 sig_type=std_logic lab=trim_r7[2:0],trim_t1}
C {devices/lab_pin.sym} 750 300 0 1 {name=ptrim4 sig_type=std_logic lab=trim_t1,trim_r6}
C {devices/lab_pin.sym} 750 360 0 1 {name=ptrim5 sig_type=std_logic lab=trim_r6,trim_t0}
C {devices/lab_pin.sym} 750 130 0 1 {name=ptrim6 sig_type=std_logic lab=trim_t3}
C {devices/lab_pin.sym} 750 210 0 1 {name=ptrim7 sig_type=std_logic lab=trim_t2}
C {devices/lab_pin.sym} 750 290 0 1 {name=ptrim8 sig_type=std_logic lab=trim_t1}
C {devices/lab_pin.sym} 750 370 0 1 {name=ptrim9 sig_type=std_logic lab=trim_t0}
C {devices/lab_pin.sym} 890 -460 0 1 {name=pseg0 sig_type=std_logic lab=vbg,r1_s}
C {devices/lab_pin.sym} 890 -400 0 1 {name=pseg1 sig_type=std_logic lab=r1_s,vbgtg}
C {devices/lab_pin.sym} 890 -300 0 1 {name=pseg2 sig_type=std_logic lab=vbgsc,r3_s}
C {devices/lab_pin.sym} 890 -240 0 1 {name=pseg3 sig_type=std_logic lab=r3_s,loop_in}
C {devices/lab_pin.sym} 890 -220 0 1 {name=pseg4 sig_type=std_logic lab=loop_in,r4_s[6:0]}
C {devices/lab_pin.sym} 890 -160 0 1 {name=pseg5 sig_type=std_logic lab=r4_s[6:0],trim_t3}
