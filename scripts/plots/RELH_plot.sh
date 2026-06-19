#!/bin/bash
# Called from HOURLY_PLOTS.sh

. /mesonet/nawips/Gemenviron.profile

export GEMCOLTBL=coltbl.xwp
export DISPLAY="localhost:1"

yy="$(date -u +%y)"
mm="$(date -u +%m)"
dd="$(date -u +%d)"
date="${yy}${mm}${dd}"
hh="$(date -u +%H)"
dateY="$(date -u +'%Y%m%d')"

GIF="relh.gif"
rm -f "${GIF}"
DEVICE="GIF|${GIF}|1024;768"
LOGFILE="/tmp/RELH_plot.out"

export DISPLAY=localhost:1

sfmap_gf << EOF > "${LOGFILE}"
    AREA	= 40.25;-97;43.75;-90
    GAREA	= 40.25;-97;43.75;-90
    SATFIL   =
    RADFIL   =
    CLRBAR =
    SFPARM   =  STID;RELH
    COLORS   =  25;(60;80;100/32;23;2;2/RELH/L)
    DATTIM   =  ${date}/${hh}
    SFFILE   =  /data/gempak/surface/${dateY}_sao.gem
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

if [ -f "${GIF}" ]; then
    pqinsert -p "plot c 000000000000 ${GIF} bogus gif" ${GIF} >& /dev/null
    rm ${GIF}
fi
