v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N -40 -80 0 -80 {lab=top}
N -40 80 0 80 {lab=bot}
N 0 -80 0 -30 {lab=top}
N 0 30 0 80 {lab=bot}
C {devices/iopin.sym} -40 -80 0 1 {name=p1 lab=top}
C {devices/iopin.sym} -40 80 0 1 {name=p2 lab=bot}
C {sg13g2_pr/rhigh.sym} 0 0 0 0 {name=R1
w='w'
l='l'
model=rhigh
body=body
spiceprefix=X
b=0
m=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
}
C {devices/iopin.sym} -40 130 0 1 {name=p9 lab=body}
