# Run at 12Z, but needs some manual crontab changing help

cd cscap
python email_daily_changes.py

cd ../ingestors
python flux_ingest.py

# Rerun yesterday and today
cd ../dbutil
python rwis2archive.py
python rwis2archive.py 1

cd ../12z
python awos_rtp.py
python asos_low.py

cd ../util
./BACKUP.csh
