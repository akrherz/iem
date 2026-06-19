#!/bin/bash

. /mesonet/nawips/Gemenviron.profile

export GEMCOLTBL=coltbl.xwp
export DISPLAY="localhost:1"

yy="$(date -u +%y)"
mm="$(date -u +%m)"
dd="$(date -u +%d)"
date="${yy}${mm}${dd}"
dateY="$(date -u +%Y%m%d)"
hh="$(date -u +%H)"
yyyymmddhh_1h="$(date -u --date '1 hour ago' +'%Y%m%d%H')"
yyyymmddhh_2h="$(date -u --date '2 hour ago' +'%Y%m%d%H')"

GIF="mesonet.gif"
rm -f "${GIF}"
DEVICE="GIF|${GIF}|1024;768"
AREA="42.6;-104.5;46;-96"
LOGFILE="/tmp/SDMESONET_sfmap.out"

# Now we plot
sfmap << EOF > ${LOGFILE}
    AREA    = ${AREA}
    GAREA    = ${AREA}
    SATFIL   =
    RADFIL   =
    SFPARM   =  skyc:.6;tmpf<120;wsym:1.2:2;alti;;dwpf<120;;;;brbk:1:1:231
    COLORS   =  32;2;32;0;4;32
    DATTIM   =  ${date}/${hh}
    SFFILE   =  /data/gempak/surface/${dateY}_sao.gem
    LATLON   =  0
    TITLE    =  32/-1/GMT: ~ South Dakota Mesonet Data
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

gdfile="/data/gempak/model/hrrr/${yyyymmddhh_1h}_hrrr.gem"
fhour="F001"
if [ ! -e "${gdfile}" ]; then
    gdfile="/data/gempak/model/hrrr/${yyyymmddhh_2h}_hrrr.gem"
    fhour="F002"
fi

gdcntr << EOF >> ${LOGFILE}
    GAREA    = ${AREA}
    GDATTIM  = ${fhour}
    GLEVEL   = 0
    GVCORD   = NONE
    GFUNC    = SM9S(PMSL)
    GDFILE   = ${gdfile}
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
    TITLE	= 32/-2/~ HRRR PMSL
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

if [ -e "${GIF}" ]; then
    pqinsert -p "plot c 000000000000 SD/${GIF} bogus gif" "${GIF}" >& /dev/null
    rm -f "${GIF}"
fi
