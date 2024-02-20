# Ensure this is actually being run at 00z, since crontab is in CST/CDT
HH=$(date -u +%H)
if [ "$HH" -ne "00" ]
    then
        exit
fi

cd util
python make_archive_baseline.py

cd ../00z
# Wait a bit, so that more obs can come in
sleep 300
python generate_rtp.py
python asos_high.py

cd ../ncei
python ingest_climdiv.py &

cd ../iemre
# need to run daily analysis for climodat estimator to then work
python daily_analysis.py --date=$(date +'%Y-%m-%d')

cd ../climodat
python sync_coop_updates.py
python daily_estimator.py --date=$(date +'%Y-%m-%d')

cd ../asos
python cf6_to_iemaccess.py

cd ../ingestors
python elnino.py

# nexrad N0R and N0Q composites
cd ../summary
python max_reflect.py $(date -u --date '1 days ago' +'%Y %m %d') 0

cd ../nldas
python process_nldasv2_noah.py $(date -u --date '5 days ago' +'%Y %m %d') &

cd ../qc
python check_n0q.py

cd ../era5
python fetch_era5.py $(date -u --date '6 days ago' +'%Y %m %d')

cd ../climodat
python era5land_extract.py --valid=$(date -u --date '7 days ago' +'%Y-%m-%d')
python nldas_extract.py --valid=$(date -u --date '6 days ago' +'%Y-%m-%d')

cd ../iemre
# We have hopefully gotten a refreshed 12z stage4 file, so we chunk it again
python stage4_12z_adjust.py $(date +'%Y %m %d')
# Run precip ingest to copy this to IEMRE
python precip_ingest.py --valid12z=$(date +'%Y-%m-%dT12:00:00')
# grid rsds using ERA5Land for 8 days ago, to be safe
python grid_rsds.py $(date -u --date '8 days ago' +'%Y %m %d')
