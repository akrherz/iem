#!/bin/csh
#		MPX_overlay.csh
# Script that generates a RADAR image of MPX

source /mesonet/nawips/Gemenviron
setenv DISPLAY localhost:1

set h_date=`date -u --date "1 hour ago" +%Y%m%d_%H`

set yy=`date -u +%y`
set YY=`date -u +%Y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set dateY=${YY}${mm}${dd}
set hh=`date -u +%H`

rm MPX_radar.gif* >& /dev/null

set DEVICE1="GIF|MPX_radar.gif|800;600"

setenv DATA_DIR /mesonet/data/nexrad/NIDS/MPX/N0R
set grid=${DATA_DIR}/N0R_${dateY}_${hh}00

if (! -e ${grid} ) then
	set grid=${DATA_DIR}/N0R_${dateY}_${hh}01
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}02
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}03
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}04
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}05
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}06
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${h_date}59
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${h_date}58
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${h_date}57
endif

set PROJ=RAD
set TITLE="Mesonet with Minneapolis NEXRAD"

# if (! -e ${grid} ) then
#	set grid=
#	set PROJ=LCC
#	set TITLE="Mesonet with NEXRAD missing"
#endif

$GEMEXE/sfmap_gf << EOF > /tmp/MPX_overlay_sfmap.out
#	GAREA	= 40.25;-97;43.75;-90
#	AREA	= 40.25;-97;43.75;-90
	AREA	= msp+
	GAREA	= msp+
	DATTIM  = ${date}/${hh}00
	GLEVEL	= 0
	GVCORD   = NONE
	SFPARM   = skyc:.6;tmpf<120;wsym:1.2:2;alti;;dwpf<120;;;;brbk:1:1:231
	COLORS   = 32;2;32;0;4;32
	SFFILE   = /mesonet/data/gempak/sao/${date}_sao.gem
	LINE     = 4/1/1
	TEXT     = 1/1
	DEVICE   = ${DEVICE1}
	SATFIL   = 
	RADFIL   = ${grid}
	PROJ     = ${PROJ}
	CLEAR    = yes
	PANEL	= 0
	TITLE	= 32/-1/~ ${TITLE}
	SCALE	= 0
	GVECT   =
	WIND    = 
	LATLON	= 0
	HILO     =  
	HLSYM    =  
	CLRBAR   = 0
	CONTUR   = 3/3
	SKIP     = 0
	CINT	= 
	FINT	=  
	FLINE    = 24-12--1 
	LUTFIL   = radar.tbl
	STNPLT   =  
	MAP     = 25//1 + 25//2
        \$mapfil =HICNUS.NWS + hipowo.cia
	list
	run

	exit
EOF

if (-e MPX_radar.gif) then
/home/ldm/bin/pqinsert -p "plot c 000000000000 MPX_radar.gif bogus gif" MPX_radar.gif >& /dev/null
rm MPX_radar.gif
endif
