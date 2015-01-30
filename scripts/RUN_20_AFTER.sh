# Run at :20 after the hour

cd ingestors
python soilm_ingest.py

sleep 60
cd ../plots
./RUN_PLOTS
