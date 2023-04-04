# Ensure this is actually being run at 00z, since crontab is in CST/CDT
HH=$(date -u +%H)
if [ "$HH" -ne "00" ]
    then
        exit
fi

cd util
python make_archive_baseline.py

cd ../iemre
# need to run daily analysis for climodat estimator to then work
python daily_analysis.py $(date +'%Y %m %d')

cd ../climodat
python sync_coop_updates.py
python daily_estimator.py $(date +'%Y %m %d')

# Wait a bit, so that more obs can come in
sleep 300

cd ../00z
python awos_rtp.py
python asos_high.py

cd ../asos
python cf6_to_iemaccess.py

cd ../ingestors
python elnino.py

# nexrad N0R and N0Q composites
cd ../summary
python max_reflect.py $(date -u --date '1 days ago' +'%Y %m %d') 0

# Rerun today
cd ../dbutil
python rwis2archive.py $(date -u --date '1 days ago' +'%Y %m %d')

cd ../dl
python download_nldas.py &

cd ../qc
python check_n0q.py

cd ../era5
python fetch_era5.py $(date -u --date '6 days ago' +'%Y %m %d')

cd ../climodat
python era5land_solarrad.py $(date -u --date '7 days ago' +'%Y %m %d')

cd ../iemre
# wait some more so to not collide with other IEMRE processes
sleep 600
python stage4_12z_adjust.py
