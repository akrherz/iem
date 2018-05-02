###
# Run at noon local time
#
cd smos
python plot.py 0

cd ../iemre
python daily_analysis.py

cd ../climodat
python daily_estimator.py
python compute_0000.py

cd ../prism
python ingest_prism.py $(date --date '3 days ago' +'%Y %m %d')

cd ../iemre
python prism_adjust_stage4.py $(date --date '3 days ago' +'%Y %m %d')
