v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 0 -80 0 -30 {lab=top,taps[2:0]
bus=true}
N 0 30 0 80 {lab=taps[2:0],bot
bus=true}
N 110 -60 140 -60 {lab=taps[2:0]}
N -50 90 -10 90 {lab=bot}
N -40 -90 -10 -90 {lab=top}
C {devices/iopin.sym} -40 -90 0 1 {name=p1 lab=top}
C {devices/iopin.sym} -50 90 0 1 {name=p2 lab=bot}
C {sg13g2_pr/rhigh.sym} 0 0 0 0 {name=R[3:0]
w='w'
l='l'
model=rhigh
body=body
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {devices/iopin.sym} 140 -60 0 0 {name=p4 lab=taps[2:0]}
C {devices/lab_pin.sym} 0 -50 2 1 {name=l1 sig_type=std_logic lab=top,taps[2:0]}
C {devices/lab_pin.sym} 0 50 2 1 {name=l2 sig_type=std_logic lab=taps[2:0],bot}
C {devices/lab_pin.sym} 110 -60 2 1 {name=l4 sig_type=std_logic lab=taps[2:0]}
C {bus_tap.sym} 0 80 2 0 {name=l3 lab=bot}
C {bus_tap.sym} 0 -80 0 1 {name=l5 lab=top}
C {devices/iopin.sym} -40 130 0 1 {name=p9 lab=body}
