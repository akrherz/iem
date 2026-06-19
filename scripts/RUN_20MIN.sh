#!/bin/bash
# Run every 20 minutes please

cd ingestors/madis || exit 1
python to_iemaccess.py --valid="$(date -u --date '2 minutes ago' +'%Y-%m-%dT%H:%M:00')"
python extract_metar.py

cd ../cocorahs || exit 1
python cocorahs_data_ingest.py

cd ../../other || exit 1
python ot2archive.py
