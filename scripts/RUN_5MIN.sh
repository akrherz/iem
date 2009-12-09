# Run every 5 minutes
cd dl
/mesonet/python/bin/python radar_composite.py

cd ../GIS
/mesonet/python/bin/python 24h_lsr.py
/mesonet/python/bin/python wwShapefile.py

cd ../current
/mesonet/python/bin/python lsr_snow_mapper.py
