#!/bin/sh

cd climodat
/mesonet/python/bin/python daily_estimator.py
/mesonet/python/bin/python compute_ia0000.py
./run.sh >& a

