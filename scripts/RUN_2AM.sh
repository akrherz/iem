#!/bin/sh

cd isuag
sh run_plots.sh

# Make sure we run this first as we need the data before producing other things
cd ../climodat
python daily_estimator.py IA
python daily_estimator.py KY
python daily_estimator.py IL
python daily_estimator.py IN
python daily_estimator.py OH
python daily_estimator.py MI
python daily_estimator.py WI
python daily_estimator.py MN
python daily_estimator.py ND
python daily_estimator.py SD
python daily_estimator.py NE
python daily_estimator.py KS
python daily_estimator.py MO

cd ../iemre
python daily_analysis.py

cd ../coop
python compute_0000.py

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
python unknown_hads.py

cd ../qc
python check_iem_precip.py
python hads_nwsli_squawk.py

cd ../ingestors/cocorahs
python redo_day.py IA
python redo_day.py IL

cd ../../windrose
python daily_drive_network.py