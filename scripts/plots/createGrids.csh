#!/bin/csh

source /mesonet/nawips/Gemenviron

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`


# First we need to delete anything out of the current Surface grid
gddelt << EOF > /tmp/createGrids_gddelt.out
    GDFILE	= /mesonet/data/gempak/surface50x50.grd
        GDATTIM = ALL
        GDNUM   = ALL
        GFUNC   = ALL
        GLEVEL  = ALL
        GVCORD  = ALL
        list
        run




    exit
EOF



# Then we ob analyze the data
oabsfc << EOF > /tmp/createGrids_oabsfc.out
        SFFILE   = /mesonet/data/gempak/sao/${date}_sao.gem
        GDFILE   = /mesonet/data/gempak/surface50x50.grd
        SFPARM   = TMPF;DWPF;PMSL;UWND;VWND;VSBY;ALTM
        DATTIM   = ${date}/${hh}00
        DTAAREA  =
        GUESS    =
        GAMMA    = .3
        SEARCH   = 49/EX
        NPASS    = 2
        QCNTL    = 10;10
 GDATTIM  = ${date}/${hh}00
 GFUNC    = TMPF;DWPF;PMSL;UWND;VWND;VSBY;ALTM
 GLEVEL   = 0
 GVCORD   = NONE

        list
        run


    exit
EOF

gpend
