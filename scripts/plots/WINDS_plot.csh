#!/bin/csh
#		WINDS_plot.csh
# Script that plots a wind comparison for the two nets
# Daryl Herzmann 10 Jul 2001
# 09 Oct 2001	Update a bit
# 17 Feb 2003	Use GIF driver
#		Cleanup more

source /mesonet/nawips/Gemenviron

setenv GEMCOLTBL coltbl.xwp

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`

rm winds.gif* >& /dev/null

set DEVICE="GIF|winds.gif|650;500"

# setenv DISPLAY localhost:1

$GEMEXE/sfmap << EOF > /tmp/WINDS_plot_sfmap.out
	AREA    = 40.25;-97;43.75;-90
	GAREA    = 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  brbk:1:1:231
	COLORS   =  2
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  /mesonet/data/gempak/sao/${date}_sao.gem
	MAP      =  25//2 + 25
 	LATLON   =  0
        TITLE    =  32/-1/~ Wind Compare [ASOS/AWOS red] [RWIS blue]
        CLEAR    =  no
        PANEL    =  0
        DEVICE   = ${DEVICE}
        PROJ     =  LCC
        FILTER   =  .3
        TEXT     =  1/1//hw
        LUTFIL   =
        STNPLT   =
	\$mapfil = HIPOWO.CIA + HICNUS.NWS
	list
	run

EOF

$GEMEXE/sfmap << EOF > /tmp/WINDS_plot_sfmap2.out
	COLORS  =  4
	SFFILE	= /mesonet/data/gempak/rwis/${date}_rwis.gem
	TITLE	= 0
	MAP	= 0
	CLEAR	= no
        DEVICE   = ${DEVICE}
	list	
	run

	exit
EOF

$GEMEXE/gpend

if (-e winds.gif) then
	#~/bin/slogo.csh ~/plots/winds.gif
	#cp winds.gif ~/current
	#mv winds.gif WEB/
  /home/ldm/bin/pqinsert -p "plot c 000000000000 winds.gif bogus gif" winds.gif >& /dev/null
  rm winds.gif
endif
