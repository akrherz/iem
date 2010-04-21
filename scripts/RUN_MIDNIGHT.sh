#!/bin/sh
# Runs at Midnight

cd qc
/mesonet/python/bin/python fixSNETPrecip.py

cd ../dbutil
/mesonet/python/bin/python rwis2archive.py
