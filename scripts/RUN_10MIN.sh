# Run every 10 minutes please
#set -x

cd current
python vsby.py
python today_precip.py
python today_gust.py
python temperature.py
python today_high.py
python rwis_station.py

cd ../dbutil
timeout 540 python asos2archive.py &

cd ../plots
csh MW_overlay.csh

cd ../ingestors
python dot_truckcams.py &

cd dotcams
python ingest_dot_webcams.py &

cd ../../summary
python update_dailyrain.py

cd ../outgoing
php wxc_rwis.php
php wxc_awos.php
python madis2csv.py
python wxc_azos_prec.py
python wxc_iarwis_traffic.py
python wxc_iemstage.py IA
python wxc_iemstage.py MN
