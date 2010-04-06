# Run every minute!
cd GIS
/mesonet/python/bin/python attribute2shape.py

cd ../ingestors
/mesonet/python/bin/python parse0006.py
/mesonet/python/bin/python parse0002.py
/mesonet/python/bin/python awos_adas.py

cd ../outgoing
/mesonet/python/bin/python snet_collect.py

cd ../ingestors/sn
/mesonet/python/bin/python parser.py
