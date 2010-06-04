#!/bin/csh
# 		gridPrecip.csh
#  Grid RADAR estimates of precip onto a 2km grid
#  Daryl Herzmann 28 May 2002
# 05 Jun 2002:	Also do NTP, makes the files a bit larger
#
########################################################

source /mesonet/nawips/Gemenviron

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

cd /mesonet/data/gempak/precip

set gdfile="`date -u +'%Y%m%d'`_prec.grd"

if (! -e ${gdfile} ) then
  cp /mesonet/data/gempak/precip/template.grd ${gdfile}
endif

set tim0=`date -u +'%y%m%d/%H'`${realmm}

gdradr << EOF > /tmp/gdradr_precip.log
 GRDAREA  = IA+
 PROJ     = MER
 KXKY     = 380;250
 GDFILE   = ${gdfile}
 RADTIM   = ${tim0}
 GDPFUN   = N1P
 RADDUR   = 15
 RADFRQ   =
 CPYFIL   =
 MAXGRD   = 200
 RADMODE  = PC
 NDVAL    = 
 STNFIL   = nexrad.tbl
 list
 run

 GDPFUN	= NTP
 list
 run

 exit
EOF

cd /mesonet/scripts/gempak/SCRIPTS

./plotPrecip.csh
./plotPrecipNTP.csh
#./plotPrecipGIS.csh
