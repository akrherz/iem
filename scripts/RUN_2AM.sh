#!/bin/sh

cd climodat
/mesonet/python/bin/python daily_estimator.py
/mesonet/python/bin/python compute_ia0000.py
./run.sh >& a

cd ../cache
/mesonet/python/bin/python warn_cache.py

cd ../ingestors/cocorahs
/mesonet/python/bin/python redo_day.py IA
/mesonet/python/bin/python redo_day.py IL
