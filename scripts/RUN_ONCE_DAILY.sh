# Run once daily
# This runs at 1 AM or so!

cd qc
/mesonet/python/bin/python dailyVtec.py

cd ../outgoing
/mesonet/python/bin/python wxc_moon.py

cd ../dbutil 
/mesonet/python/bin/python ot2archive.py
/mesonet/python/bin/python hads_delete_dups.py

cd ../climodat
/mesonet/python/bin/python daily_estimator.py
/mesonet/python/bin/python compute_ia0000.py
./run.sh >& a
