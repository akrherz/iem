#!/bin/sh

cd isuag
sh run_plots.sh

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
python compute_hads_sts.py

cd ../qc
python hads_nwsli_squawk.py

cd ../ingestors/cocorahs
python redo_day.py IA
python redo_day.py IL

cd ../../windrose
python daily_drive_network.py