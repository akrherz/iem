# Run at :20 after the hour

cd ingestors
python soilm_ingest.py

sleep 60
cd ../plots
./RUN_PLOTS

cd ../isuag
python isusm2rr5.py

cd ../hads
python compute_hads_pday.py
