
cd dl
/mesonet/python/bin/python ncep_stage4.py

cd ../sbw
/mesonet/python/bin/python polygonMosaic.py S
/mesonet/python/bin/python polygonMosaic.py T
/mesonet/python/bin/python polygonMosaic.py W

cd ../qc
/mesonet/python/bin/python checkWebcam.py

cd ../ingestors/squaw
./ingest.sh

cd ../scan
/mesonet/python/bin/python parse.py
