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

cd ../../current
/mesonet/python/bin/python q2_5min_rate.py
