#
# We are run at :10 after the hour, some of these processes are intensive 
# 
YYYY=$(date -u +'%Y')
MM=$(date -u +'%m')
DD=$(date -u +'%d')
HH=$(date -u +'%H')
LHH=$(date +'%H')
YEST=$(date --date '1 day ago' +'%Y %m %d')
TODAY=$(date +'%Y %m %d')

cd dl
if [ $HH -eq "23" ]
then
    python download_cfs.py &
fi

cd ../iemre
# MRMS hourly totals arrive shortly after the top of the hour
if [ $LHH -eq "00" ]
then
    python merge_mrms_q3.py	$YEST
else
    python merge_mrms_q3.py	
fi

python merge_ifc.py $TODAY
if [ $LHH -eq "01" ]
then
    python merge_ifc.py $YEST
fi

if [ $HH -eq "12" ]
then
    python merge_mrms_q3.py	$YEST
    cd ../current
    python q3_today_total.py $YEST
fi

# We have troubles with IEMRE daily_analysis running timely at midnight, so
# we run at 11 PM for today as well
if [ $LHH -eq "23" ]
then
    python daily_analysis.py $TODAY
    python grid_rsds.py	$TODAY
fi

if [ $LHH -eq "05" ]
then
    cd ../coop
    python cfs_extract.py &
fi

cd ../hads
python process_hads_inbound.py &

cd ../plots
./RUN_PLOTS

cd ../ingestors
python flux_ingest.py

if [ $LHH -eq "15" ]
then
    python nass_quickstats.py &
fi

cd rwis
python process_traffic.py &

cd ../../current
python plot_hilo.py
python ifc_today_total.py
if [ $LHH -eq "01" ]
then
    python ifc_today_total.py $YEST
fi
python today_min_windchill.py

cd ../summary
python hourly_precip.py
if [ $LHH -eq "06" ]
then
    python max_reflect.py $(date -u --date '1 days ago' +'%Y %m %d') 6 &
fi

cd ../week
python plot_obs.py

cd ../iemplot
./RUN.csh

cd ../iemre
python hourly_analysis.py `date -u +'%Y %m %d %H'`
python hourly_analysis.py `date -u --date '2 hours ago' +'%Y %m %d %H'`

cd ../mrms
python make_mrms_rasters.py $YYYY $MM $DD $HH

cd ../smos
python ingest_smos.py

cd ../qc
python check_awos_online.py

cd ../dbutil
python mine_autoplot.py &

cd ../current
python q3_xhour.py 6
python q3_xhour.py 3
python q3_xhour.py 1
python q3_today_total.py 

cd ../ua
if [ $HH -eq "04" ]
then
    python ingest_from_rucsoundings.py $YYYY $MM $DD 00
    python compute_params.py $YYYY
fi
if [ $HH -eq "16" ]
then
    python ingest_from_rucsoundings.py $YYYY $MM $DD 12
    python compute_params.py $YYYY
fi

cd ../mos
python current_bias.py NAM
python current_bias.py GFS
python current_bias.py NBS

if [ $HH -eq "01" ]
then
    cd ../coop
    python ndfd_extract.py &

    cd ../ndfd
    python ndfd2netcdf.py $(date -u +'%Y %m %d')
    python plot_temps.py $(date -u +'%Y %m %d')
fi

# Additional hourly_analysis for a number of days ago, to pick up new data
cd ../iemre
python hourly_analysis.py `date -u --date '1 days ago' +'%Y %m %d %H'`
python hourly_analysis.py `date -u --date '9 days ago' +'%Y %m %d %H'`
