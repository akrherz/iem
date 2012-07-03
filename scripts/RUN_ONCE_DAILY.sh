# Run once daily

cd qc
python check_vtec_eventids.py

cd ../outgoing
python wxc_moon.py

cd ../dbutil 
/mesonet/python/bin/python ot2archive.py
/mesonet/python/bin/python hads_delete_dups.py
