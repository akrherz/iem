#!/bin/sh

cd isuag
sh run_plots.sh

# Run the climodat estimator to get sites that are valid at midnight
# only for Iowa at the moment as we have no other such sites outside of
# Iowa
cd ../climodat
python daily_estimator.py IA

cd ../climodat
sh run.sh &

cd ../coop
python hrrr_solarrad.py
DD=$(date +%d)
if [ $DD -eq "01" ]
	then
	python first_guess_for_harry.py
	python email_iass_report.py monthly
fi
DOY=$(date +%u)
if [ "$DOY" -eq "1" ]
	then
		python email_iass_report.py weekly	
fi

cd ../cache
python warn_cache.py &

cd ../dbutil
python clean_afos.py
python compute_hads_sts.py
python clean_unknown_hads.py
python unknown_stations.py

cd ../ingestors/cocorahs
python redo_day.py IA
python redo_day.py IL

cd ../../windrose
python daily_drive_network.py