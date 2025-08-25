# Run every 10 minutes please

cd current
python vsby.py
python today_precip.py
python today_gust.py
python temperature.py
python today_high.py
python rwis_station.py

cd ../hads
python process_hads_inbound.py &

cd ../dbutil
timeout -v 540 python asos2archive.py &
timeout -v 540 python rwis2archive.py &

cd ../ingestors
OPENSSL_CONF=dotcams/openssl.conf python dot_truckcams.py &

cd dotcams
# Le Sigh
OPENSSL_CONF=openssl.conf python ingest_dot_webcams.py &

cd ../../summary
python update_dailyrain.py

cd ../isusm
python isusm2rr5.py

cd ../outgoing
python madis2csv.py
