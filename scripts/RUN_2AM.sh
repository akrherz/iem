#!/bin/sh
DD=$(date +%d)

cd isusm
bash run_plots.sh
python backfill_summary.py &
if [ $DD -eq "07" ]
    then
        python nmp_monthly_email.py
fi
python fix_high_low.py --date=$(date --date '1 days ago' +'%Y-%m-%d')
python fix_high_low.py --date=$(date --date '10 days ago' +'%Y-%m-%d')

cd ../swat
python swat_realtime.py &

# Run the climodat estimator to get sites that are valid at midnight
cd ../climodat
python daily_estimator.py --date=$(date --date '1 days ago' +'%Y-%m-%d')
python compute_climate.py --date=$(date --date '1 days ago' +'%Y-%m-%d')

# Look for stuff we missed with noaaport ingest
cd ../rtma
python rtma_backfill.py --date=$(date --date '3 days ago' +'%Y-%m-%d')

cd ../climodat
bash run.sh &

cd ../coop
if [ $DD -eq "01" ]
    then
    python first_guess_for_harry.py
fi

cd ../util
if [ $DD -eq "02" ]
    then
        bash monthly.sh $(date --date '3 days ago' +'%y %m')
fi

cd ../dl
if [ $DD -eq "09" ]
    then
         python download_narr.py --year=$(date --date '13 days ago' +%Y) --month=$(date --date '13 days ago' +%m) &
fi
python fetch_power.py --year=$(date --date '7 days ago' +'%Y') --domain=
python fetch_power.py --year=$(date --date '7 days ago' +'%Y') --domain=china
python fetch_power.py --year=$(date --date '7 days ago' +'%Y') --domain=europe
cd ../climodat
python power_extract.py &

cd ../cache
python warn_cache.py &

cd ../dbutil
python clean_afos.py
python clean_telemetry.py
python clean_mos.py &
python compute_hads_sts.py
python clean_unknown_hads.py
python unknown_stations.py

cd ../ingestors/ncei
if [ $DD -eq "15" ]
    then
    python ingest_fisherporter.py
fi

cd ../../windrose
python daily_drive_network.py &

cd ../yieldfx
python psims_baseline.py --date=$(date --date '1 days ago' +'%Y-%m-%d')
python psims_baseline.py --date=$(date --date '8 days ago' +'%Y-%m-%d')

cd ../prism
python ingest_prism.py --date=$(date --date '7 days ago' +'%Y-%m-%d')
python ingest_prism.py --date=$(date --date '60 days ago' +'%Y-%m-%d')
python ingest_prism.py --date=$(date --date '365 days ago' +'%Y-%m-%d')

cd ../hads
python sync_idpgis.py
