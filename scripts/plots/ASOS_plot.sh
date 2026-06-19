#!/bin/bash
# Run from HOURLY_PLOTS.sh

. /mesonet/nawips/Gemenviron.profile

export DISPLAY="localhost:1"

yy="$(date -u +%y)"
MM="$(date -u +%m)"
dd="$(date -u +%d)"
date="${yy}${MM}${dd}"
dateY="$(date -u +%Y%m%d)"
hh="$(date -u +%H)"

mm="00"

GIF="asos.gif"
rm -f "${GIF}"
DEVICE="GIF|${GIF}|1024;768"


sfmap_gf << EOF > /tmp/sfmap.out
    AREA    = 40.25;-97;43.75;-90
    GAREA    = 40.25;-97;43.75;-90
    SATFIL   =
    RADFIL   =
    SFPARM   =  skyc;tmpf;wsym:1.2:2;altm;;dwpf;;;;brbk:1:2:231
    COLORS   =  32;2;32;25;4;32
    DATTIM   =  ${date}/${hh}${mm}
    SFFILE   =  /data/gempak/surface/${dateY}_sao.gem
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

if [ -f "${GIF}" ]; then
    pqinsert -p "plot c 000000000000 ${GIF} bogus gif" "${GIF}" >& /dev/null
    rm -f "${GIF}"
fi
