#!/bin/csh
#		createGrids.csh
# Script that does OA on surface files
# Daryl Herzmann 09 Jul 2001

source /mesonet/nawips/Gemenviron

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`

set IAGRD="/mesonet/data/gempak/grids/iowa_5km.gem"
set MWGRD="/mesonet/data/gempak/grids/midwest_10km.gem"
set USGRD="/mesonet/data/gempak/grids/us_25km.gem"

# First we need to delete anything out of the current Surface grid
gddelt << EOF > /tmp/createGrids_gddelt.out
  GDFILE = $IAGRD
  GDATTIM = ALL
  GDNUM   = ALL
  GFUNC   = ALL
  GLEVEL  = ALL
  GVCORD  = ALL
  run

  GDFILE = $MWGRD
  run

  GDFILE = $USGRD
  run


  exit
EOF



# Then we ob analyze the data
oabsfc << EOF > /tmp/createGrids_oabsfc.out
  SFFILE   = /mesonet/data/gempak/meso/${date}_meso.gem
  GDFILE   = $IAGRD
  SFPARM   = TMPF;DWPF;PMSL;UWND;VWND;VSBY;ALTM
  DATTIM   = ${date}/${hh}00
  DTAAREA  =
  GUESS    =
  GAMMA    = .3
  SEARCH   = 20/EX
  NPASS    = 2
  QCNTL    = 
  list
  run

  SFFILE = /mesonet/data/gempak/sao/${date}_sao.gem
  GDFILE = $MWGRD
  list
  run

  SFFILE = /mesonet/data/gempak/sao/${date}_sao.gem
  GDFILE = $USGRD
  list
  run

  exit
EOF

gpend
