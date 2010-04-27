#!/bin/csh
# 		VSBY_plot.csh
# Daryl Herzmann 22 Oct 2001
# 12 Dec 2001:	Use various colors
# 17 Feb 2003:	Use new GIF driver
#########################################################

source /mesonet/nawips/Gemenviron

setenv GEMCOLTBL coltbl.xwp

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`

rm vsby.gif >& /dev/null

set DEVICE="GIF|vsby.gif|650;500"

#setenv DISPLAY localhost:1

$GEMEXE/sfmap << EOF > TMP/VSBY_plot_sfmap.out
	AREA	= 40.25;-97;43.75;-90
	GAREA	= 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  STID;VSBY*10 > 10
	COLORS   =  25;4
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  /mesonet/data/gempak/meso/${date}_meso.gem
	MAP	=  25//2 + 25
 	LATLON	=  0
        TITLE	=  32/-1/~ Visibility [0.1 miles]
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

	SFPARM   =  STID;VSBY*10 < 11
	COLORS	= 25;2
	list
	run

EOF

gpend

if (-e vsby.gif) then
	#~/bin/slogo.csh ~/plots/vsby.gif
	#cp vsby.gif ~/current
	#mv vsby.gif WEB/
 /home/ldm/bin/pqinsert -p "plot c 000000000000 vsby.gif bogus gif" vsby.gif >& /dev/null
endif
