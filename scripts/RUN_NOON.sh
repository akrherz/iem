###
# Run at noon local time
#
cd smos
python plot.py 0

cd ../iemre
# We hopefully have a 12z 24h file by now
python stage4_12z_adjust.py --date=$(date +'%Y-%m-%d')
# Copy the data to IEMRE hourly
python precip_ingest.py --valid12z=$(date +'%Y-%m-%dT12:00:00')
python ingest_nohrsc.py --date=$(date +'%Y-%m-%d')
python daily_analysis.py --date=$(date +'%Y-%m-%d') --domain=
python daily_analysis.py --date=$(date --date '1 day ago' +'%Y-%m-%d') --domain=china

cd ../prism
python ingest_prism.py --date=$(date --date '1 days ago' +'%Y-%m-%d')

cd ../iemre
# adjusts stage IV hourly file to PRISM reality
python prism_adjust_stage4.py $(date --date '1 days ago' +'%Y %m %d')
# Copies updated stage IV hourly into IEMRE hourly
python precip_ingest.py --valid12z=$(date --date '1 days ago' +'%Y-%m-%dT12:00:00')

cd ../climodat
python daily_estimator.py --date=$(date +'%Y-%m-%d')
python daily_estimator.py --date=$(date --date '1 days ago'  +'%Y-%m-%d')
# Perhaps some more QC happened, that we now need to pick up
python daily_estimator.py --date=$(date --date '7 days ago'  +'%Y-%m-%d')
python compute4regions.py $(date +'%Y %m %d')
python compute4regions.py $(date --date '1 days ago'  +'%Y %m %d')
python hrrr_solarrad.py --date=$(date --date '1 days ago'  +'%Y-%m-%d')
# Sync any coop data that may have updated over the past 24 hours
python sync_coop_updates.py

cd ../iemre
# Since we have now adjusted the 12z precip 1 day ago, we should rerun
# iemre for two days ago
python ingest_nohrsc.py --date=$(date --date '2 days ago' +'%Y-%m-%d')
python daily_analysis.py --date=$(date --date '2 days ago' +'%Y-%m-%d') --domain=
python daily_analysis.py --date=$(date --date '2 days ago' +'%Y-%m-%d') --domain=china
python daily_analysis.py --date=$(date --date '2 days ago' +'%Y-%m-%d') --domain=europe
python ingest_nohrsc.py --date=$(date --date '10 days ago' +'%Y-%m-%d')
# Updated soil temperature data from ERA5
python daily_analysis.py --date=$(date --date '10 days ago' +'%Y-%m-%d') --domain=
python daily_analysis.py --date=$(date --date '10 days ago' +'%Y-%m-%d') --domain=china
python daily_analysis.py --date=$(date --date '10 days ago' +'%Y-%m-%d') --domain=europe

# and now recompute climodat statewide/climate from two days ago
cd ../climodat
python compute4regions.py $(date --date '2 days ago' +'%Y %m %d')

# CFS workflow, first two are for yesterday and we actually run for two
# days ago
cd ../cache
bash download_cpc.sh

cd ../dl
# NB used for drydown
python download_cfs.py --date=$(date --date '3 days ago' +'%Y-%m-%d')
python download_cfs.py --date=$(date --date '4 days ago' +'%Y-%m-%d')
cd ../yieldfx
python cfs2iemre_netcdf.py
