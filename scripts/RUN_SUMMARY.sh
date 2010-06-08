# Scripts to run for summary type plots
# Run this only a couple of times per day, probably
#set echo

cd gdd
/mesonet/python/bin/python normal_may1.py

cd ../current
/mesonet/python/bin/python plot_hilo.py 1

cd ../climate
/mesonet/python/bin/python today_hilo.py
/mesonet/python/bin/python today_rec_hilo.py
/mesonet/python/bin/python today_rec_minhi.py

cd ../week
/mesonet/python/bin/python avg_high.py
/mesonet/python/bin/python avg_low.py

cd ../month
/mesonet/python/bin/python obs_precip.py
/mesonet/python/bin/python obs_precip_coop.py
/mesonet/python/bin/python plot_avgt.py
/mesonet/python/bin/python plot_gdd.py
/mesonet/python/bin/python plot_sdd.py

cd ../season
/mesonet/python/bin/python plot_4month_stage4.py

cd ../year
/mesonet/python/bin/python precip.py
/mesonet/python/bin/python plot_gdd.py
/mesonet/python/bin/python plot_gdd.py gdd52

cd ../summary
/mesonet/python/bin/python rwis_daily_summary.py
