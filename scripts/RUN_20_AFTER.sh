# Run at :20 after the hour

cd ingestors
python soilm_ingest.py

cd madis
python extract_hfmetar.py 0 &

sleep 60
cd ../../plots
./RUN_PLOTS

cd ../isuag
python isusm2rr5.py

cd ../hads
python compute_hads_pday.py
