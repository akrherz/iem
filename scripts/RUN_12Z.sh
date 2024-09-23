# Ensure this is actually being run at 12z, since crontab is in CST/CDT
DOW=$(date +%w)
HH=$(date -u +%H)
if [ "$HH" -ne "12" ]
    then
        exit
fi

cd asos
python cf6_to_iemaccess.py

# On Tuedays, fetch the Sunday update
if [ "$DOW" -eq "2" ]
    then
        cd ../nass
        python ingest_iowa_pdf.py --sunday=$(date --date '2 days ago' +'%Y-%m-%d')
fi

cd ../hads
python compute_hads_pday.py --date=$(date -u --date '1 days ago' +'%Y-%m-%d')

cd ../util
python daily_archive_backup.py &

# Run this twice as to account for some timezones west of Hawaii
cd ../asos
python compute_daily.py
python compute_daily.py --date=$(date -u --date '2 days ago' +'%Y-%m-%d')

cd ../dailyb
python spammer.py

cd ../ingestors/other
python feel_ingest.py

cd ../../util
sh BACKUP.sh

cd ../uscrn
python compute_uscrn_pday.py --date=$(date --date '1 days ago' +'%Y-%m-%d')
python compute_uscrn_pday.py --date=$(date --date '7 days ago' +'%Y-%m-%d')

cd ../yieldfx
python yieldfx_workflow.py
python dump_hybridmaize.py
