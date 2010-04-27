#!/bin/csh
#		1h_precip.csh
#  Plots up the 1 hour precip values for the area
# 17 Feb 2003:	Use GIF driver
##########################################################

source /mesonet/nawips/Gemenviron

setenv GEMCOLTBL coltbl.xwp

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`

rm 1hprecip.gif >& /dev/null

set DEVICE="GIF|1hprecip.gif"


$GEMEXE/sfmap << EOF > /tmp/1h_precip_sfmap.out
	AREA	= 40.25;-97;43.75;-90
	GAREA	= 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  P01I*100
	COLORS   =  2
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  /mesonet/data/gempak/meso/${date}_meso.gem
	MAP	=  25//2 + 25
 	LATLON	=  0
        TITLE	=  32/-1/1h precip ending ~
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

gpend

if (-e 1hprecip.gif) then
	#~/bin/logo.csh ~/plots/1hprecip.gif
	#cp 1hprecip.gif ~/current
	#mv 1hprecip.gif WEB/
  /home/ldm/bin/pqinsert -p "plot c 000000000000 1hprecip.gif bogus gif" 1hprecip.gif >& /dev/null
endif
