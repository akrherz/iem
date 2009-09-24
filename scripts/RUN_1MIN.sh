# Run every minute!
cd GIS
/mesonet/python/bin/python attribute2shape.py

cd ../ingestors
/mesonet/python/bin/python parse0006.py
/mesonet/python/bin/python parse0002.py
