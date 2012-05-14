#!/bin/csh

/mesonet/python/bin/python gen_1hour.py

set fp="/tmp/presdelt_`date -u +'%H'`00.png"
set ftime="`date -u +'%Y%m%d%H'`00"
wget -q -O ${fp} http://iem21.local/GIS/apps/delta/plot.php
/home/ldm/bin/pqinsert -p "plot a $ftime bogus $fp png" $fp 
rm $fp
