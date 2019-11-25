#!/bin/bash
# Cache the CPC's Soil Moisture maps
# https://mesonet.agron.iastate.edu/timemachine/#87
# https://mesonet.agron.iastate.edu/timemachine/#88
# https://mesonet.agron.iastate.edu/timemachine/#89
# set -x

DSTAMP=$(date --date '1 day ago' +'%Y%m%d%H%M')

FNS="curr.w.full.daily curr.w.anom.daily curr.w.rank.daily"
for prefix in $FNS; do
    wget -q --timeout=60 -O /tmp/${prefix}_${DSTAMP}.gif https://www.cpc.ncep.noaa.gov/products/Soilmst_Monitoring/Figures/daily/${prefix}.gif
    pqinsert -i -p "plot a ${DSTAMP} bogus cpc/${prefix}.gif gif" /tmp/${prefix}_${DSTAMP}.gif
    rm -f /tmp/${prefix}_${DSTAMP}.gif >& /dev/null
done
exit 0