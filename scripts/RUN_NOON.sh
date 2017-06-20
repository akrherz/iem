###
# Run at noon local time
#
cd smos
python plot.py 0

cd ../iemre
python daily_analysis.py

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
python compute_0000.py

cd ../prism
python ingest_prism.py $(date --date '3 days ago' +'%Y %m %d')

cd ../iemre
python prism_adjust_stage4.py $(date --date '3 days ago' +'%Y %m %d')
