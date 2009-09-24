# Run every 10 minutes please
cd alerts
/mesonet/python/bin/python check_db.py
cd ../current
/mesonet/python/bin/python vsby.py

cd ../delta
/mesonet/python/bin/python gen_15min.py

cd ../outgoing
php wxc_rwis.php
/mesonet/python/bin/python madis2csv.py
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
