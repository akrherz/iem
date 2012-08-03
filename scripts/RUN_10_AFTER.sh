#
# We are run at :10 after the hour, some of these processes are intensive 
# 
YYYY=$(date -u +'%Y')
MM=$(date -u +'%m')
DD=$(date -u +'%d')
HH=$(date -u +'%H')

cd mos
python current_bias.py NAM
python current_bias.py GFS

cd ../plots
./RUN_PLOTS

cd ../delta
./RUN.csh

cd ../ingestors
python beloit.py

cd ../outgoing
php wxc_cocorahs.php

cd ../current
python plot_hilo.py 0


cd ../summary
python hourly_precip.py
python update_snet_precip.py

cd ../week
/mesonet/python/bin/python plot_obs.py

cd ../iemplot
./RUN.csh

cd ../dbutil
/mesonet/python/bin/python asos2archive.py iowa


cd ../iemre
/mesonet/python/bin/python grid_asos.py
/mesonet/python/bin/python grid_asos.py `date -u --date '2 hours ago' +'%Y %m %d %H'`

cd ../q2
python make_raster_24h.py $YYYY $MM $DD $HH

cd ../smos
python ingest.py
