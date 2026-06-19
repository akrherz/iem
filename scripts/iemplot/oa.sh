#!/bin/bash

. /mesonet/nawips/Gemenviron.profile


hh="$(date -u --date '1 minute' +'%H')"
yyyymmddhh_1h="$(date -u --date '1 hour ago' +'%Y%m%d%H')"
yyyymmddhh_2h="$(date -u --date '2 hour ago' +'%Y%m%d%H')"

if [ ! -e /mesonet/data/iemplot/grid_25_25.grd ]; then
    echo "Missing grid_25_25.grd, copying template over..."
    cp templates/grid_25_25.grd /mesonet/data/iemplot/
fi

if [ ! -e /mesonet/data/iemplot/surface.gem ]; then
    echo "Missing surface.gem, copying template over..."
    cp templates/surface.gem /mesonet/data/iemplot/
fi


gddelt << EOF > /tmp/oa_gddelt.out
    GDFILE = /mesonet/data/iemplot/grid_25_25.grd
    GDATTIM = ALL
    GLEVEL = ALL
    GVCORD = ALL
    GFUNC = ALL
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

gdbiint << EOF > /tmp/oa_gdbiint.out
    GDFILE   = $gdfile
    GDOUTF   = /mesonet/data/iemplot/grid_oa.grd
    GFUNC    = PMSL
    GLEVEL   = 0
    GVCORD   = NONE
    GDATTIM  = ${fhour}
    GDNUM    =
    list
    run

    exit
EOF

gddiag << EOF > /tmp/oa_gddiag.out
    GDFILE = /mesonet/data/iemplot/grid_oa.grd
    GDOUTF = /mesonet/data/iemplot/grid_oa.grd
    GFUNC  = PMSL
    GDATTIM = ${fhour}
    GLEVEL  = 0
    GVCORD = NONE
    GRDNAM = ALTM
    GPACK =
    list
    run

    exit
EOF

sfdelt << EOF > /tmp/oa_sfdelt.out
    SFFILE = /mesonet/data/iemplot/surface.gem
    DATTIM = ALL
    AREA   = DSET
    list
    run

    exit
EOF

python dump_altm.py

sfedit << EOF > /tmp/oa_sfedit.out
    SFEFIL   = /mesonet/data/iemplot/altm.txt
    SFFILE   = /mesonet/data/iemplot/surface.gem
    list
    run

    exit
EOF

oabsfc << EOF > /tmp/oa_oabsfc.out
    SFFILE = /mesonet/data/iemplot/surface.gem
    GDFILE   = /mesonet/data/iemplot/grid_25_25.grd
    SFPARM   = ALTM
    DATTIM   = /${hh}
    DTAAREA  = ia
    GDATTIM = ${fhour}
    GUESS    =
    GUESFUN =
    GAMMA    = .3
    SEARCH   = 10/EX
    NPASS    = 2
    QCNTL    = 3
    list
    run

    exit
EOF

gpend
