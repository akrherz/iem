#!/bin/bash
# Run every 10 minutes please

cd current || exit 1
python vsby.py
python today_precip.py
python today_gust.py
python temperature.py
python today_high.py
python rwis_station.py

cd ../hads || exit 1
python process_hads_inbound.py &

cd ../dbutil || exit 1
timeout -v 540 python asos2archive.py &
timeout -v 540 python rwis2archive.py &

cd ../ingestors || exit 1
python dot_truckcams.py &

cd dotcams || exit 1
python ingest_dot_webcams.py &

cd ../../summary || exit 1
python update_dailyrain.py

cd ../isusm || exit 1
python isusm2rr5.py

cd ../outgoing || exit 1
python madis2csv.py
