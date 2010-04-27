#!/bin/csh
# 17 Feb 2003:	Use GIF driver
#
########################################################

source /mesonet/nawips/Gemenviron

setenv DISPLAY localhost:1
set MONPREC="0309_pmon.gif"
set AREA="40.50;-95.2;43.10;-92.0"

sfmap_gf << EOF > ../TMP/mesoplot_sfmap.out
 AREA     = ${AREA}
 GAREA    = ${AREA}
 SATFIL   =  
 RADFIL   =  
 DATTIM   = 030930/2340
 SFFILE   = /mesonet/ARCHIVE/gempak/surface/snet/2003_09/030930_snet.gem
 COLORS   = 2;0;4;0;32
 LATLON   = 0
 CLEAR    = YES
 PANEL    = 0
 PROJ     = LCC
 FILTER   = NO
 TEXT     = 0.8
 LUTFIL   =  
 STNPLT   =  
 CLRBAR   =  
 MAP     = 25 + 25//2
 \$MAPFIL = HICNUS.NWS + hipowo.cia
 COLORS = 4
 DEVICE = GIF|${MONPREC}|650;600
 TITLE    = 32/-1/2003 September SchoolNet Prec Totals [.01 in]
 SFPARM = PMON
 TEXT   = 1/2///s/c
 list
 run

 exit
EOF
