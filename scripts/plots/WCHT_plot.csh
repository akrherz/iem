#!/bin/csh
# 		WCHT_plot.csh

source /mesonet/nawips/Gemenviron
setenv DISPLAY localhost:1
setenv GEMCOLTBL coltbl.xwp

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`
set ftime="`date -u +'%Y%m%d%H'`00"

set DEVICE="GIF|wcht.gif|650;500"

$GEMEXE/sfmap << EOF > /tmp/WCHT_plot_sfmap.out
	AREA	= 40.25;-97;43.75;-90
	GAREA	= 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  WCHT
	COLORS   =  4
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  /mesonet/data/gempak/meso/${date}_meso.gem
	MAP	=  25//2 + 25
 	LATLON	=  0
        TITLE	=  32/-1/~ NWS Wind Chill Index
        CLEAR	=  no
        PANEL	=  0
        DEVICE	= ${DEVICE}
        PROJ	=  LCC
        FILTER	=  .8
        TEXT	=  1/1//hw
        LUTFIL	=
        STNPLT	=
	\$mapfil = HIPOWO.CIA + HICNUS.NWS
	list
	run

EOF

gpend

if (-e wcht.gif) then
pqinsert -p "plot ac $ftime wcht.gif wceq_${hh}00.gif gif" wcht.gif >& /dev/null
rm  wcht.gif
endif
