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
/mesonet/python/bin/python lsr_snow_mapper.py >& /dev/null

cd ../ingestors/rwis
./download.csh &

cd ../dotcams
python process.py 

#cd ../awos
#/mesonet/python/bin/python parse_idot.py 

cd ../../q2
python make_raster.py 

# Lets wait a bit now
sleep 60
python hsr.py

cd ../current
/mesonet/python/bin/python q2_5min_rate.py
/mesonet/python/bin/python q2_today_total.py
/mesonet/python/bin/python q2_Xhour.py 1
/mesonet/python/bin/python q2_Xhour.py 3
/mesonet/python/bin/python q2_Xhour.py 6
