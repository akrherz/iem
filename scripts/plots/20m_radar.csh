#!/bin/csh

source /mesonet/nawips/Gemenviron

set yy=`date --date '1 minute' -u +%y`
set YYYY=`date --date '1 minute' -u +%Y`
set mm=`date --date '1 minute' -u +%m`
set dd=`date --date '1 minute' -u +%d`
set date=${yy}${mm}${dd}
set dateY=${YYYY}${mm}${dd}
set hh=`date --date '1 minute' -u +%H`
set mm=`date --date '1 minute' -u +%M`

set localtime="`date +'%Y/%m/%d %I:%M %p'`"

if (${mm} > 40 ) then
	set mm = "40"
	set m = "4"
else if (${mm} > 20) then
	set mm = "20"
	set m = "2"
else
	set mm = "00"
	set m = "0"
endif

rm 20radarOverlay.gif* 20radarOverlay_s.gif* >& /dev/null

set DEVICE1="GIF|20radarOverlay.gif"
set DEVICE2="GIF|20radarOverlay_s.gif|500;400"


setenv DATA_DIR /mesonet/data/nexrad/NIDS/DMX/N0R
set grid=${DATA_DIR}/N0R_${dateY}_${hh}${mm}
set proj="RAD"

if (! -e ${grid} )then
	set grid=${DATA_DIR}/N0R_${dateY}_${hh}${m}1
endif

if (! -e ${grid} )then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}${m}2
endif

if (! -e ${grid} )then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}${m}3
endif

if (! -e ${grid} )then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}${m}4
endif

if (! -e ${grid} )then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}${m}5
endif

if (! -e ${grid} )then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}${m}6
endif

if (! -e ${grid} )then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}${m}7
endif

if (! -e ${grid} )then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}${m}8
endif

if (! -e ${grid} )then
        set grid=${DATA_DIR}/N0R_${dateY}_${hh}${m}9
endif


set TITLE="32/-1/${date}/${hh}${mm} 20m Mesonet with Radar"

if (! -e ${grid} ) then
	set grid = " "
	set proj = "LCC"
	set TITLE = "32/-1/${date}/${hh}${mm} 20m Mesonet Radar missing"
endif


$GEMEXE/sfmap << EOF > /dev/null
	GAREA	= 40.25;-97;43.75;-90
	AREA	= 40.25;-97;43.75;-90
	DATTIM  = ${date}/${hh}${mm}
	GLEVEL   = 0
	GVCORD   = NONE
	SFPARM   =  skyc:.6;tmpf<120;wsym:1.2:2;alti;;dwpf<120;;;;brbk:1:1:231
	COLORS   =  32;2;32;0;4;32
	SFFILE   = /mesonet/data/gempak/sao/${date}_sao.gem
	LINE     = 4/1/1
	TEXT     = 1/1
	DEVICE   = ${DEVICE1}
	SATFIL   = 
	RADFIL   = ${grid}
	PROJ     = ${proj}
	CLEAR    = yes
	PANEL	= 0
	TITLE	= ${TITLE} (${localtime})
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

	DEVICE	= ${DEVICE2}
	list
	run


	exit
EOF

gpend

if (-e 20radarOverlay.gif) then
  /home/ldm/bin/pqinsert -p "plot r 000000000000 20radarOverlay_ bogus gif" 20radarOverlay.gif
  rm -f 20radarOverlay.gif
endif

if (-e 20radarOverlay_s.gif) then
  /home/ldm/bin/pqinsert -p "plot r 000000000000 20radarOverlay_s_ bogus gif" 20radarOverlay_s.gif
  rm -f 20radarOverlay_s.gif
endif
