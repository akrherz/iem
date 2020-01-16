#set echo

cd current
python plot_hilo.py 1

cd ../12z
python asos_low.py

cd ../climate
python today_hilo.py
python today_rec_hilo.py

cd ../month
python obs_precip.py
python obs_precip_coop.py
python plot_avgt.py
python plot_gdd.py
python plot_sdd.py

cd ../gs
python plot_gdd.py


cd ../season
python plot_4month_stage4.py
python plot_cli_jul1_snow.py

cd ../year
python precip.py
python plot_gdd.py
python plot_gdd.py gdd52
python plot_gdd.py gdd48
