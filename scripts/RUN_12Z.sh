
cd ingestors
/mesonet/python/bin/python flux_ingest.py

# Rerun yesterday and today
cd ../dbutil
/mesonet/python/bin/python rwis2archive.py
/mesonet/python/bin/python rwis2archive.py 1

cd ../12z
/mesonet/python/bin/python awos_rtp.py

cd ../qc
/mesonet/python/bin/python check5day.py
