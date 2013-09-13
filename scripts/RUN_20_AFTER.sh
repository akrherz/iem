
cd isuag
python check4file.py

cd ../ingestors
python soilm_ingest.py

sleep 60
cd ../plots
./RUN_PLOTS
