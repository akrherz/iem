# Run every 10 minutes please
cd alerts
/mesonet/python/bin/python check_db.py
cd ../current
/mesonet/python/bin/python vsby.py

cd ../delta
/mesonet/python/bin/python gen_15min.py
