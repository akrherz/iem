#!/bin/bash
# Run from HOURLY_PLOTS

. /mesonet/nawips/Gemenviron.profile

export GEMCOLTBL=coltbl.xwp

yy=`date -u +%y`
mm=`date -u +%m`
dd=`date -u +%d`
date=${yy}${mm}${dd}
hh=`date -u +%H`

GIF="temps.gif"
DEVICE="GIF|${GIF}|1024;768"

sfmap << EOF > /tmp/TEMPS_plot.out
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
    TITLE    =  32/-1/~ Temp Comparison  [ASOS red]  [RWIS blue]
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

sfmap << EOF >> /tmp/TEMPS_plot.out
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

if [ -f ${GIF} ]; then
    pqinsert -p "plot c 000000000000 ${GIF} bogus gif" ${GIF} >& /dev/null
    rm -f ${GIF}
fi
