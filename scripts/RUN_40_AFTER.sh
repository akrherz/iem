YYYY6=$(date -u --date '6 hours ago' +'%Y')
MM6=$(date -u --date '6 hours ago' +'%m')
DD6=$(date -u --date '6 hours ago' +'%d')
HH6=$(date -u --date '6 hours ago' +'%H')

cd dl
python ncep_stage4.py

cd ../sbw
python polygonMosaic.py S
sleep 2
python polygonMosaic.py T
sleep 2
python polygonMosaic.py W

cd ../iemre
python stage4_hourlyre.py
python stage4_hourlyre.py `date -u --date '3 hours ago' +'%Y %m %d %H'`
python stage4_hourlyre.py `date -u --date '1 day ago' +'%Y %m %d %H'`

cd ../current
python stage4_hourly.py
python stage4_today_total.py
python stage4_Xhour.py 24
python stage4_Xhour.py 48

cd ../qc
python check_webcams.py

cd ../outgoing
python wxc_iemrivers.py

cd ../iemplot
./RUN.csh

cd ../ingestors/squaw
./ingest.sh

cd ../scan
python scan_ingest.py

cd ../raws
./download.csh

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
python ingest.py $YYYY6 $MM6 $DD6 $HH6
