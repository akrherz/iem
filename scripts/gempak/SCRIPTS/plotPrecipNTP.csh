#!/bin/csh
# Plots the n1p gridded data
# Daryl Herzmann 28 May 2002
# 19 Nov 2002:	Update scale to avoid solids
# 17 Feb 2003:	Use GIF driver
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
set gif="nexradPrecipNTP"

rm -f ${gif}* >& /dev/null

gdplot2_gf << EOF > ../TMP/gdplot2_precip.out
 GDFILE   = ${gdfile}
 GDATTIM  = ${tim0}
 GLEVEL   = 0
 GVCORD   = NONE
 PANEL    = 0
 SKIP     = 0
 SCALE    = 0
 GDPFUN   = NTP
 TYPE     = F
 CONTUR   = 0
 CINT     = 0
 LINE     = 3
 FINT     = 0;.05;.10;.25;.50;.75;1.00;1.25;2.00;3.00;4.00;5.00;6.00;7.00
 FLINE    = 0;0;26-24;21-23;20;18;17;15-7
 HILO     =  
 HLSYM    =  
 CLRBAR   = 1
 WIND     = 
 REFVEC   =  
 TEXT     = 1
 TITLE    = 5/-1/NEXRAD STORM TOTAL THROUGH ${ts}Z
 CLEAR    = YES
 GAREA    = grid
 PROJ     = CED
 MAP      = 1
 LATLON   = 0
 DEVICE   = GIF|${gif}.gif|650;500
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


if (-e ${gif}.gif) then
  #if (${realmm} == "00") then 
  #  /home/ldm/bin/pqinsert -p "plot ac $ftime ${gif}.gif ${gif}_${ts}.gif gif" ${gif}.gif
  #else 
  /home/ldm/bin/pqinsert -p "plot c $ftime ${gif}.gif ${gif}_${ts}.gif gif" ${gif}.gif
  #endif
endif
