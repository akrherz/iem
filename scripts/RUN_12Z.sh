# Run at 12Z, but needs some manual crontab changing help

cd cscap
python harvest_agronomic.py 2011
python harvest_agronomic.py 2012
python harvest_agronomic.py 2013
python harvest_soil_nitrate.py 2011
python harvest_soil_nitrate.py 2012
python harvest_soil_nitrate.py 2013
python email_daily_changes.py 
python set_dashboard_links.py 2012
python set_dashboard_links.py 2013
python set_dashboard_links.py 2014

cd ../12z
python awos_rtp.py
python asos_low.py

# Rerun yesterday and today
cd ../dbutil
python rwis2archive.py $(date -u --date '1 days ago' +'%Y %m %d')
python rwis2archive.py $(date -u +'%Y %m %d')
python ot2archive.py $(date -u --date '1 days ago' +'%Y %m %d')
python ot2archive.py $(date -u +'%Y %m %d')

cd ../util
csh BACKUP.csh
