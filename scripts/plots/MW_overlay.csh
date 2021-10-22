#!/bin/csh
#		MW_overlay.csh
# Script that overlays RADAR onto of Midwest Obs

source /mesonet/nawips/Gemenviron
setenv DISPLAY localhost:1

setenv GEMCOLTBL coltbl.xwp

set yy=`date -u --date '1 minute' +%y`
set MM=`date -u --date '1 minute' +%m`
set dd=`date -u --date '1 minute' +%d`
set date=${yy}${MM}${dd}
set hh=`date -u --date '1 minute' +%H`
set mm=`date -u --date '1 minute' +%M`


if (${mm} > 40 ) then
        set mm = "40"
else if (${mm} > 20) then
        set mm = "20"
else
        set mm = "00"
endif

set timestamp="`date -u +'%Y%m%d%H'`${mm}"
set RADTIME="${yy}${MM}${dd}/${hh}${mm}"

rm MWoverlay.gif* >& /dev/null

set DEVICE="GIF|MWoverlay.gif|900;700"

#set RADTIME=`cat /tmp/compRADAR.time`
set AREA="39.25;-98.0;44.75;-89.0"
set SFCTIME=${date}/${hh}${mm}

gdplot << EOF > /tmp/MW_overlay_gdplot.out
	GAREA    = ${AREA}
        PROJ     = MER
	GDATTIM  = LAST
	GDFILE	= /mesonet/data/gempak/radar.gem
	GFUNC   = N0R
        PANEL   = 0
 CLEAR	= yes
        LATLON   = 0
        DEVICE   = ${DEVICE}
 MAP	= 25 + 25//2
 \$mapfil = hicnus.nws + hipowo.cia

        text     = 1/1/1
        TITLE    = 0
        GLEVEL   = 0
        GVCORD   = none
        CTYPE    = F
        PANEL    = 0
        SKIP     = 0
        SCALE    = 0
        CONTUR   = 0
        HILO     =
        LATLON   = 0
        STNPLT   =
        SATFIL   =
        RADFIL   =
        LUTFIL   =
        STREAM   =
        POSN     = 0
        COLORS   = 1
        MARKER   = 0
        GRDLBL   = 0
        FILTER   = YES
        FINT     = 10;15;20;25;30;35;40;45;50;55;60;65;70;75;80
        FLINE    = 0;26;24;21;22;23;20;18-16;14-10;0
        CLRBAR   = 32

	list
	run

	exit
EOF
# Now we plot
sfmap << EOF > /tmp/MW_overlay_sfmap.out
	AREA    = ${AREA}
	GAREA    = ${AREA}
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  skyc:.6;tmpf<120;wsym:1.2:2;alti;;dwpf<120;;;;brbk:1:1:231
	COLORS   =  32;2;32;0;4;32
 	DATTIM   =  ${SFCTIME}
 	SFFILE   =  /mesonet/data/gempak/sao/${date}_sao.gem
 	LATLON   =  0
        TITLE    =  32/-1/RADTIME: ${RADTIME}   SFCTIME: ${SFCTIME}
 CLEAR	= no
        PANEL    =  0
        DEVICE   = ${DEVICE}
        PROJ     =  MER
        FILTER   =  .3
        TEXT     =  1/1//hw
        LUTFIL   =
        STNPLT   =
	MAP	= 0
  CLEAR = no
	list
	run

	exit
EOF

gpend

if (-e MWoverlay.gif) then
	pqinsert -p "plot acr $timestamp MWoverlay_ MWoverlay_${hh}${mm}.gif gif" MWoverlay.gif >& /dev/null
	rm MWoverlay.gif
endif
