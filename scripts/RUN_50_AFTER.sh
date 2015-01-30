# cronscript for 50 minutes after the hour

cd dl
python ncep_stage4.py

# Give the stage IV data time to process thru LDM
sleep 30

cd ../current
python stage4_hourly.py
python stage4_today_total.py
python stage4_Xhour.py 24
python stage4_Xhour.py 48

cd ../iemre
python stage4_hourlyre.py
python stage4_hourlyre.py `date -u --date '3 hours ago' +'%Y %m %d %H'`
python stage4_hourlyre.py `date -u --date '1 day ago' +'%Y %m %d %H'`

#END