# Run at 40 minutes after the hour, there are some expensive scripts here

DT6="$(date -u --date '6 hours ago' +'%Y-%m-%dT%H'):00:00"

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
python extract_hfmetar.py --hours=0 &
python to_iemaccess.py --valid=$(date -u --date '2 hours ago' +'%Y-%m-%dT%H:%M:00') &

cd ../cocorahs
python cocorahs_stations.py --newerthan=$(date --date '7 days ago' +'%Y-%m-%d')T00:00:00

cd ../../plots
./RUN_PLOTS
cd black
./surfaceContours.csh

cd ../../model
# set above incase this bleeds into the next hour
python motherlode_ingest.py --valid=$DT6
