#!/bin/bash

. /mesonet/nawips/Gemenviron.profile

yy=$(date -u +%y)
mm=$(date -u +%m)
dd=$(date -u +%d)
date=${yy}${mm}${dd}
hh=$(date -u +%H)
dateY="$(date -u +'%Y%m%d')"


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
    SFFILE   = /data/gempak/surface/${dateY}_sao.gem
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
