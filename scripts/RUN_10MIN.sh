# Run every 10 minutes please
cd current
/mesonet/python/bin/python iowa_tmpf.py
cd ../alerts
/mesonet/python/bin/python check_db.py
