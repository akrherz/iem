# Run Stage IV processing
# Appears we can run at :59 after and have data
TSTAMP=$(date -u +'%Y-%m-%dT%H:00:00')

cd dl
python ncep_stage4.py

# Give the stage IV data time to process thru LDM
sleep 30

cd ../current
python stage4_hourly.py --valid=$TSTAMP
python stage4_today_total.py
python stage4_xhour.py 24
python stage4_xhour.py 48

cd ../iemre
python precip_ingest.py --valid=$TSTAMP
python precip_ingest.py --valid=$(date -u --date '4 hours ago' +'%Y-%m-%dT%H:00:00')
python precip_ingest.py --valid=$(date -u --date '1 day ago' +'%Y-%m-%dT%H:00:00')
