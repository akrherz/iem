#!/bin/csh
# Copies out the RAW schoolnet data feed to archived files

set ts=`date +'%Y%m%d_%H'`
set dir="/mesonet/ARCHIVE/raw/snet_feed/`date +'%Y_%m'`" 

cd /mesonet/data/logs

if (-e snet.log) then
  cp snet.log /tmp/snet_${ts}.raw
  echo > snet.log
  cd /tmp
  gzip snet_${ts}.raw
  if ! (-e ${dir} ) then
    mkdir -p ${dir}
  endif
  mv snet_${ts}.raw.gz $dir 
else
  echo "DARYL!  Where is the schoolnet log!"
  echo "snet.log is missing!" | mail -s "NWN restart" akrherz@iastate.edu
endif
