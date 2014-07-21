#!/bin/csh
#set echo
# We want one minute into the future!
set yy=`date --date '1 minute' +%y`
set mm=`date --date '1 minute' +%m`
set dd=`date --date '1 minute' +%d`
set hh=`date --date '1 minute' +%H`

csh oa.csh $yy $mm $dd $hh
csh IAMESONET_plot.csh $yy $mm $dd $hh
csh pres_plot.csh $yy $mm $dd $hh
