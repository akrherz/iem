#!/bin/bash
# Run at :20 after the hour

# Jobs down below can be a bit slow, so we want these to run for the right
# hour and so not to collide
cd dl || exit 1
python download_gfs.py --valid="$(date -u --date '6 hours ago' +'%Y-%m-%dT%H'):00:00" &

# Still boggling this timing
python download_imerg.py --valid="$(date -u --date '4 hours ago' +'%Y-%m-%dT%H:00:00')"
python download_imerg.py --valid="$(date -u --date '4 hours ago' +'%Y-%m-%dT%H:30:00')" --realtime
python download_imerg.py --valid="$(date -u --date '6 hours ago' +'%Y-%m-%dT%H:00:00')"
python download_imerg.py --valid="$(date -u --date '6 hours ago' +'%Y-%m-%dT%H:30:00')"
python download_imerg.py --valid="$(date -u --date '27 hours ago' +'%Y-%m-%dT%H:00:00')"
python download_imerg.py --valid="$(date -u --date '27 hours ago' +'%Y-%m-%dT%H:30:00')"
python download_imerg.py --valid="$(date -u --date '35 hours ago' +'%Y-%m-%dT%H:00:00')"
python download_imerg.py --valid="$(date -u --date '35 hours ago' +'%Y-%m-%dT%H:30:00')"
python download_imerg.py --valid="$(date -u --date '6 months ago' +'%Y-%m-%dT%H:00:00')"
python download_imerg.py --valid="$(date -u --date '6 months ago' +'%Y-%m-%dT%H:30:00')"

cd ../plots || exit 1
bash RUN_PLOTS.sh

cd ../ndfd || exit 1
python ndfd2iemre.py &

cd ../isusm || exit 1
python agg_1minute.py

cd ../hads || exit 1
python compute_hads_phour.py --valid="$(date -u --date '1 hour ago' +'%Y-%m-%dT%H:00:00')"
python compute_hads_pday.py --date="$(date '+%Y-%m-%d')"

cd ../ingestors || exit 1
python uscrn_ingest.py

cd ../uscrn || exit 1
python compute_uscrn_pday.py --date="$(date '+%Y-%m-%d')"

# Run later to keep from conflicting with RUN_20MIN.sh to_iemaccess.py
cd ../ingestors/madis || exit 1
python extract_hfmetar.py --hours=0

# Reprocess day old HADS
cd ../../hads || exit 1
python compute_hads_phour.py --valid="$(date -u --date '24 hours ago' +'%Y-%m-%dT%H:00:00')"
