v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N -180 10 -120 10 {
lab=GND}
N 130 10 270 10 {
lab=vref}
N 270 10 270 130 {
lab=vref}
N -180 -50 -120 -50 {lab=#net1}
C {devices/vsource.sym} 0 -270 0 0 {name=Vavdd value="PWL(0 0 'ramp_time' 'Vavdd')"}
C {devices/vdd.sym} 0 -300 0 0 {name=l7 lab=avdd}
C {devices/gnd.sym} 0 -240 0 0 {name=l8 lab=GND}
C {devices/code.sym} 150 -320 0 0 {name=stimuli
only_toplevel=false
value="
.lib 'models_dir'/cornerMOShv.lib 'mos_corner'
.lib 'models_dir'/cornerMOSlv.lib 'mos_corner'
.lib 'models_dir'/cornerCAP.lib cap_typ
.option TEMP='temperature'
.option warn=1
.control
save all
tran 10n 1500u 0 100n
let vds_m6 = v(x1.net2) - v(x1.vptat)
let vds_m7 = v(x1.net3)
set wr_singlescale
wrdata 'simpath'/'filename'_'N'.data V(vref)
wrdata 'simpath'/'filename'_'N'_diag.data v(vref) v(x1.vptat) v(x1.vbias_st) v(net2) v(x1.net4) vds_m6 vds_m7 i(v.x1.vm_b1) i(vmeas_ana)
set filetype=ascii
write 'simpath'/'filename'_'N'.raw
quit
.endc
"}
C {devices/lab_pin.sym} 270 10 0 1 {name=l10 sig_type=std_logic lab=vref}
C {devices/vdd.sym} -180 -110 0 0 {name=l1 lab=avdd}
C {devices/capa.sym} 270 160 0 0 {name=C1
m=1
value='Cload'
device="ceramic capacitor"}
C {devices/gnd.sym} 270 190 0 0 {name=l9 lab=GND}
C {devices/ammeter.sym} -180 -80 0 0 {name=Vmeas_ana savecurrent=true}
C {devices/gnd.sym} -180 10 0 0 {name=l2 lab=GND}
C {sch/cmos_vref.sym} 10 -20 0 0 {name=X1}
C {devices/gnd.sym} 10 60 0 0 {name=lsub lab=GND}
