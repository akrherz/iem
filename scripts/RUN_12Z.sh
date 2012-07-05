# Run at 12Z, but needs some manual crontab changing help

cd cscap
python email_daily_changes.py

cd ../ingestors
/mesonet/python/bin/python flux_ingest.py

# Rerun yesterday and today
cd ../dbutil
/mesonet/python/bin/python rwis2archive.py
/mesonet/python/bin/python rwis2archive.py 1

cd ../12z
/mesonet/python/bin/python awos_rtp.py
/mesonet/python/bin/python asos_low.py

cd ../util
./BACKUP.csh
