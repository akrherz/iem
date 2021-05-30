#set -x

cd current
python plot_hilo.py $(date --date '1 day ago' +'%Y %m %d')

cd ../12z
python asos_low.py

cd ../climate
python today_hilo.py
python today_rec_hilo.py

cd ../month
python plot_gdd.py
python obs_precip.py
python obs_precip_coop.py
python plot_avgt.py
python plot_sdd.py

cd ../season
python plot_4month_stage4.py
python plot_cli_jul1_snow.py

cd ../year
python plot_stage4.py
python precip.py
python plot_gdd.py 50
python plot_gdd.py 52
python plot_gdd.py 48

cd ../gs
python plot_gdd.py
