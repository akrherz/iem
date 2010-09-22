cd delta
./RUN.csh

cd ../qc
/mesonet/python/bin/python correctGusts.py

cd ../ingestors
/mesonet/python/bin/python beloit.py

cd ../outgoing
php wxc_cocorahs.php

cd ../current
/mesonet/python/bin/python plot_hilo.py 0
/mesonet/python/bin/python q2_today_total.py

cd ../summary
/mesonet/python/bin/python hourly_precip.py
/mesonet/python/bin/python update_snet_precip.py

cd ../week
/mesonet/python/bin/python plot_obs.py

cd ../iemplot
./RUN.csh

cd ../dbutil
/mesonet/python/bin/python asos2archive.py iowa

cd ../plots
./RUN_PLOTS

cd ../iemre
/mesonet/python/bin/python grid_asos.py
/mesonet/python/bin/python grid_asos.py `date -u --date '2 hours ago' +'%Y %m %d %H'`
