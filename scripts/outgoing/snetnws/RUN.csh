#!/bin/tcsh
# Script to generate SNET metar and insert
# Daryl Herzmann 29 Mar 2002
# 11 Apr 2002:	Run ALL at once
# 07 Jun 2002:  Do a database insert as well.
# 18 Jun 2002:	Zip up the Shapefile and move
# 25 Jul 2002:	Change name of schoolnet sao file to .sao
# 26 Jul 2002:	 -- And change to yet another name
#  5 Aug 2002:  Insert new sao format!
#  4 Nov 2002:	Also add localRR5.dat which has the headers...
# 22 Aug 2003	Alert my cell phone, when the SchoolNet is down! :(
# 27 Oct 2003	Restart server if something goes bad
###############################################

#echo "FIXME"
#exit

set TS=`date -u +%d%H%M`
set mm=`date +'%M'`

/mesonet/python/bin/python snet_fe.py

mv snet.sao IA.snet${TS}.sao
#mv snet2.sao IA.snet${TS}.sao

#echo "Inserting snet${TS}.dat"
/home/ldm/bin/pqinsert IA.snet${TS}.sao
#/home/ldm/bin/pqinsert IA.snet${TS}.sao

rm -f IA.snet${TS}.sao

set len=`wc -l snet.csv | awk '{print $1}'`


if (${len} > 6) then
  #echo "Inserting snet.csv"
  /home/ldm/bin/pqinsert snet.csv
  /home/ldm/bin/pqinsert kelo.csv
else
  #echo "SchoolNet Missing ${TS}" | mail -s "SNET MISSING" -c akrherz@sprintpcs.com akrherz@iastate.edu
  echo "SchoolNet Missing ${TS}" | mail -s "SNET MISSING" akrherz@iastate.edu
endif

#rm snet.csv

if ($mm == 15) then
    /home/ldm/bin/pqinsert -p "SUADSMRR5DMX.dat" LOCDSMRR5DMX.dat
endif
if ($mm == 35) then
    /home/ldm/bin/pqinsert -p "SUADSMRR5DMX.dat" LOCDSMRR5DMX.dat
endif

if ($mm == 55) then
  set len=`wc -l SUADSMRR5DMX.dat | awk '{print $1}'`
  if (${len} > 6 ) then
    /home/ldm/bin/pqinsert SUADSMRR5DMX.dat
  else
    echo "Missing SNET SHEF" | mail -s "SHEF SNET missing" akrherz@iastate.edu
  endif
endif


if ($mm == 55 ) then
  set len=`wc -l SUAFSDRR5FSD.dat | awk '{print $1}'`
  if (${len} > 6 ) then
    /home/ldm/bin/pqinsert SUAFSDRR5FSD.dat
  else
    echo "Missing SNET SHEF" | mail -s "SHEF SNET missing" akrherz@iastate.edu
  endif

endif



rm -f SUADMXRR5DMX.dat

if (-e snet_current.shp) then
  zip -q snet_current.zip snet_current.shp snet_current.shx snet_current.dbf
  mv snet_current.shp snet_current.shx snet_current.dbf snet_current.zip /mesonet/www/html/GIS/data/datasets/
  rm -f snet_current.shp snet_current.shx snet_current.dbf
endif
