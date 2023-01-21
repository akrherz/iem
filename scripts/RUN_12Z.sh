# Ensure this is actually being run at 12z, since crontab is in CST/CDT
HH=$(date -u +%H)
if [ "$HH" -ne "12" ]
	then
		exit
fi

cd asos
python cf6_to_iemaccess.py

# DVN wants this to run at 12:10 UTC, so we start the cron script a bit late
cd ../12z
python awos_rtp.py

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

cd ../ingestors/other
python feel_ingest.py

# Rerun yesterday and today
cd ../../dbutil
python rwis2archive.py $(date -u --date '1 days ago' +'%Y %m %d')
python rwis2archive.py $(date -u +'%Y %m %d')

cd ../other
python ot2archive.py $(date -u --date '1 days ago' +'%Y %m %d')
python ot2archive.py $(date -u +'%Y %m %d')

cd ../util
csh BACKUP.csh

cd ../uscrn
python compute_uscrn_pday.py $(date --date '1 days ago' +'%Y %m %d')
python compute_uscrn_pday.py $(date --date '7 days ago' +'%Y %m %d')

cd ../yieldfx
python yieldfx_workflow.py
python dump_hybridmaize.py
