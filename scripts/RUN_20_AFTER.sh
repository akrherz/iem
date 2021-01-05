# Run at :20 after the hour

cd ingestors/madis
python extract_hfmetar.py 0 &

sleep 60
cd ../../plots
./RUN_PLOTS

cd ../isusm
python agg_1minute.py

cd ../isuag
python isusm2rr5.py

cd ../hads
python compute_hads_pday.py

cd ../ingestors
python uscrn_ingest.py

cd ../uscrn
python compute_uscrn_pday.py
