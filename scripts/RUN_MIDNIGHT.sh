# Runs at Midnight

cd webalizer
sh processlogs.sh &

cd ../qc
python adjust_snet_precip.py
python check_hilo.py

cd ../dbutil
./save_snet_raw.csh
python rwis2archive.py

cd ../smos
python plot.py 0

# Wait a bit before doing this
sleep 600
cd ../qc
python correctGusts.py
python check_station_geom.py
python check_vtec_eventids.py

cd ../outgoing
python wxc_moon.py

cd ../dbutil 
python ot2archive.py
python hads_delete_dups.py