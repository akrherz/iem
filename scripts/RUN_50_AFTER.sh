# cronscript for 50 minutes after the hour

cd dl
python ncep_stage4.py

# Give the stage IV data time to process thru LDM
sleep 30

cd ../current
python stage4_hourly.py
python stage4_today_total.py
python stage4_xhour.py 24
python stage4_xhour.py 48

cd ../iemre
python stage4_ingest.py `date -u +'%Y %m %d %H'`
python stage4_ingest.py `date -u --date '3 hours ago' +'%Y %m %d %H'`
python stage4_ingest.py `date -u --date '1 day ago' +'%Y %m %d %H'`

cd ../ingestors/madis
python extract_hfmetar.py 2 &

# Run HRRR radiation ingest at 10 PM, so that we have this available
# for ISUSM et al
HH=$(date +%H)
if [ "$HH" -eq "22" ]
	then
		cd ../../climodat
		python hrrr_solarrad.py $(date +'%Y %m %d')	
fi

#END