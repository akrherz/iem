
cd ingestors
/mesonet/python/bin/python flux_ingest.py

# Rerun yesterday and today
cd ../dbutil
/mesonet/python/bin/python rwis2archive.py
/mesonet/python/bin/python rwis2archive.py 1
