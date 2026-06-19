
cd current || exit 1
python plot_hilo.py --date=$(date --date '1 day ago' +'%Y-%m-%d')

cd ../12z || exit 1
python asos_low.py

cd ../climate || exit 1
python today_hilo.py
python today_rec_hilo.py

cd ../month || exit 1
python plot_gdd.py
python obs_precip.py
python obs_precip_coop.py
python plot_avgt.py
python plot_sdd.py

cd ../season || exit 1
python plot_4month_stage4.py
python plot_cli_jul1_snow.py

cd ../year || exit 1
python plot_stage4.py
python precip.py
python plot_gdd.py --gddbase=50
python plot_gdd.py --gddbase=52
python plot_gdd.py --gddbase=48

cd ../gs || exit 1
python plot_gdd.py
