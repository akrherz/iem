# Paths are setup in setuppaths.sh
python database/store_test_data.py $(which psql)
python scripts/dbutil/sync_stations.py
python scripts/mrms/init_daily_mrms.py --year=2024
python scripts/mrms/init_mrms_dailyc.py
python scripts/prism/init_daily.py --year=2024
python scripts/iemre/init_daily.py --year=2024 --domain=
python scripts/iemre/init_daily.py --year=2024 --domain=europe
python scripts/iemre/init_dailyc.py
python scripts/iemre/init_stage4_hourly.py --year=2024
python scripts/iemre/init_stage4_daily.py --year=2024

curl -o /mesonet/ldmdata/gis/images/4326/USCOMP/n0q_0.json \
https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0q_0.json
curl -o /mesonet/ldmdata/gis/images/4326/USCOMP/n0r_0.json \
https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0r_0.json

curl -o /mesonet/share/pickup/yieldfx/ames.met \
https://mesonet.agron.iastate.edu/pickup/yieldfx/ames.met
