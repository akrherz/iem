
cd delta
./RUN.csh

cd ../outgoing
php wxc_cocorahs.php

cd ../current
/mesonet/python/bin/python plot_hilo.py 0

cd ../summary
/mesonet/python/bin/python hourly_precip.py
/mesonet/python/bin/python update_snet_precip.py

cd ../week
/mesonet/python/bin/python plot_obs.py

cd ../iemplot
./RUN.csh
