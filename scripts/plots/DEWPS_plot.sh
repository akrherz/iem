#!/bin/bash
# Called from HOURLY_PLOTS.sh

. /mesonet/nawips/Gemenviron.profile

export GEMCOLTBL=coltbl.xwp
export DISPLAY="localhost:1"

yy=$(date -u +%y)
mm=$(date -u +%m)
dd=$(date -u +%d)
date=${yy}${mm}${dd}
hh=$(date -u +%H)
dateY="$(date -u +'%Y%m%d')"

GIF="dewps.gif"
rm -f "${GIF}"
DEVICE="GIF|${GIF}|1024;768"
LOGFILE="/tmp/DEWPS_plot.log"

sfmap << EOF > "${LOGFILE}"
    AREA    = 40.25;-97;43.75;-90
    GAREA    = 40.25;-97;43.75;-90
    SATFIL   =
    RADFIL   =
    SFPARM   =  dwpf<120
    COLORS   =  2
    DATTIM   =  ${date}/${hh}
    SFFILE   =  /data/gempak/surface/${dateY}_sao.gem
    LATLON   =  0
    TITLE    =  32/-1/~ Dew Point Comp [ASOS red]  [RWIS blue]
    CLEAR    =  no
    PANEL    =  0
    DEVICE   = ${DEVICE}
    PROJ     =  LCC
    FILTER   =  .3
    TEXT     =  1/1//hw
    LUTFIL   =
    STNPLT   =
    MAP     = 25 + 25//2
    \$MAPFIL = HICNUS.NWS + hipowo.cia
    list
    run

EOF

sfmap << EOF >> "${LOGFILE}"
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

gpend

if [ -f "${GIF}" ]; then
    pqinsert -p "plot c 000000000000 ${GIF} ${GIF} gif" "${GIF}" >& /dev/null
    rm -f "${GIF}"
fi
