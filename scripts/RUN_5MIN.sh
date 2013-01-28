# Run every 5 minutes
cd dl
python radar_composite.py 

cd ../outgoing
python dump_precip.py

cd snetnws
python snet_fe.py &

cd ../../GIS
python 24h_lsr.py 

cd ../current
python lsr_snow_mapper.py >& /dev/null

cd ../ingestors/rwis
./download.csh &

cd ../dotcams
python process.py 

cd ../../q2
python make_raster.py 

# Lets wait a bit now
sleep 60
python hsr.py

cd ../current
python q2_5min_rate.py
python q2_today_total.py
python q2_Xhour.py 1
python q2_Xhour.py 3
python q2_Xhour.py 6
