# Run at :20 after the hour

cd ingestors/madis
python extract_hfmetar.py 0 &

cd ../other
python cobs_ingest.py

sleep 60
cd ../../plots
./RUN_PLOTS

cd ../isuag
python agg_1minute.py
python isusm2rr5.py

cd ../dbutil
python asos2archive.py hourly

cd ../hads
python compute_hads_pday.py

cd ../ingestors
python uscrn_ingest.py
