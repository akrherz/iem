#!/bin/sh
DD=$(date +%d)
DOW=$(date +%u)

cd isuag
bash run_plots.sh
if [ $DD -eq "07" ]
	then
		python nmp_monthly_email.py
fi

# Run the climodat estimator to get sites that are valid at midnight
cd ../climodat
python daily_estimator.py $(date --date '1 days ago' +'%Y %m %d')

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
		 python download_narr.py $(date --date '13 days ago' +'%Y %m') &
fi
# run every Monday
if [ $DD -eq "1" ]
	then
		python fetch_power.py $(date --date '7 days ago' +'%Y')
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

cd ../ncdc
if [ $DD -eq "15" ]
	then
	python ingest_fisherporter.py $(date --date '90 days ago' +'%Y %m')
	python ingest_fisherporter.py $(date --date '180 days ago' +'%Y %m')
	python ingest_fisherporter.py $(date --date '360 days ago' +'%Y %m')
fi


cd ../asos_1minute
if [ $DD -eq "09" ]
then
	python parse_ncdc_asos1minute.py
fi


cd ../../windrose
python daily_drive_network.py &

cd ../yieldfx
python psims_baseline.py $(date --date '1 days ago' +'%Y %m %d')

cd ../prism
python ingest_prism.py $(date --date '7 days ago' +'%Y %m %d')
python ingest_prism.py $(date --date '60 days ago' +'%Y %m %d')
python ingest_prism.py $(date --date '90 days ago' +'%Y %m %d')
