#!/bin/csh
#		DMX_overlay.csh
# Script that plots RADAR over the Mesonet data
# 12 June 2001: Daryl Herzmann
# 18 Jun 2001:  Updated for mesonet box
# 20 Jun 2001:  If 00 Radar does not exist, then 05 probably does

source /home/nawips/Gemenviron

set h_date=`date -u --date "1 hour ago" +%Y%m%d_%H`

set yy=`date -u +%y`
set YY=`date -u +%Y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set dateY=${YY}${mm}${dd}
set hh=`date -u +%H`

rm ${1}_RADAR.gif* >& /dev/null

set DEVICE1="GF|${1}_RADAR.gif|600;600"

setenv DISPLAY localhost:1

setenv DATA_DIR /home/ldm/data/nexrad/nids/${1}/N0R
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


$GEMEXE/sfmap_gf << EOF > ../TMP/${1}_RADAR_overlay.out
	GAREA	= DSM+
	AREA	= DSM+
	DATTIM  = ${date}/${hh}00
	GLEVEL	= 0
	GVCORD   = NONE
	SFPARM   = 
	COLORS   = 
	SFFILE   = /mesonet/data/gempak/24hour.gem
	LINE     =
	TEXT     =
	DEVICE   = ${DEVICE1}
	SATFIL   = 
	RADFIL   = ${grid}
	PROJ     = RAD
	CLEAR    = yes
	PANEL	= 0
	TITLE	= 0
	SCALE	= 0
	GVECT   =
	WIND    = 
	LATLON	= 0
	HILO     =  
	HLSYM    =  
	CLRBAR   = 0
	CONTUR   = 0
	SKIP     = 0
	CINT	= 
	FINT	=  
	FLINE    = 
	LUTFIL   = ../../TABLES/radar.tbl
	STNPLT   =  
	MAP     = 0
        \$mapfil =
	list
	run

	exit
EOF

convert -transparency white ${1}_RADAR.gif ${1}_RADAR2.gif
convert -colorspace Transparent -crop 540x540+30+30 ${1}_RADAR2.gif ${1}_RADAR.tif

geotifcp -e ${1}_RADAR.wld ${1}_RADAR.tif ${1}_final.tif
cp ${1}_final.tif /mesonet/www/html/GIS/data/images/${1}_RADAR.tif
