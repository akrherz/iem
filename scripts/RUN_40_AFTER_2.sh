#Run at 40 minutes after the hour

cd hrrr
python hrrr_jobs.py $(date -u --date '1 hours ago' +'%Y %m %d %H')