#!/bin/bash

. /mesonet/nawips/Gemenviron.profile

export GEMCOLTBL=coltbl.xwp
export DISPLAY=localhost:1

yy=$(date -u --date '1 minute' +'%y')
mm=$(date -u --date '1 minute' +'%m')
dd=$(date -u --date '1 minute' +'%d')
hh=$(date -u --date '1 minute' +'%H')
dateY=$(date -u --date '1 minute' +'%Y%m%d')
date=${yy}${mm}${dd}
timestamp=$(date -u --date '1 minute' +'%Y%m%d%H00')

nicetime=$(date -d "20${1}-${2}-${3} ${4}:00" +"%b %d %I %p")

GIF="mesonet_altm.gif"
rm -f "${GIF}"
DEVICE="GIF|${GIF}|1024;768"
AREA="40.15;-97.1;43.85;-89.9"
LOGFILE="/tmp/pres_plot.out"

# Now we plot
sfmap << EOF > "${LOGFILE}"
    AREA    = ${AREA}
    GAREA    = ${AREA}
    SATFIL   =
    RADFIL   =
    SFPARM   =  STID;;;altm>100;;;;;;;brbk:1:1:231
    COLORS   =  2;32
    DATTIM   =  ${date}/${hh}
    SFFILE   =  /data/gempak/surface/${dateY}_sao.gem
    LATLON   =  0
    TITLE    =  32/-1/GMT: ~ Iowa Mesonet Altimeter Plot
    CLEAR    =  yes
    PANEL    =  0
    DEVICE   = ${DEVICE}
    PROJ     =  LCC
    FILTER   =  .3
    TEXT     =  1/1//hw
    LUTFIL   =
    STNPLT   =
    MAP	= 25 + 25//2
    \$MAPFIL = HICNUS.NWS + hipowo.cia
    list
    run

    exit
EOF


gdcntr << EOF >> "${LOGFILE}"
    GAREA    = ${AREA}
    GDATTIM  = ${date}/${hh}
    GLEVEL   = 0
    GVCORD   = NONE
    GFUNC    = SM9S(ALTM)
    GDFILE   = /mesonet/data/iemplot/grid_oa.grd
    CINT     = 1
    LINE     = 4
    MAP      = 0
    TEXT     = 1
    DEVICE   = ${DEVICE}
    SATFIL   =
    RADFIL   =
    PROJ     = LCC
    CLEAR    = no
    PANEL	= 0
    TITLE	= 32/-2/LOCAL: ${nicetime}
    SCALE    = 0
    LATLON   = 0
    HILO     =
    HLSYM    =
    CLRBAR   = 1
    CONTUR   = 3/3
    SKIP     = 0
    FINT     = 0
    FLINE    = 10-20
    CTYPE    = C
    LUTFIL   =
    STNPLT   =
    list
    run

    exit
EOF

gpend


if [ -f "${GIF}" ]; then
    pqinsert -p "plot ac ${timestamp} ${GIF} mesonet_altm_${hh}00.gif gif" "${GIF}" >& /dev/null
    rm -f "${GIF}"
fi
