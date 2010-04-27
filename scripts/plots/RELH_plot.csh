#!/bin/csh
# 		RELH_plot.csh
# Daryl Herzmann 13 Feb 2004
#########################################################

source /mesonet/nawips/Gemenviron

setenv GEMCOLTBL coltbl.xwp

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`

rm relh.gif* >& /dev/null

set DEVICE="GF|relh.gif"

setenv DISPLAY localhost:1

$GEMEXE/sfmap_gf << EOF > TMP/RELH_plot_sfmap.out
	AREA	= 40.25;-97;43.75;-90
	GAREA	= 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
  CLRBAR = 
	SFPARM   =  STID;RELH
	COLORS   =  25;(60;80;100/32;23;2;2/RELH/L)
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  /mesonet/data/gempak/meso/${date}_meso.gem
	MAP	=  25//2 + 25
 	LATLON	=  0
        TITLE	=  32/-1/~ Relative Humidity
        CLEAR	=  no
        PANEL	=  0
        DEVICE	= ${DEVICE}
        PROJ	=  LCC
        FILTER	=  .8
        TEXT	=  1
        LUTFIL	=
        STNPLT	=
	\$mapfil = HIPOWO.CIA + HICNUS.NWS
	list
	run

EOF

if (-e relh.gif) then
	#~/bin/slogo.csh ~/plots/relh.gif
	#mv relh.gif ~/current
  /home/ldm/bin/pqinsert -p "plot c 000000000000 relh.gif bogus gif" relh.gif >& /dev/null
endif
