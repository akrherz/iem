# Runs at Midnight CST/CDT
DD=$(date -u +'%d')
MM=$(date -u +'%m')
YYYY=$(date -u +'%Y')

# Need this done so that certain variables are there for DEP
cd asos
python compute_daily.py

cd ../other
python update_daily_srad.py $(date --date '1 day ago' +'%Y %m %d')

# Need this done so that IEMRE daily grids are there for DEP
cd ../iemre
python daily_analysis.py --date=$(date --date '1 day ago' +'%Y-%m-%d')

cd ../asos
python adjust_report_type.py --date=$(date -u --date '1 day ago' +'%Y-%m-%d')

cd ../smos
python plot.py 12

# Wait a bit before doing this
sleep 600
cd ../qc
python check_station_geom.py
python check_vtec_eventids.py
python check_afos.py --date=$(date --date '1 day ago' +'%Y-%m-%d')

cd ../iemre
python grid_rsds.py --date=$(date --date '1 day ago' +'%Y-%m-%d')

cd ../dbutil 
python hads_delete_dups.py

cd ../hads
python dedup_hml_forecasts.py
python raw2obs.py

cd ../mrms
python copy_daily_24h.py $(date +'%Y %m %d')
python mrms_monthly_plot.py

# Assume we have MERRA data by the 28th each month
if [ $DD -eq "28" ]
then
    cd ../dl
    python fetch_merra.py
    MM=$(date -u --date '1 month ago' +'%m')
    YYYY=$(date -u --date '1 month ago' +'%Y')
    cd ../climodat
    python merra_solarrad.py --year=$YYYY --month=$MM
fi

# Move content to offlining
cd ../util
python autolapses2box.py
