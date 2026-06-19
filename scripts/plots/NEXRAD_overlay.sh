#!/bin/bash

. /mesonet/nawips/Gemenviron.profile

export DISPLAY="localhost:1"
export GEMCOLTBL=coltbl.xwp

RADAR=$1

yy="$(date -u +%y)"
YY="$(date -u +%Y)"
mm="$(date -u +%m)"
dd="$(date -u +%d)"
date="${yy}${mm}${dd}"
dateY="${YY}${mm}${dd}"
hh="$(date -u +%H)"

GIF="${RADAR}_radar.gif"
rm -f "${GIF}"
DEVICE1="GIF|${GIF}|1024;768"

DATA_DIR="/data/gempak/nexrad/NIDS/${RADAR}/N0B"

# Start from the current date and work backwards for 30 minutes till we
# find a file like N0B_20260619_1257
grid=""
for i in {0..30}; do
    dt="$(date -u -d "-${i} minutes" +'%Y%m%d_%H%M')"
    file="${DATA_DIR}/N0B_${dt}"
    if [ -f "$file" ]; then
        grid="$file"
        hhmm="$(date -u -d "-${i} minutes" +'%H%M')"
        break
    fi
done

area="dsm"
if [ "$RADAR" = "OAX" ]; then
    area="oma"
elif [ "$RADAR" = "DVN" ]; then
    area="dvn"
elif [ "$RADAR" = "FSD" ]; then
    area="fsd"
elif [ "$RADAR" = "ARX" ]; then
    area="lsr"
elif [ "$RADAR" = "EAX" ]; then
    area="mci"
elif [ "$RADAR" = "MPX" ]; then
    area="msp"
fi

sfmap << EOF > "/tmp/${RADAR}_overlay_sfmap.out"
    AREA	= ${area}+
    GAREA	= ${area}+
    DATTIM  = ${date}/${hh}00
    GLEVEL	= 0
    GVCORD   = NONE
    IMCBAR = 4
    SFPARM   = skyc:.6;tmpf<120;wsym:1.2:2;alti;;dwpf<120;;;;brbk:1:1:231
    COLORS   = 32;2;32;0;4;32
    SFFILE   = /data/gempak/surface/${dateY}_sao.gem
    LINE     = 4/1/1
    TEXT     = 1/1
    DEVICE   = ${DEVICE1}
    SATFIL   =
    RADFIL   = ${grid}
    PROJ     = RAD
    CLEAR    = yes
    PANEL	= 0
    TITLE	= 32/-1/~ Mesonet with ${RADAR} NEXRAD @ ${hhmm}
    SCALE	= 0
    GVECT   =
    WIND    =
    LATLON	= 0
    HILO     =
    HLSYM    =
    CLRBAR   = 1
    CONTUR   = 3/3
    SKIP     = 0
    CINT	=
    FINT	=
    FLINE    = 24-12--1
    LUTFIL   = radar.tbl
    STNPLT   =
    MAP     = 25//1 + 25//2
    \$mapfil =HICNUS.NWS + hipowo.cia
    list
    run

    exit
EOF

gpend

if [ -f "${GIF}" ]; then
    pqinsert -p "plot c 000000000000 ${RADAR}_radar.gif bogus gif" "${GIF}" >& /dev/null
    rm -f "${GIF}"
fi
