# Run at 12Z, but needs some manual crontab changing help

# DVN wants this to run at 12:10 UTC, so we start the cron script a bit late
cd 12z
python awos_rtp.py
python asos_low.py

cd ../hads
python compute_hads_pday.py $(date -u --date '1 days ago' +'%Y %m %d')

cd ../util
python daily_archive_backup.py &

# Run this twice as to account for some timezones west of Hawaii
cd ../asos
python compute_daily.py
python compute_daily.py $(date -u --date '2 days ago' +'%Y %m %d')

cd ../dailyb
python spammer.py

cd ../coop
python cfs_extract.py &

cd ../ingestors/other
python feel_ingest.py

# Rerun yesterday and today
cd ../../dbutil
python rwis2archive.py $(date -u --date '1 days ago' +'%Y %m %d')
python rwis2archive.py $(date -u +'%Y %m %d')
python ot2archive.py $(date -u --date '1 days ago' +'%Y %m %d')
python ot2archive.py $(date -u +'%Y %m %d')

cd ../ingestors
DOY=$(date +%u)
if [ "$DOY" -eq "2" ]
	then
		python nass_quickstats.py	
fi

cd ../util
csh BACKUP.csh

cd ../yieldfx
python yieldfx_workflow.py

cd ../dl
python fill_mrms_holes.py
