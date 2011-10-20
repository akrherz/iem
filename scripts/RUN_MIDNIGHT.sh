#!/bin/sh
# Runs at Midnight

cd qc
/mesonet/python/bin/python fixSNETPrecip.py
python check_hilo.py

cd ../dbutil
./save_snet_raw.csh
/mesonet/python/bin/python rwis2archive.py
/mesonet/python/bin/python snet2archive.py

cd ../smos
/mesonet/python/bin/python plot.py 0

# Wait a bit before doing this
sleep 600
cd ../qc
/mesonet/python/bin/python correctGusts.py

python check_station_geom.py