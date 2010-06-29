#!/bin/csh
# Copies out the RAW feed data from shared memory
# Daryl Herzmann 11 Jul 2002
#  5 Oct 2002:	If the raw feed is missing, lets restart nwn.py, eh?
# 14 Oct 2002:  What is going on in this script? Disable for now...

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
  echo "/dev/shm/snet.log is missing!" | mail -s "NWN restart" akrherz@iastate.edu
endif
