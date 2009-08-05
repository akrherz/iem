# Run every 10 minutes please
cd alerts
/mesonet/python/bin/python check_db.py
cd ../current
/mesonet/python/bin/python vsby.py
