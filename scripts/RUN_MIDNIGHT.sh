#!/bin/sh
# Runs at Midnight

cd qc
/mesonet/python/bin/python fixSNETPrecip.py
/mesonet/python/bin/python check_hilo.py

cd ../dbutil
./save_snet_raw.csh
/mesonet/python/bin/python rwis2archive.py
/mesonet/python/bin/python snet2archive.py
