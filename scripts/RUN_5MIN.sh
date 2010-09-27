# Run every 5 minutes
cd dl
/mesonet/python/bin/python radar_composite.py

cd ../GIS
/mesonet/python/bin/python 24h_lsr.py
/mesonet/python/bin/python wwShapefile.py

cd ../current
/mesonet/python/bin/python lsr_snow_mapper.py >& /dev/null

cd ../outgoing/snetnws
./RUN.csh

cd ../../ingestors/rwis
./download.csh

cd ../dotcams
/mesonet/python/bin/python process.py

cd ../awos
/mesonet/python/bin/python parse_idot.py

# Lets wait a bit now
sleep 60

cd ../../current
/mesonet/python/bin/python q2_5min_rate.py
/mesonet/python/bin/python q2_today_total.py
/mesonet/python/bin/python q2_Xhour.py 1
/mesonet/python/bin/python q2_Xhour.py 3
/mesonet/python/bin/python q2_Xhour.py 6