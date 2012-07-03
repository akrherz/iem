# Scripts to run for summary type plots
# Run this only a couple of times per day, probably
#set echo

cd gdd
python normal_may1.py

cd ../current
python plot_hilo.py 1

cd ../climate
python today_hilo.py
python today_rec_hilo.py
python today_rec_minhi.py

cd ../week
python avg_high.py
python avg_low.py

cd ../month
/mesonet/python/bin/python obs_precip.py
/mesonet/python/bin/python obs_precip_coop.py
/mesonet/python/bin/python plot_avgt.py
/mesonet/python/bin/python plot_gdd.py
/mesonet/python/bin/python plot_sdd.py

cd ../gs
/mesonet/python/bin/python plot_gdd.py


cd ../season
python plot_4month_stage4.py

cd ../year
python precip.py
python plot_gdd.py
python plot_gdd.py gdd52
python plot_gdd.py gdd48

