# Run every 10 minutes please
#set -x

cd current
python vsby.py
python today_precip.py
python today_gust.py
python temperature.py
python today_high.py
python rwis_station.py

cd ../summary
python updateRain.py

cd ../delta
python gen_15min.py

cd ../outgoing
php wxc_rwis.php
php wxc_awos.php
python madis2csv.py
python wxc_azos_prec.py
php spider.php
python wxc_iarwis_traffic.py

cd kcci
python wxc_top5.py
python wxc_top5month.py
python wxc_top5gusts.py
python wxc_top5highs.py
python wxc_top5lows.py

python wxc_top5myrain.py 2
python wxc_top5myrain.py 3
python wxc_top5myrain.py 7
python wxc_top5myrain.py 14
