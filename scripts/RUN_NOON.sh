###
# Run at noon local time
#
cd smos
python plot.py 0

cd ../iemre
python daily_analysis.py

cd ../climodat
python daily_estimator.py $(date +'%Y %m %d')
python hrrr_solarrad.py $(date --date '1 days ago'  +'%Y %m %d')
python daily_estimator.py $(date --date '1 days ago'  +'%Y %m %d')
python compute_0000.py

cd ../prism
python ingest_prism.py $(date --date '3 days ago' +'%Y %m %d')

cd ../iemre
# adjusts stage IV hourly file to PRISM reality
python prism_adjust_stage4.py $(date --date '3 days ago' +'%Y %m %d')

# Copies updated stage IV hourly into IEMRE hourly
python precip_ingest.py $(date --date '3 days ago' +'%Y %m %d')

# Since we have now adjusted the 12z precip 3 days ago, we should rerun
# iemre for four days ago
python daily_analysis.py $(date --date '4 days ago' +'%Y %m %d')

# and now recompute climodat statewide/climate from four days ago
cd ../climodat
python compute_0000.py $(date --date '4 days ago' +'%Y %m %d')

# CFS workflow, data hopefully exists for the previous date
cd ../dl
python download_cfs.py && cd ../yieldfx && python cfs2iemre_netcdf.py && python cfs_tiler.py
