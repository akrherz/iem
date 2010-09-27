
cd 00z
/mesonet/python/bin/python awos_rtp.py

cd ../summary
/mesonet/python/bin/python max_reflect.py

# Rerun today
cd ../dbutil
/mesonet/python/bin/python rwis2archive.py 1



cd ../qc
/mesonet/python/bin/python check5day.py

cd ../iemre
/mesonet/python/bin/python stage4_12z_adjust.py
