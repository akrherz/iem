#!/bin/bash
# Finally, the script that plots all of this good data
# Daryl Herzmann 10 November 2000
# 19 Jun 2001:  Modified for use on the new mesonet box
#		Changed Smoothing of Pressure Field
# 02 Jul 2001:  Now we only have 1 GEMPAK file, yeah!
# 30 Jul 2001:	Lets Archive this plot, Eh?
# 31 Oct 2001:	Use 25x25 grid for Surface Contour
# 09 Nov 2001:	Plot ALTM instead of PMSL and use 50x50 grid
# 25 Feb 2002:	Place nicer timestamp on Plot
# 17 Feb 2003:	Use new GIF driver
# 23 Mar 2004	Lets filter more obs
####################################################

. /mesonet/nawips/Gemenviron.profile

export GEMCOLTBL=coltbl.xwp
export DISPLAY=localhost:1

yy=$(date -u --date '1 minute' +'%y')
mm=$(date -u --date '1 minute' +'%m')
dd=$(date -u --date '1 minute' +'%d')
date=${yy}${mm}${dd}
dateY="$(date -u --date '1 minute' +'%Y%m%d')"
hh=$(date -u --date '1 minute' +'%H')
timestamp=$(date -u --date '1 minute' +'%Y%m%d%H00')

nicetime=$(date -d "20${1}-${2}-${3} ${4}:00" +"%b %d %I %p")
generated=$(date +"%b %d %I:%M %p")

GIF="mesonet.gif"
rm -f "${GIF}"
DEVICE="GIF|${GIF}|900;700"
AREA="40.15;-97.1;43.85;-89.9"
LOGFILE="/tmp/IAMESONET_plot.log"
FHOUR_FILE="/mesonet/data/iemplot/fhour.txt"
fhour="F001"
if [ -s "${FHOUR_FILE}" ]; then
    fhour="$(cat "${FHOUR_FILE}")"
fi

# Now we plot
sfmap << EOF > "${LOGFILE}"
    AREA    = ${AREA}
    GAREA    = ${AREA}
    SATFIL   =
    RADFIL   =
    SFPARM   =  skyc:.6;tmpf<120;wsym:1.2:2;alti;;dwpf<120;;;;brbk:1:1:231
    COLORS   =  32;2;32;0;4;32
    DATTIM   =  ${date}/${hh}
    SFFILE   =  /data/gempak/surface/${dateY}_sao.gem
    LATLON   =  0
    TITLE    =  32/-1/GMT: ~ Generated: $generated IEM Plot
    CLEAR    =  yes
    PANEL    =  0
    DEVICE   = ${DEVICE}
    PROJ     =  LCC
    FILTER   =  .5
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
    GDATTIM  = ${date}/${hh}00${fhour}
    GLEVEL   = 0
    GVCORD   = NONE
    GFUNC    = SM9S(PMSL)
    GDFILE   = /mesonet/data/iemplot/grid_25_25.grd
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

if [ ! -f "${GIF}" ]; then
    echo "${GIF} was not crated, here is the log"
    cat $LOGFILE
    exit 1
fi

if [ -f "${GIF}" ]; then
    pqinsert -p "plot ac ${timestamp} mesonet.gif mesonet_${hh}00.gif gif" "${GIF}"
    rm -f "${GIF}"
fi
