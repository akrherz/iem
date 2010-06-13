# Run every 10 minutes please
#set echo

cd alerts
/mesonet/python/bin/python check_db.py
cd ../current
/mesonet/python/bin/python vsby.py
# Can't avoid plots of all zeros producing an error :(
/mesonet/python/bin/python today_precip.py >& /dev/null
/mesonet/python/bin/python today_gust.py
/mesonet/python/bin/python temperature.py
/mesonet/python/bin/python today_high.py
/mesonet/python/bin/python rwis_station.py

cd ../summary
/mesonet/python/bin/python updateRain.py

cd ../delta
/mesonet/python/bin/python gen_15min.py

cd ../outgoing
php wxc_rwis.php
php wxc_awos.php
/mesonet/python/bin/python madis2csv.py
/mesonet/python/bin/python wxc_azos_prec.py
php spider.php

cd kcci
/mesonet/python/bin/python wxc_top5.py
/mesonet/python/bin/python wxc_top5month.py
/mesonet/python/bin/python wxc_top5gusts.py
/mesonet/python/bin/python wxc_top5highs.py
/mesonet/python/bin/python wxc_top5lows.py

/mesonet/python/bin/python wxc_top5myrain.py 2
/mesonet/python/bin/python wxc_top5myrain.py 3
/mesonet/python/bin/python wxc_top5myrain.py 7
/mesonet/python/bin/python wxc_top5myrain.py 14
