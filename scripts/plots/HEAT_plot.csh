#!/bin/csh
# 		HEAT_plot.csh
# Daryl Herzmann 10 November 2000

source /mesonet/nawips/Gemenviron
setenv DISPLAY localhost:1


setenv GEMCOLTBL coltbl.xwp

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`
set ftime="`date -u +'%Y%m%d%H'`00"

rm heat.gif >& /dev/null

set DEVICE="GIF|heat.gif"

$GEMEXE/sfmap_gf << EOF > /tmp/HEAT_plot_sfmap.out
	AREA	= 40.25;-97;43.75;-90
	GAREA	= 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  HEAT
	COLORS   =  2
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  /mesonet/data/gempak/meso/${date}_meso.gem
	MAP	=  25//2 + 25
 	LATLON	=  0
        TITLE	=  32/-1/~ Heat Index
        CLEAR	=  no
        PANEL	=  0
        DEVICE	= ${DEVICE}
        PROJ	=  LCC
        FILTER	=  .3
        TEXT	=  1/1//hw
        LUTFIL	=
        STNPLT	=
	\$mapfil = HIPOWO.CIA + HICNUS.NWS
	list
	run

EOF


if (-e heat.gif) then
  pqinsert -p "plot ac $ftime heat.gif heat_${hh}00.gif gif" heat.gif >& /dev/null
rm heat.gif
endif
