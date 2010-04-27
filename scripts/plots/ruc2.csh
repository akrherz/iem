#!/bin/csh
# Script that plots RUC2 data, which would give a nice surface analysis
# Daryl Herzmann 18 Dec 2001
#
# Run later in the hour, so that the RUC2 should be in by then and th
#  surface data will be in as well.  Easy does it!!
# 17 Feb 2003:	Use GIF driver
#  3 Jun 2003	Back to the GF driver

source /mesonet/nawips/Gemenviron

setenv DISPLAY localhost:1
set OUTGIF="ruc2_iem_T.gif"

rm -f $OUTGIF >& /dev/null

gdplot2 << EOF > /tmp/ruc2.gdplot2.out
 GDFILE   = RUC2
 GDATTIM  = F000
 GLEVEL   = 2
 GVCORD   = HGHT
 PANEL    = 0
 SKIP     = 0
 SCALE    = 0
 GDPFUN   = TMPF
 TYPE     = P
 CONTUR   = 0
 CINT     = 2
 LINE     = 5
 FINT     = 2
 FLINE    = 27-11
 HILO     =
 HLSYM    =
 CLRBAR   = 1
 WIND     =
 REFVEC   =
 TITLE    = 1/-1/~ RUC2 2m Point Temps [F]
 TEXT     = 1
 CLEAR    = YES
 GAREA    = IA+
 PROJ     = LCC
 MAP      = 1
 LATLON   = 0
 DEVICE   = GF|${OUTGIF}
 STNPLT   =
 SATFIL   =
 RADFIL   =
 LUTFIL   =
 STREAM   =
 POSN     = 0
 COLORS   = 1
 MARKER   = 0
 GRDLBL   = 0
 FILTER   = YES
 list
 run

 exit
EOF

set date=`date -u +%y%m%d`
set hh=`date -u +%H`

sfmap << EOF > /tmp/ruc2.sfmap.out
 AREA     = IA+
 GAREA    = IA+
 SATFIL   =  
 RADFIL   =  
 SFPARM   = TMPF
 DATTIM   = /${hh}00
 SFFILE   = /mesonet/data/gempak/meso/${date}_meso.gem
 COLORS   = 5
 MAP      = 0
 LATLON   = 0
 TITLE    = 5/-2/~ Mesonet Air Temps [F]
 CLEAR    = NO
 PANEL    = 0
 DEVICE   = GF|${OUTGIF}
 PROJ     = LCC
 FILTER   = YES
 TEXT     = 1
 LUTFIL   =  
 STNPLT   =  
 CLRBAR   =  
 list
 run
 
 exit
EOF

gpend

if (-e ${OUTGIF} ) then
  /home/ldm/bin/pqinsert -p "plot c 000000000000 model/$OUTGIF bogus gif" ${OUTGIF} >& /dev/null
#	mv ${OUTGIF} /mesonet/www/html/wx/data/models/

endif

#________________________________________________________________

set OUTGIF="ruc2_iem_Td.gif"


rm -f $OUTGIF >& /dev/null

gdplot2 << EOF > /tmp/ruc2.gdplot2.out
 GDFILE   = RUC2
 GDATTIM  = F000
 GLEVEL   = 2
 GVCORD   = HGHT
 PANEL    = 0
 SKIP     = 0
 SCALE    = 0
 GDPFUN   = DWPF
 TYPE     = P
 CONTUR   = 0
 CINT     = 2
 LINE     = 5
 FINT     = 2
 FLINE    = 27-11
 HILO     =
 HLSYM    =
 CLRBAR   = 1
 WIND     =
 REFVEC   =
 TITLE    = 1/-1/~ RUC2 2m Point Dew Points [F]
 TEXT     = 1
 CLEAR    = YES
 GAREA    = IA+
 PROJ     = LCC
 MAP      = 1
 LATLON   = 0
 DEVICE   = GF|${OUTGIF}
 STNPLT   =
 SATFIL   =
 RADFIL   =
 LUTFIL   =
 STREAM   =
 POSN     = 0
 COLORS   = 1
 MARKER   = 0
 GRDLBL   = 0
 FILTER   = YES
 list
 run

 exit
EOF

set date=`date -u +%y%m%d`
set hh=`date -u +%H`

sfmap << EOF > /tmp/ruc2.sfmap.out
 AREA     = IA+
 GAREA    = IA+
 SATFIL   =  
 RADFIL   =  
 SFPARM   = DWPF
 DATTIM   = /${hh}00
 SFFILE   = /mesonet/data/gempak/meso/${date}_meso.gem
 COLORS   = 5
 MAP      = 0
 LATLON   = 0
 TITLE    = 5/-2/~ Mesonet Air Temps [F]
 CLEAR    = NO
 PANEL    = 0
 DEVICE   = GF|${OUTGIF}
 PROJ     = LCC
 FILTER   = YES
 TEXT     = 1
 LUTFIL   =  
 STNPLT   =  
 CLRBAR   =  
 list
 run
 
 exit
EOF

gpend

if (-e ${OUTGIF} ) then
  /home/ldm/bin/pqinsert -p "plot c 000000000000 model/$OUTGIF bogus gif" ${OUTGIF} >& /dev/null
#	mv ${OUTGIF} /mesonet/www/html/wx/data/models/

endif

#________________________________________________________________




set OUTGIF="ruc2_iem_Rh.gif"

rm -f ${OUTGIF}* >& /dev/null

gdplot2 << EOF > /tmp/ruc2.gdplot2.out
 GDFILE   = RUC2
 GDATTIM  = F000
 GLEVEL   = 2
 GVCORD   = HGHT
 PANEL    = 0
 SKIP     = 0
 SCALE    = 0
 GDPFUN   = RELH
 TYPE     = P
 CONTUR   = 0
 CINT     = 2
 LINE     = 5
 FINT     = 2
 FLINE    = 27-11
 HILO     =
 HLSYM    =
 CLRBAR   = 1
 WIND     =
 REFVEC   =
 TITLE    = 1/-1/~ RUC2 2m Point Relative Humidity [%]
 TEXT     = 1
 CLEAR    = YES
 GAREA    = IA+
 PROJ     = LCC
 MAP      = 1
 LATLON   = 0
 DEVICE   = GF|${OUTGIF}
 STNPLT   =
 SATFIL   =
 RADFIL   =
 LUTFIL   =
 STREAM   =
 POSN     = 0
 COLORS   = 1
 MARKER   = 0
 GRDLBL   = 0
 FILTER   = YES
 list
 run

 exit
EOF

set date=`date -u +%y%m%d`
set hh=`date -u +%H`

sfmap << EOF > /tmp/ruc2.sfmap.out
 AREA     = IA+
 GAREA    = IA+
 SATFIL   =  
 RADFIL   =  
 SFPARM   = RELH
 DATTIM   = /${hh}00
 SFFILE   = /mesonet/data/gempak/meso/${date}_meso.gem
 COLORS   = 5
 MAP      = 0
 LATLON   = 0
 TITLE    = 5/-2/~ Mesonet Air Relative Humidity [%]
 CLEAR    = NO
 PANEL    = 0
 DEVICE   = GF|${OUTGIF}
 PROJ     = LCC
 FILTER   = YES
 TEXT     = 1
 LUTFIL   =  
 STNPLT   =  
 CLRBAR   =  
 list
 run
 
 exit
EOF

gpend

if (-e ${OUTGIF} ) then
  /home/ldm/bin/pqinsert -p "plot c 000000000000 model/$OUTGIF bogus gif" ${OUTGIF} >& /dev/null
#	mv ${OUTGIF} /mesonet/www/html/wx/data/models/

endif

#________________________________________________________________

set OUTGIF="ruc2_iem_V.gif"

rm -f ${OUTGIF}* >& /dev/null

gdplot2 << EOF > /tmp/ruc2.gdplot2.out
 GDFILE   = RUC2
 GDATTIM  = F000
 GLEVEL   = 10
 GVCORD   = HGHT
 PANEL    = 0
 SKIP     = 0
 SCALE    = 0
 GDPFUN   = WND
 TYPE     = b
 CONTUR   = 0
 CINT     = 2
 LINE     = 32
 FINT     = 2
 FLINE    = 27-11
 HILO     =
 HLSYM    =
 CLRBAR   = 1
 WIND     = bk31
 REFVEC   =
 TITLE    = 1/-1/~ RUC2 10m Winds
 TEXT     = 1
 CLEAR    = YES
 GAREA    = IA+
 PROJ     = LCC
 MAP      = 1
 LATLON   = 0
 DEVICE   = GF|${OUTGIF}
 STNPLT   =
 SATFIL   =
 RADFIL   =
 LUTFIL   =
 STREAM   =
 POSN     = 0
 COLORS   = 1
 MARKER   = 1
 GRDLBL   = 0
 FILTER   = YES
 list
 run

 exit
EOF

set date=`date -u +%y%m%d`
set hh=`date -u +%H`

sfmap << EOF > /tmp/ruc2.sfmap.out
 AREA     = IA+
 GAREA    = IA+
 SATFIL   =  
 RADFIL   =  
 SFPARM   = BRBK
 DATTIM   = /${hh}00
 SFFILE   = /mesonet/data/gempak/meso/${date}_meso.gem
 COLORS   = 5
 MAP      = 0
 LATLON   = 0
 TITLE    = 5/-2/~ Mesonet Winds
 CLEAR    = NO
 PANEL    = 0
 DEVICE   = GF|${OUTGIF}
 PROJ     = LCC
 FILTER   = YES
 TEXT     = 1
 LUTFIL   =  
 STNPLT   =  
 CLRBAR   =  
 list
 run
 
 exit
EOF

gpend

if (-e ${OUTGIF} ) then
  /home/ldm/bin/pqinsert -p "plot c 000000000000 model/$OUTGIF bogus gif" ${OUTGIF} >& /dev/null
#	mv ${OUTGIF} /mesonet/www/html/wx/data/models/

endif

./ruc2_plots.csh
