# Run at 30 minutes after the hour

cd hrrr
python hrrr_jobs.py --valid=$(date -u --date '1 hours ago' +'%Y-%m-%dT%H'):00:00 --is-realtime
# Reprocess 6 hours ago
python hrrr_jobs.py --valid=$(date -u --date '6 hours ago' +'%Y-%m-%dT%H'):00:00
