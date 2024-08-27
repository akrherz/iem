#Run at 40 minutes after the hour, there are some expensive scripts here
YYYY6=$(date -u --date '6 hours ago' +'%Y')
MM6=$(date -u --date '6 hours ago' +'%m')
DD6=$(date -u --date '6 hours ago' +'%d')
HH6=$(date -u --date '6 hours ago' +'%H')

cd dl
python download_ffg.py &
(python download_hrrr_rad.py ; python download_hrrr_tsoil.py) &
python download_nam.py --valid=$(date -u --date '3 hours ago' +'%Y-%m-%dT%H'):00:00 &

cd ../rtma
python wind_power.py &

cd ../qc
python check_webcams.py
python check_isusm_online.py

cd ../iemplot
./RUN.csh

cd ../ingestors/squaw
python ingest_squaw.py

python /opt/iem/scripts/scan/scan_ingest.py &

cd ../madis
python extract_madis.py
python extract_hfmetar.py 0 &
python to_iemaccess.py 2 &

cd ../cocorahs
python cocorahs_stations.py IA
python cocorahs_data_ingest.py IA

cd ../../plots
./RUN_PLOTS
cd black
./surfaceContours.csh

cd ../../model
python motherlode_ingest.py $YYYY6 $MM6 $DD6 $HH6
