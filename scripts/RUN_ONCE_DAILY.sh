# Run once daily

cd qc
python check_vtec_eventids.py

cd ../outgoing
python wxc_moon.py

cd ../dbutil 
python ot2archive.py
python hads_delete_dups.py
