###
# Run at noon local time
#
cd smos
python plot.py 0

cd ../iemre
python daily_analysis.py

cd ../climodat
python daily_estimator.py $(date +'%Y %m %d')
python daily_estimator.py $(date --date '1 days ago'  +'%Y %m %d')
python compute_0000.py

cd ../prism
python ingest_prism.py $(date --date '3 days ago' +'%Y %m %d')

cd ../iemre
python prism_adjust_stage4.py $(date --date '3 days ago' +'%Y %m %d')

# Since we have now adjusted the 12z precip 3 days ago, we should rerun
# iemre for four days ago
python daily_analysis.py $(date --date '4 days ago' +'%Y %m %d')
