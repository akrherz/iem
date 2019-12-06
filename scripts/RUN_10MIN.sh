# Run every 10 minutes please
#set -x

cd current
python vsby.py
python today_precip.py
python today_gust.py
python temperature.py
python today_high.py
python rwis_station.py

cd ../plots
csh MW_overlay.csh

cd ../ingestors
python dot_truckcams.py &

cd ../summary
python update_dailyrain.py

cd ../outgoing
LD_PRELOAD=/opt/miniconda3/envs/prod/lib/libstdc++.so:/opt/miniconda3/envs/prod/lib/libz.so:/opt/miniconda3/envs/prod/lib/libharfbuzz.so php wxc_rwis.php
LD_PRELOAD=/opt/miniconda3/envs/prod/lib/libstdc++.so:/opt/miniconda3/envs/prod/lib/libz.so:/opt/miniconda3/envs/prod/lib/libharfbuzz.so php wxc_awos.php
python madis2csv.py
python wxc_azos_prec.py
python wxc_iarwis_traffic.py
python wxc_iemstage.py IA
python wxc_iemstage.py MN
