# Run at :20 after the hour

cd ingestors
python soilm_ingest.py

cd ../isuag
python isusm2rr5.py

sleep 60
cd ../plots
./RUN_PLOTS
