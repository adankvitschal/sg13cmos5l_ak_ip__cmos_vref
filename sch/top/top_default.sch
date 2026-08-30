v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 390 20 430 20 {
lab=dvdd}
N 390 50 430 50 {
lab=dvss}
N 740 -370 770 -370 {
lab=#net1}
N 1050 -560 1070 -560 {
lab=vbg}
N 810 -470 810 -450 {
lab=#net2}
N 810 -550 810 -530 {
lab=#net3}
N 810 -630 810 -610 {
lab=#net4}
N 830 -500 830 -440 {
lab=#net4}
N 810 -630 830 -630 {
lab=#net4}
N 830 -250 830 -220 {
lab=avss}
N 630 -90 660 -90 {
lab=trim3}
N 630 -10 660 -10 {
lab=trim2}
N 630 70 660 70 {
lab=trim1}
N 630 150 660 150 {
lab=trim0}
N 1050 -560 1050 -540 {
lab=vbg}
N 1050 -470 1050 -460 {
lab=vbgtg}
N 1050 -390 1050 -380 {
lab=vbgsc}
N 1050 -470 1070 -470 {
lab=vbgtg}
N 1050 -310 1050 -300 {
lab=#net1}
N 1050 -390 1070 -390 {
lab=vbgsc}
N 740 -310 1050 -310 {
lab=#net1}
N 740 -370 740 -310 {
lab=#net1}
N 910 -390 970 -390 {
lab=vbg}
N 970 -560 970 -390 {
lab=vbg}
N 970 -560 1050 -560 {
lab=vbg}
N 1050 -240 1050 -130 {
lab=#net5}
N 810 -500 830 -500 {
lab=#net4}
N 1030 280 1050 280 {
lab=avss}
N 1050 -480 1050 -470 {
lab=vbgtg}
N 1050 -400 1050 -390 {
lab=vbgsc}
N 1050 -320 1050 -310 {
lab=#net1}
N 830 -630 830 -500 {
lab=#net4}
N 1050 -130 1050 -120 {
lab=#net5}
N 1050 190 1050 280 {
lab=avss}
N 890 110 890 120 {
lab=#net6}
N 890 110 1050 110 {
lab=#net6}
N 1050 110 1050 120 {
lab=#net6}
N 1050 30 1050 40 {
lab=#net7}
N 1050 -50 1050 -40 {
lab=#net8}
N 890 30 890 40 {
lab=#net7}
N 890 30 1050 30 {
lab=#net7}
N 890 -50 890 -40 {
lab=#net8}
N 890 -50 1050 -50 {
lab=#net8}
N 890 -130 890 -120 {
lab=#net5}
N 890 -130 1050 -130 {
lab=#net5}
N 890 180 890 190 {
lab=avss}
N 890 190 1050 190 {
lab=avss}
N 1010 150 1010 210 {
lab=SUB}
N 890 -90 1010 -90 {
lab=SUB}
N 890 -10 1010 -10 {
lab=SUB}
N 890 70 1010 70 {
lab=SUB}
N 890 150 1010 150 {lab=SUB}
N 890 100 890 110 {
lab=#net6}
N 1050 100 1050 110 {
lab=#net6}
N 890 20 890 30 {
lab=#net7}
N 1050 20 1050 30 {
lab=#net7}
N 890 -60 890 -50 {
lab=#net8}
N 1050 -60 1050 -50 {
lab=#net8}
N 1050 180 1050 190 {
lab=avss}
N 1010 -90 1010 -10 {
lab=SUB}
N 1010 -10 1010 70 {
lab=SUB}
N 1010 70 1010 150 {
lab=SUB}
N 740 -90 850 -90 {lab=#net9}
N 740 -10 850 -10 {lab=#net10}
N 740 70 850 70 {lab=#net11}
N 740 150 850 150 {lab=#net12}
N 700 -500 770 -500 {lab=#net13}
N 830 -340 830 -250 {
lab=avss}
N 360 -250 830 -250 {lab=avss}
N 610 -800 610 -730 {lab=avdd18}
N 590 -800 610 -800 {
lab=avdd18}
N 360 -470 390 -470 {lab=#net4}
N 360 -410 360 -250 {lab=avss}
N 340 -250 360 -250 {lab=avss}
N 360 -410 390 -410 {lab=avss}
N 640 -470 700 -470 {lab=#net13}
N 700 -500 700 -470 {lab=#net13}
N 640 -410 770 -410 {lab=#net14}
N 610 -630 810 -630 {lab=#net4}
N 360 -630 360 -470 {lab=#net4}
N 610 -670 610 -630 {lab=#net4}
N 360 -630 610 -630 {lab=#net4}
C {devices/opin.sym} 1070 -560 0 0 {name=p2 lab=vbg
}
C {devices/iopin.sym} 340 -250 0 1 {name=p9 lab=avss}
C {devices/iopin.sym} 430 20 0 0 {name=p7 lab=dvdd}
C {devices/iopin.sym} 430 50 0 0 {name=p8 lab=dvss}
C {devices/opin.sym} 1070 -390 0 0 {name=p20 lab=vbgsc
}
C {devices/opin.sym} 1070 -470 0 0 {name=p21 lab=vbgtg
}
C {devices/lab_pin.sym} 390 20 0 0 {name=p28 sig_type=std_logic lab=dvdd}
C {devices/lab_pin.sym} 390 50 0 0 {name=p30 sig_type=std_logic lab=dvss}
C {sch/output_amp.sym} 830 -390 0 0 {name=x2}
C {devices/ammeter.sym} 810 -580 0 0 {name=Vm_b3 savecurrent=true lvs_ignore=short}
C {devices/ipin.sym} 630 -90 0 0 {name=p4 lab=trim3}
C {devices/ipin.sym} 630 -10 0 0 {name=p5 lab=trim2}
C {devices/ipin.sym} 630 70 0 0 {name=p6 lab=trim1}
C {devices/ipin.sym} 630 150 0 0 {name=p11 lab=trim0}
C {devices/gnd.sym} 360 -190 0 0 {name=l1 lab=SUB}
C {devices/ammeter.sym} 360 -220 0 0 {name=Vsub_short savecurrent=true}
C {devices/lab_pin.sym} 830 -220 0 0 {name=p18 sig_type=std_logic lab=avss}
C {sg13g2_pr/sg13_hv_pmos.sym} 790 -500 0 0 {name=M1
l='pbias_length'
w='amp_bias_width'
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_stdcells/sg13g2_buf_1.sym} 700 -90 0 0 {name=x5 VDD=VDD VSS=VSS prefix=sg13g2_ }
C {sg13g2_stdcells/sg13g2_buf_1.sym} 700 -10 0 0 {name=x6 VDD=VDD VSS=VSS prefix=sg13g2_ }
C {sg13g2_stdcells/sg13g2_buf_1.sym} 700 70 0 0 {name=x7 VDD=VDD VSS=VSS prefix=sg13g2_ }
C {sg13g2_stdcells/sg13g2_buf_1.sym} 700 150 0 0 {name=x8 VDD=VDD VSS=VSS prefix=sg13g2_ }
C {sg13g2_pr/rhigh.sym} 1050 -510 0 0 {name=R1
w='base_width'
l='r1_length'
model=rhigh
body=sub!
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sg13g2_pr/rhigh.sym} 1050 -430 0 0 {name=R2
w='base_width'
l='r2_length'
model=rhigh
body=sub!
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sg13g2_pr/rhigh.sym} 1050 -350 0 0 {name=R3
w='base_width'
l='r3_length'
model=rhigh
body=sub!
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sg13g2_pr/rhigh.sym} 1050 -270 0 0 {name=R4
w='base_width'
l='r4_length'
model=rhigh
body=sub!
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {devices/gnd.sym} 1010 210 0 0 {name=l2 lab=SUB}
C {sg13g2_pr/sg13_hv_nmos.sym} 870 150 0 0 {name=M6
l='trim_switch_length'
w='trim_switch_width'
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 870 70 0 0 {name=M7
l='trim_switch_length'
w='trim_switch_width'
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 870 -10 0 0 {name=M8
l='trim_switch_length'
w='trim_switch_width'
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 870 -90 0 0 {name=M9
l='trim_switch_length'
w='trim_switch_width'
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/rhigh.sym} 1050 150 0 0 {name=R5
w='base_width'
l='r5_length'
model=rhigh
body=sub!
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sg13g2_pr/rhigh.sym} 1050 70 0 0 {name=R6
w='base_width'
l='r6_length'
model=rhigh
body=sub!
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sg13g2_pr/rhigh.sym} 1050 -10 0 0 {name=R7
w='base_width'
l='r7_length'
model=rhigh
body=sub!
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sg13g2_pr/rhigh.sym} 1050 -90 0 0 {name=R8
w='base_width'
l='r8_length'
model=rhigh
body=sub!
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {sch/cmos_vref.sym} 520 -440 0 0 {name=X1}
C {devices/lab_pin.sym} 1030 280 0 0 {name=p1 sig_type=std_logic lab=avss}
C {devices/iopin.sym} 590 -800 0 1 {name=p10 lab=avdd18}
C {devices/ipin.sym} 490 -700 0 0 {name=p14 lab=ena}
C {sg13g2_stdcells/sg13g2_buf_1.sym} 530 -700 0 0 {name=x4 VDD=VDD VSS=VSS prefix=sg13g2_ }
C {sg13g2_pr/sg13_hv_pmos.sym} 590 -700 0 0 {name=M2
l='ena_length'
w='ena_width'
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
