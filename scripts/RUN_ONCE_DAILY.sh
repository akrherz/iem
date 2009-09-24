# Run once daily
# This runs at 1 AM or so!

cd qc
/mesonet/python/bin/python dailyVtec.py

cd ../outgoing
/mesonet/python/bin/python wxc_moon.py
