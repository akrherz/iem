
cd delta
./RUN.csh

cd ../summary
/mesonet/python/bin/python snet_hourly_precip.py
/mesonet/python/bin/python update_snet_precip.py

cd ../week
/mesonet/python/bin/python plot_obs.py
