#!/bin/bash

. /mesonet/nawips/Gemenviron.profile

export DISPLAY="localhost:1"
export GEMCOLTBL=coltbl.xwp

yy=$(date -u +%y)
mm=$(date -u +%m)
dd=$(date -u +%d)
date=${yy}${mm}${dd}
hh=$(date -u +%H)
ftime="$(date -u +'%Y%m%d%H')00"
dateY="$(date -u +'%Y%m%d')"

GIF="heat.gif"
rm -f "${GIF}"
DEVICE="GIF|${GIF}|1024;768"

sfmap_gf << EOF > /tmp/HEAT_plot_sfmap.out
    AREA	= 40.25;-97;43.75;-90
    GAREA	= 40.25;-97;43.75;-90
    SATFIL   =
    RADFIL   =
    SFPARM   =  HEAT
    COLORS   =  2
    DATTIM   =  ${date}/${hh}
    SFFILE   =  /data/gempak/surface/${dateY}_sao.gem
    MAP	=  25//2 + 25
    LATLON	=  0
    TITLE	=  32/-1/~ Heat Index
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


if [ -f "${GIF}" ]; then
    pqinsert -p "plot ac $ftime heat.gif heat_${hh}00.gif gif" "${GIF}" >& /dev/null
    rm "${GIF}"
fi
