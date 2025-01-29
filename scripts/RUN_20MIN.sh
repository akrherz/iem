# Run every 20 minutes please

cd ingestors/madis
python to_iemaccess.py
python extract_metar.py

cd ../cocorahs
python cocorahs_data_ingest.py

cd ../../other
python ot2archive.py
