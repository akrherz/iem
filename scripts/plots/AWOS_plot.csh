#!/bin/csh

source /mesonet/nawips/Gemenviron

set yy=`date -u --date '1 minute' +%y`
set MM=`date -u --date '1 minute' +%m`
set dd=`date -u --date '1 minute' +%d`
set date=${yy}${MM}${dd}
set hh=`date -u --date '1 minute' +%H`
set mm=`date -u --date '1 minute' +%M`

set localtime="`date +'%Y/%m/%d %I:%M %p'`"

if (${mm} > 40 ) then
        set mm = "40"
else if (${mm} > 20) then
        set mm = "20"
else
        set mm = "00"
endif

setenv DISPLAY localhost:1

rm awos.gif* ceil.gif* >& /dev/null

set DEVICE="GIF|awos.gif|650;500"
set DEVICE2="GIF|ceil.gif|650;500"


$GEMEXE/sfmap_gf << EOF > /tmp/awos_plot_sfmap.out
 \$RESPOND = YES
	AREA    = 40.25;-97;43.75;-90
	GAREA    = 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  skyc;tmpf;wsym:1.2:2;;;dwpf;;;;brbk:1:2:111
	COLORS   =  32;2;32;4;32
 	DATTIM   =  ${date}/${hh}${mm}
	SFFILE   =  /mesonet/data/gempak/awos/${date}_awos.gem
 	LATLON   =  0
        TITLE    =  32/-1/~ AWOS Data (${localtime})
        CLEAR    =  no
        PANEL    =  0
        DEVICE   = ${DEVICE}
        PROJ     =  LCC
        FILTER   =  .3
        TEXT     =  1/1//hw
        LUTFIL   =
        STNPLT   =
	MAP	= 25 + 25//2
	\$mapfil = HICNUS.NWS + hipowo.cia
	list
	run

	SFFILE	= /mesonet/data/gempak/meso/${date}_meso.gem
	DEVICE	= ${DEVICE2}
	SFPARM	= ;CEIL;wsym:1.2:2;;;;;;;brbk:1:2:111
	TITLE	= 32/-1/~ ASOS/AWOS Ceiling 100ft (${localtime})
	CLEAR	= yes
	list
	run

	exit
EOF

if (-e awos.gif ) then
    pqinsert -p "plot c 000000000000 awos.gif bogus gif" awos.gif
    pqinsert -p "plot c 000000000000 ceil.gif bogus gif" ceil.gif
    rm awos.gif
    rm ceil.gif
endif
