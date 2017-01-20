# Run at :20 after the hour

cd ingestors
python soilm_ingest.py

cd madis
python extract_hfmetar.py 0 &

cd ../other
python cobs_ingest.py

sleep 60
cd ../../plots
./RUN_PLOTS

cd ../isuag
python isusm2rr5.py

cd ../dbutil
python asos2archive.py hourly

cd ../hads
python compute_hads_pday.py
