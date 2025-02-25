# Run every 20 minutes please

cd ingestors/madis
python to_iemaccess.py --valid=$(date -u '%Y-%m-%dT%H:%M:00')
python extract_metar.py

cd ../cocorahs
python cocorahs_data_ingest.py

cd ../../other
python ot2archive.py
