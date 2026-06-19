#!/bin/bash
#set echo
# We want one minute into the future!
yy="$(date --date '1 minute' +%y)"
mm="$(date --date '1 minute' +%m)"
dd="$(date --date '1 minute' +%d)"
hh="$(date --date '1 minute' +%H)"

bash oa.sh
bash IAMESONET_plot.sh "$yy" "$mm" "$dd" "$hh"
bash pres_plot.sh "$yy" "$mm" "$dd" "$hh"
