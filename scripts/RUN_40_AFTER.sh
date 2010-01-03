
cd dl
/mesonet/python/bin/python ncep_stage4.py

cd ../sbw
/mesonet/python/bin/python polygonMosaic.py S
sleep 4
/mesonet/python/bin/python polygonMosaic.py T
sleep 4
/mesonet/python/bin/python polygonMosaic.py W

cd ../qc
/mesonet/python/bin/python checkWebcam.py

cd ../outgoing
/mesonet/python/bin/python wxc_iemrivers.py

cd ../ingestors/squaw
./ingest.sh

cd ../scan
/mesonet/python/bin/python parser.py

cd ../raws
./download.csh

# This is intensive...
cd ../../week
/mesonet/python/bin/python plot_stage4.py
