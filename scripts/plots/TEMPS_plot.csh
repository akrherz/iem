#!/bin/csh
# Finally, the script that plots all of this good data
# Daryl Herzmann 10 November 2000

source /mesonet/nawips/Gemenviron

setenv GEMCOLTBL coltbl.xwp

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`

# rm temps.gif*

set DEVICE="GIF|temps.gif"


$GEMEXE/sfmap << EOF > /tmp/TEMPS_plot_sfmap.out
	AREA    = 40.25;-97;43.75;-90
	GAREA    = 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  tmpf<120
	COLORS   =  2
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  /mesonet/data/gempak/sao/${date}_sao.gem
	MAP      =  25//2 + 25
 	LATLON   =  0
        TITLE    =  32/-1/~ Temp Comparison  [ASOS/AWOS red]  [RWIS blue]
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

	exit
EOF

$GEMEXE/sfmap << EOF > /tmp/TEMPS_plot_sfmap2.out
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

if (-e temps.gif) then
 pqinsert -p "plot c 000000000000 temps.gif bogus gif" temps.gif >& /dev/null
	rm -f temps.gif
endif
