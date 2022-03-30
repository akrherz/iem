#!/bin/csh
# Finally, the script that plots all of this good data
# Daryl Herzmann 10 November 2000

source /mesonet/nawips/Gemenviron

setenv DISPLAY localhost:1

set yy=`date -u +%y`
set MM=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${MM}${dd}
set hh=`date -u +%H`

set mm = "00"

rm asos.gif* >& /dev/null

set DEVICE="GIF|asos.gif"


$GEMEXE/sfmap_gf << EOF > /tmp/sfmap.out
	AREA    = 40.25;-97;43.75;-90
	GAREA    = 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  skyc;tmpf;wsym:1.2:2;altm;;dwpf;;;;brbk:1:2:231
	COLORS   =  32;2;32;25;4;32
 	DATTIM   =  ${date}/${hh}${mm}
 	SFFILE   =  /mesonet/data/gempak/sao/${date}_sao.gem
 	LATLON   =  0
        TITLE    =  32/-1/~ ASOS Data 
        CLEAR    =  no
        PANEL    =  0
        DEVICE   = ${DEVICE}
        PROJ     =  LCC
        FILTER   =  .3
        TEXT     = 1.2
        LUTFIL   =
        STNPLT   =
	MAP	= 25 + 25//2
	\$mapfil = HICNUS.NWS + hipowo.cia
	list
	run

	exit
EOF

if (-e asos.gif ) then
    pqinsert -p "plot c 000000000000 asos.gif bogus gif" asos.gif >& /dev/null
    rm asos.gif
endif
