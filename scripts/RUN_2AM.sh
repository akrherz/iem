#!/bin/sh

# First Guess for harry, run on the first of each month
cd coop
DD=$(date +%d)
if [ $DD -eq "01" ]
	then
	python first_guess_for_harry.py
fi

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
python grid_climodat.py

cd ../climodat
python compute_0000.py
./run.sh >& a &

cd ../cache
python warn_cache.py

cd ../dbutil
python asos2archive.py
python clean_afos.py

cd ../qc
python check_iem_precip.py
python hads_nwsli_squawk.py

cd ../ingestors/cocorahs
/mesonet/python/bin/python redo_day.py IA
/mesonet/python/bin/python redo_day.py IL

cd ../../windrose
python daily_drive_network.py