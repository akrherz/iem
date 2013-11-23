YYYY6=$(date -u --date '6 hours ago' +'%Y')
MM6=$(date -u --date '6 hours ago' +'%m')
DD6=$(date -u --date '6 hours ago' +'%d')
HH6=$(date -u --date '6 hours ago' +'%H')


cd sbw
python polygonMosaic.py S
sleep 2
python polygonMosaic.py T
sleep 2
python polygonMosaic.py W

cd ../qc
python check_webcams.py

cd ../outgoing
python wxc_iemrivers.py

cd ../iemplot
./RUN.csh

cd ../ingestors/squaw
python ingest_squaw.py

cd ../scan
python scan_ingest.py

cd ../madis
python extractMADIS.py
python extractMetarQC.py

cd ../cocorahs
python cocorahs_stations.py IA
python cocorahs_stations.py IL
python cocorahs_data_ingest.py IL
python cocorahs_data_ingest.py IA

# This is intensive...
cd ../../week
python plot_stage4.py

cd ../plots
./ruc2.csh
./RUN_PLOTS
cd black
./surfaceContours.csh

cd ../../model
python motherlode_ingest.py $YYYY6 $MM6 $DD6 $HH6
