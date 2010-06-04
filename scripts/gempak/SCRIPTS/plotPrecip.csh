#!/bin/csh
# Plots the n1p gridded data
# Daryl Herzmann 28 May 2002
# 17 Feb 2003:	Use GIF driver
# 17 Mar 2003	Keep background from being all messed up...
#############################################

source /mesonet/nawips/Gemenviron

setenv DISPLAY localhost:1

set mm=`date +%M`
if ($mm > 45) then
  set realmm="45"
else if ($mm > 30) then
  set realmm="30"
else if ($mm > 15) then
  set realmm="15"
else
  set realmm="00"
endif


set gdfile="/mesonet/data/gempak/precip/`date -u +'%Y%m%d'`_prec.grd"
set tim0=`date -u +'%y%m%d/%H'`${realmm}
set tim1=`date --date '1 hour ago' +'%d %I:'`${realmm}
set tim2="`date +'%d %I:'`${realmm} `date +'%p'`"
set ts=`date -u +'%H'`${realmm}
set ftime="`date -u +'%Y%m%d%H'`${realmm}"
set gif="nexradPrecip1h"

rm -f ${gif}* >& /dev/null


gdplot2_gf << EOF > ../TMP/plotPrecip_gdplot2.out
 GDFILE   = ${gdfile}
 GDATTIM  = ${tim0}
 GLEVEL   = 0
 GVCORD   = NONE
 PANEL    = 0
 SKIP     = 0
 SCALE    = 0
 GDPFUN   = N1P
 TYPE     = F
 CONTUR   = 0
 CINT     = 0
 LINE     = 3
 FINT     = .01;.05;.10;.25;.50;.75;1.00;1.25;1.50;1.75;2.00;3.00
 FLINE    = 0;26;24;21;22;23;20;18-16;14-10;0
 HILO     =  
 HLSYM    =  
 CLRBAR   = 1 
 WIND     = 
 REFVEC   =  
 TEXT     = 1
 TITLE    = 5/-1/NEXRAD ESTIMATED PRECIP ${tim1} - ${tim2}
 CLEAR    = YES
 GAREA    = grid
 PROJ     = MER
 MAP      = 1
 LATLON   = 0
 DEVICE   = GF|${gif}.gif|650;500
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

 DEVICE   = GF|${gif}2.gif|800;800
 TITLE	= 0
 CLRBAR = 0
 list 
 run

 exit
EOF


if (-e ${gif}.gif) then
  if (${realmm} == "00") then
    /home/ldm/bin/pqinsert -p "plot ac $ftime ${gif}.gif ${gif}_${ts}.gif gif" ${gif}.gif
  else 
    /home/ldm/bin/pqinsert -p "plot c $ftime ${gif}.gif ${gif}_${ts}.gif gif" ${gif}.gif
  endif
endif
