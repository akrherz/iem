#!/bin/bash
# Run at 40 minutes after the hour, there are some expensive scripts here

DT6="$(date -u --date '6 hours ago' +'%Y-%m-%dT%H'):00:00"
DT="$(date -u --date '1 hour' +'%Y-%m-%dT%H'):00:00"
DT12="$(date -u --date '12 hours ago' +'%Y-%m-%dT%H'):00:00"

cd dl || exit 1
python download_ffg.py &
(python download_hrrr_rad.py ; python download_hrrr_tsoil.py) &
python download_nam.py --valid="$(date -u --date '3 hours ago' +'%Y-%m-%dT%H'):00:00" &

cd ../rtma || exit 1
python wind_power.py &

cd ../iemre || exit 1
python use_ifs.py --valid="$DT"
python use_ifs.py --valid="$DT12" &

cd ../qc || exit 1
python check_webcams.py
python check_isusm_online.py

cd ../iemplot || exit 1
bash RUN.sh

cd ../ingestors/squaw || exit 1
python ingest_squaw.py

python /opt/iem/scripts/scan/scan_ingest.py &

cd ../madis || exit 1
python extract_madis.py
python extract_hfmetar.py --hours=0 &

cd ../cocorahs || exit 1
python cocorahs_stations.py --newerthan="$(date --date '7 days ago' +'%Y-%m-%d')T00:00:00"

cd ../../plots || exit 1
bash RUN_PLOTS.sh

cd black || exit 1
bash surfaceContours.sh

cd ../../model || exit 1
# set above incase this bleeds into the next hour
python motherlode_ingest.py --valid="$DT6"
