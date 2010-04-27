#!/bin/csh
# Drive schoolnet plot creation
# Daryl Herzmann 11 Feb 2002
# 21 Feb 2002: 	Piggy back the yesterday precip plotter
# 22 Mar 2004	Generate our own GEMPAK file
############################################################
set yymmdd=`date -u +%y%m%d`
source /mesonet/nawips/Gemenviron

./buildSF.py

if (! -e /mesonet/data/gempak/snet/${yymmdd}_snet.gem ) then
  cp /mesonet/scripts/snet/gempak/template.gem /mesonet/data/gempak/snet/${yymmdd}_snet.gem
endif

#cat ~/snet/gempak/header.txt ~/snet/gempak/20${yymmdd}.fil > /tmp/snet.fil
cat /mesonet/scripts/snet/gempak/header.txt sfedit.fil > /tmp/snet.fil

sfedit << EOF > ../TMP/RUN_sfedit.out
  SFFILE = /mesonet/data/gempak/snet/${yymmdd}_snet.gem
  SFEFIL = /tmp/snet.fil
  list
  run

  exit
EOF

./mesoplot.csh ${yymmdd} 2100

#./inject.csh

# Wait 5 more minutes for comparison
sleep 300
./compare.csh
