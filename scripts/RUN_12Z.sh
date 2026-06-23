#!/bin/bash
# Ensure this is actually being run at 12z, since crontab is in CST/CDT
HH=$(date -u +%H)
if [ "$HH" -ne "12" ]
then
    exit
fi

cd asos || exit 1
python cf6_to_iemaccess.py

cd ../hads || exit 1
python compute_hads_pday.py --date="$(date -u --date '1 days ago' +'%Y-%m-%d')"

# Run this twice as to account for some timezones west of Hawaii
cd ../summary || exit 1
python compute_daily.py --date="$(date -u --date '1 days ago' +'%Y-%m-%d')"
python compute_daily.py --date="$(date -u --date '2 days ago' +'%Y-%m-%d')"

cd ../dailyb || exit 1
python spammer.py

cd ../uscrn || exit 1
python compute_uscrn_pday.py --date="$(date --date '1 days ago' +'%Y-%m-%d')"
python compute_uscrn_pday.py --date="$(date --date '7 days ago' +'%Y-%m-%d')"

cd ../yieldfx || exit 1
python yieldfx_workflow.py
python dump_hybridmaize.py
