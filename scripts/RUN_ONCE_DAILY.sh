# Run once daily

cd qc
/mesonet/python/bin/python dailyVtec.py

cd ../outgoing
/mesonet/python/bin/python wxc_moon.py

cd ../dbutil 
/mesonet/python/bin/python ot2archive.py
/mesonet/python/bin/python hads_delete_dups.py
