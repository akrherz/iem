#!/bin/csh
#set echo
# We want one minute into the future!
set yy=`date --date '1 minute' +%y`
set mm=`date --date '1 minute' +%m`
set dd=`date --date '1 minute' +%d`
set hh=`date --date '1 minute' +%H`

./oa.csh $yy $mm $dd $hh
./IAMESONET_plot.csh $yy $mm $dd $hh
./pres_plot.csh $yy $mm $dd $hh
