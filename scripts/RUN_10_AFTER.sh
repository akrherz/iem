#!/bin/bash
# We are run at :10 after the hour, some of these processes are intensive
#
YYYY=$(date -u +'%Y')
MM=$(date -u +'%m')
DD=$(date -u +'%d')
HH=$(date -u +'%H')
HH=${HH#0}
LHH=$(date +'%H')

python cache/midwest_winter_roads.py &
python dl/download_ndfd.py &

# Run at 0, 1, and 2 UTC
if [[ $HH -eq 0 || $HH -eq 1 || $HH -eq 2 ]]
then
    python 00z/generate_rtp.py
fi

# Run at 12, 13, and 14 UTC
if [[ $HH -eq 12 || $HH -eq 13 || $HH -eq 14 ]]
then
    python 12z/generate_rtp.py
fi

cd mrms || exit 1
# MRMS hourly totals arrive shortly after the top of the hour
if [ "$LHH" -eq "00" ]
then
    python merge_mrms_q3.py	--date="$(date --date '1 days ago' +'%Y-%m-%d')"
else
    python merge_mrms_q3.py --date="$(date +'%Y-%m-%d')"
fi
# QC comes about an hour delayed, so rerun the previous day
if [ "$LHH" -eq "03" ]
then
    python merge_mrms_q3.py	--date="$(date --date '1 days ago' +'%Y-%m-%d')"
fi
# Special processing for DEP, to run at 5 PM, as DEP runs at 6 PM
if [ "$LHH" -eq "17" ]
then
    python merge_mrms_q3.py	--date="$(date +'%Y-%m-%d')" --for-dep
fi

cd ../ingestors/other || exit 1
python feel_ingest.py &

cd ../../iemre || exit 1
python merge_ifc.py --date="$(date +'%Y-%m-%d')"
if [ "$LHH" -eq "01" ]
then
    python merge_ifc.py --date="$(date --date '1 day ago' +'%Y-%m-%d')"
fi

if [ "$HH" -eq 12 ]
then
    cd ../current || exit 1
    python mrms_today_total.py --date="$(date --date '1 day ago' +'%Y-%m-%d')"
fi

# We have troubles with IEMRE daily_analysis running timely at midnight, so
# we run at 11 PM for today as well
if [ "$LHH" -eq "23" ]
then
    python daily_analysis.py --date="$(date +'%Y-%m-%d')" --domain=conus
    python grid_rsds.py	--date="$(date +'%Y-%m-%d')"
fi

if [ "$LHH" -eq "05" ]
then
    cd ../coop || exit 1
    python cfs_extract.py &
fi

cd ../plots || exit 1
bash RUN_PLOTS.sh

cd ../ingestors || exit 1
python flux_ingest.py

cd ../nass || exit 1
if [ "$LHH" -eq "15" ]
then
    python nass_quickstats.py &
fi

cd ../ingestors/rwis || exit 1
python process_traffic.py &

cd ../../current || exit 1
python plot_hilo.py --date="$(date +'%Y-%m-%d')"
python ifc_today_total.py --date="$(date --date '60 minutes ago' +'%Y-%m-%d')" --realtime
if [ "$LHH" -eq "01" ]
then
    python ifc_today_total.py --date="$(date --date '1 days ago' +'%Y-%m-%d')"
fi
python today_min_windchill.py --date="$(date +'%Y-%m-%d')" --realtime

cd ../summary || exit 1
python hourly_precip.py
if [ "$LHH" -eq "06" ]
then
    python max_reflect.py --valid="$(date -u --date '1 days ago' +'%Y-%m-%dT06:00:00')" &
fi

cd ../week || exit 1
python plot_obs.py

cd ../iemplot || exit 1
bash RUN.sh

cd ../iemre || exit 1
python hourly_analysis.py --valid="$(date -u +'%Y-%m-%dT%H:00:00')"
python hourly_analysis.py --valid="$(date -u --date '2 hours ago' +'%Y-%m-%dT%H:00:00')"

cd ../mrms || exit 1
python make_mrms_rasters.py --valid="$(date -u +'%Y-%m-%dT%H:00:00')"

cd ../smos || exit 1
python ingest_smos.py

cd ../qc || exit 1
python check_awos_online.py

cd ../dbutil || exit 1
python mine_autoplot.py &

cd ../current || exit 1
python q3_xhour.py --hours=6
python q3_xhour.py --hours=3
python q3_xhour.py --hours=1
python mrms_today_total.py --date="$(date +'%Y-%m-%d')"

cd ../ua || exit 1
if [ "$HH" -eq "01" ]
then
    python ingest_from_spc.py --valid="${YYYY}-${MM}-${DD}T00:00:00"
    python compute_params.py --year="$YYYY"
fi
if [ "$HH" -eq "13" ]
then
    python ingest_from_spc.py --valid="${YYYY}-${MM}-${DD}T12:00:00"
    python compute_params.py --year="$YYYY"
fi
if [ "$HH" -eq "19" ]
then
    python ingest_from_spc.py --valid="${YYYY}-${MM}-${DD}T18:00:00"
    python compute_params.py --year="$YYYY"
fi

cd ../mos || exit 1
python current_bias.py --model=NAM
python current_bias.py --model=GFS
python current_bias.py --model=NBS

if [ "$HH" -eq "01" ]
then
    cd ../coop || exit 1
    python ndfd_extract.py &

    cd ../ndfd || exit 1
    python ndfd2netcdf.py --date="$(date -u +'%Y-%m-%d')"
    python plot_temps.py --date="$(date -u +'%Y-%m-%d')"
fi

# Additional hourly_analysis for a number of days ago, to pick up new data
cd ../iemre || exit 1
python hourly_analysis.py --valid="$(date -u --date '1 days ago' +'%Y-%m-%dT%H:00:00')"
python hourly_analysis.py --valid="$(date -u --date '9 days ago' +'%Y-%m-%dT%H:00:00')"
python hourly_analysis.py --valid="$(date -u --date '9 days ago' +'%Y-%m-%dT%H:00:00')" --domain=europe
python hourly_analysis.py --valid="$(date -u --date '9 days ago' +'%Y-%m-%dT%H:00:00')" --domain=china
python hourly_analysis.py --valid="$(date -u --date '9 days ago' +'%Y-%m-%dT%H:00:00')" --domain=sa
