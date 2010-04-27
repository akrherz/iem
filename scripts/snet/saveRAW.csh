#!/bin/csh
# Copies out the RAW feed data from shared memory
# Daryl Herzmann 11 Jul 2002
#  5 Oct 2002:	If the raw feed is missing, lets restart nwn.py, eh?
# 14 Oct 2002:  What is going on in this script? Disable for now...

set ts=`date +'%Y%m%d_%H'`
set dir="/mesonet/ARCHIVE/raw/snet_feed/`date +'%Y_%m'`" 

cd /dev/shm

if (-e snet.log) then
  mv snet.log snet_${ts}.raw
  gzip snet_${ts}.raw
  if ! (-e ${dir} ) then
    mkdir -p ${dir}
  endif
  mv snet_${ts}.raw.gz $dir 
else
  echo "DARYL!  Where is the schoolnet log!"
  echo "Restart NWN" | mail -s "NWN restart" akrherz@sprintpcs.com
#  kill -9 `pidof -s /usr/bin/python ./nwn.py`
#  cd ~/snet/client
#  ./nwn.py >&! ~/logs/snet.log &
endif
