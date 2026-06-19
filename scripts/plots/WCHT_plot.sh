#!/bin/bash
# Run from HOURLY_PLOTS.sh

. /mesonet/nawips/Gemenviron.profile
export DISPLAY="localhost:1"
export GEMCOLTBL=coltbl.xwp

yy="$(date -u +%y)"
mm="$(date -u +%m)"
dd="$(date -u +%d)"
date="${yy}${mm}${dd}"
hh="$(date -u +%H)"
ftime="$(date -u +'%Y%m%d%H')00"
YYYYmmdd="$(date -u +'%Y%m%d')"

GIF="wcht.gif"
rm -f "${GIF}"
LOGFILE="/tmp/WCHT_plot.out"
DEVICE="GIF|${GIF}|1024;768"

sfmap << EOF > ${LOGFILE}
    AREA	= 40.25;-97;43.75;-90
    GAREA	= 40.25;-97;43.75;-90
    SATFIL   =
    RADFIL   =
    SFPARM   =  WCHT
    COLORS   =  4
    DATTIM   =  ${date}/${hh}
    SFFILE   =  /data/gempak/surface/${YYYYmmdd}_sao.gem
    MAP	=  25//2 + 25
    LATLON	=  0
    TITLE	=  32/-1/~ NWS Wind Chill Index
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

EOF

gpend

if [ -f ${GIF} ]; then
    pqinsert -p "plot ac $ftime ${GIF} wceq_${hh}00.gif gif" ${GIF} >& /dev/null
    rm ${GIF}
fi
