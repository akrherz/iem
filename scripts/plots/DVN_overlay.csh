#!/bin/csh
#		DVN_overlay.csh
# Script that plots RADAR over the Mesonet data

source /mesonet/nawips/Gemenviron


set h_date=`date -u --date "1 hour ago" +%Y%m%d_%H`

set yy=`date -u +%y`
set YY=`date -u +%Y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set dateY=${YY}${mm}${dd}
set hh=`date -u +%H`

rm DVN_radar.gif* >& /dev/null

set DEVICE1="GIF|DVN_radar.gif|800;600"


setenv DATA_DIR /mesonet/data/nexrad/NIDS/DVN/N0R
setenv CHECK_DIR /mesonet/data/nexrad/NIDS/DVN/N0V

set grid=${DATA_DIR}/N0R_${dateY}_${hh}00
set USE_TIME=${dateY}_${hh}00

if (! -e ${grid} ) then
	set grid=${DATA_DIR}/N0R_${dateY}_${hh}01
	set USE_TIME=${dateY}_${hh}01
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}02
	set USE_TIME=${dateY}_${hh}02
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}03
	set USE_TIME=${dateY}_${hh}03
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}04
	set USE_TIME=${dateY}_${hh}04
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}05
	set USE_TIME=${dateY}_${hh}05
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}06
	set USE_TIME=${dateY}_${hh}06
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${h_date}59
	set USE_TIME=${h_date}59
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${h_date}58
	set USE_TIME=${h_date}58
endif

if (! -e ${grid} ) then
        set grid=${DATA_DIR}/N0R_${h_date}57
	set USE_TIME=${h_date}59
endif


set TITLE="Mesonet with Quad Cities NEXRAD"
set RADFIL=${grid}
set PROJ=RAD

#set checkGrid=${CHECK_DIR}/N0V_${USE_TIME}
#if (! -e ${checkGrid} ) then
#	set TITLE = Mesonet and Radar in Clear Air
#	set RADFIL=
#	set PROJ=LCC
#endif

$GEMEXE/sfmap << EOF > /tmp/RADAR_overlay_sfmap.out
#	GAREA	= 40.25;-97;43.75;-90
#	AREA	= 40.25;-97;43.75;-90
	GAREA	= dvn+
	AREA	= dvn+
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
	RADFIL   = ${RADFIL}
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

gpend

if (-e DVN_radar.gif) then
/home/ldm/bin/pqinsert -p "plot c 000000000000 DVN_radar.gif bogus gif" DVN_radar.gif >& /dev/null
rm DVN_radar.gif
endif
