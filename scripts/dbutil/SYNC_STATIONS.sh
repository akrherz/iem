#!/bin/sh
# Need to sync all our station metadata, when we add new sites!

python set_elevation.py
python set_county.py
python assignClimate.py
python set_wfo.py
python set_timezone.py

python sync_stations.py
python addSiteMesosite.py
