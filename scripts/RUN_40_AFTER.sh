
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

cd ../iemplot
./RUN.csh

cd ../ingestors/squaw
./ingest.sh

cd ../scan
/mesonet/python/bin/python parser.py

cd ../raws
./download.csh

cd ../madis
/mesonet/python/bin/python extractMADIS.py
/mesonet/python/bin/python extractMetarQC.py

cd ../cocorahs
/mesonet/python/bin/python stations.py IA
/mesonet/python/bin/python stations.py IL
/mesonet/python/bin/python process.py IL
/mesonet/python/bin/python process.py IA

# This is intensive...
cd ../../week
/mesonet/python/bin/python plot_stage4.py
