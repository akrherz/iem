# Run at :20 after the hour

# Jobs down below can be a bit slow, so we want these to run for the right
# hour and so not to collide
cd dl
python download_gfs.py --valid=$(date -u --date '6 hours ago' +'%Y-%m-%dT%H'):00:00 &

python download_imerg.py --valid=$(date -u --date '7 hours ago' +'%Y-%m-%dT%H:00:00')
python download_imerg.py --valid=$(date -u --date '7 hours ago' +'%Y-%m-%dT%H:30:00') --realtime
python download_imerg.py --valid=$(date -u --date '27 hours ago' +'%Y-%m-%dT%H:00:00')
python download_imerg.py --valid=$(date -u --date '27 hours ago' +'%Y-%m-%dT%H:30:00')
python download_imerg.py --valid=$(date -u --date '35 hours ago' +'%Y-%m-%dT%H:00:00')
python download_imerg.py --valid=$(date -u --date '35 hours ago' +'%Y-%m-%dT%H:30:00')
python download_imerg.py --valid=$(date -u --date '6 months ago' +'%Y-%m-%dT%H:00:00')
python download_imerg.py --valid=$(date -u --date '6 months ago' +'%Y-%m-%dT%H:30:00')

cd ../ingestors/madis
python extract_hfmetar.py 0 &
python to_iemaccess.py --offset=1 &

cd ../../plots
./RUN_PLOTS

cd ../ndfd
python ndfd2iemre.py &

cd ../isusm
python agg_1minute.py

cd ../hads
python compute_hads_pday.py --date=$(date '+%Y-%m-%d')

cd ../ingestors
python uscrn_ingest.py

cd ../uscrn
python compute_uscrn_pday.py
