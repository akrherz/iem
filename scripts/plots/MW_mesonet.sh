#!/bin/bash
# Called from RUN_59_AFTER.sh and HOURLY_PLOTS

. /mesonet/nawips/Gemenviron.profile

export GEMCOLTBL=coltbl.xwp
export DISPLAY=localhost:1

YYYYmmdd="$(date -u --date '1 minute' +'%Y%m%d')"
yy=$(date -u --date '1 minute' +%y)
mm=$(date -u --date '1 minute' +%m)
dd=$(date -u --date '1 minute' +%d)
date=${yy}${mm}${dd}
hh=$(date -u --date '1 minute' +%H)
timestamp=$(date -u --date '1 minute' +'%Y%m%d%H00')
yyyymmddhh_1h=$(date -u --date '1 hour ago' +'%Y%m%d%H')
yyyymmddhh_2h=$(date -u --date '2 hour ago' +'%Y%m%d%H')

GIF="MWmesonet.gif"
DEVICE="GIF|${GIF}|1024;768"
AREA="37;-105;48.5;-85"
LOGFILE="/tmp/MW_mesonet.out"

# Ensure our output file does not exist, otherwise GEMPAK will be naughty
if [ -e ${GIF} ]; then
    rm ${GIF}
fi

# Now we plot
sfmap << EOF > ${LOGFILE}
    AREA    = ${AREA}
    GAREA	= ${AREA}
    SATFIL   =
    RADFIL   =
    SFPARM   =  skyc:.6;tmpf;wsym:1.2:2;alti;;dwpf;;;;brbk:0.8:1:231
    COLORS   =  32;2;32;0;(50;70/4;23;23/DWPF);32
    DATTIM   =  ${date}/${hh}
    SFFILE   =  /data/gempak/surface/${YYYYmmdd}_sao.gem
    LATLON   =  0
    TITLE    =  32/-1/~ MidWest Mesonet Data
    CLEAR    =  yes
    PANEL    =  0
    DEVICE   = ${DEVICE}
    PROJ     =  LCC
    FILTER   =  .5
    TEXT     = 1
    LUTFIL   =
    STNPLT   =
    CLRBAR =
    MAP	= 25 + 25//2
    \$MAPFIL = HICNUS.NWS + hipowo.cia
    list
    run

    exit
EOF

gdfile="/data/gempak/model/hrrr/${yyyymmddhh_1h}_hrrr.gem"
fhour="F001"
if [ ! -e ${gdfile} ]; then
    gdfile="/data/gempak/model/hrrr/${yyyymmddhh_2h}_hrrr.gem"
    fhour="F002"
fi


gdcntr << EOF >> ${LOGFILE}
    AREA	= ${AREA}
    GAREA    = ${AREA}
    GDATTIM  = ${fhour}
    GLEVEL   = 0
    GVCORD   = NONE
    GFUNC    = SM9S(PMSL)
    GDFILE   = $gdfile
    CINT     = 4
    LINE     = 4
    MAP      = 0
    TEXT     = 1
    DEVICE   = ${DEVICE}
    SATFIL   =
    RADFIL   =
    PROJ     = LCC
    CLEAR    = no
    PANEL	= 0
    TITLE	= 32/-2/^ HRRR PMSL
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

if [ -e ${GIF} ]; then
  pqinsert -p "plot ac $timestamp ${GIF} MWmesonet_${hh}00.gif gif" ${GIF} >& /dev/null
  rm ${GIF}
fi

