# Runs at Midnight CST/CDT
DD=$(date -u +'%d')
MM=$(date -u +'%m')
YYYY=$(date -u +'%Y')

# Need this done so that certain variables are there for DEP
cd asos
python compute_daily.py

# Need this done so that IEMRE daily grids are there for DEP
cd ../iemre
python daily_analysis.py $(date --date '1 day ago' +'%Y %m %d')

cd ../smos
python plot.py 12

# Wait a bit before doing this
sleep 600
cd ../qc
python check_station_geom.py
python check_vtec_eventids.py
python check_afos_sources.py

cd ../outgoing
python wxc_moon.py

cd ../iemre
python grid_rsds.py

cd ../dbutil 
python hads_delete_dups.py

cd ../hads
python dedup_hml_forecasts.py
python raw2obs.py

cd ../mrms
python create_daily_symlink.py $(date --date '1 day ago' +'%Y %m %d')
python mrms_monthly_plot.py

# Assume we have MERRA data by the 28th each month
if [ $DD -eq "28" ]
then
	cd ../dl
	python fetch_merra.py
	MM=$(date -u --date '1 month ago' +'%m')
	YYYY=$(date -u --date '1 month ago' +'%Y')
	cd ../climodat
	python merra_solarrad.py $YYYY $MM
	cd ../iemre
	python grid_rsds.py $YYYY $MM
fi

# Pick a sequential state
cd ../util
STATE=$(python pick_state.py)
cd ../climodat
python check_database.py $STATE
python use_acis.py $STATE
cd ../coop
python use_acis.py $STATE
cd ../dbutil
python compute_climate_sts.py ${STATE}CLIMATE

# Ingest Poker
cd ../../util
python poker2afos.py
python i5_2_cybox.py
python autolapses2box.py
