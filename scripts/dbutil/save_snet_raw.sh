#!/bin/bash
# Copies out the RAW schoolnet data feed to archived files
# Called from RUN_MIDNIGHT.sh

ts=$(date +'%Y%m%d_%H')
basedir=$(date +'%Y_%m')
mydir="/mesonet/ARCHIVE/raw/snet_feed/$basedir" 

cd /mesonet/data/logs

if [ -f snet.log ]; then
	cp snet.log /tmp/snet_${ts}.raw
	echo > snet.log
	cd /tmp
	gzip snet_${ts}.raw
	mkdir -p ${mydir}
	mv snet_${ts}.raw.gz $mydir 
else
	echo "DARYL!  Where is the schoolnet log!"
	echo "snet.log is missing!" | mail -s "NWN restart" akrherz@iastate.edu
fi
