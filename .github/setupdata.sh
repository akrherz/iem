# Paths are setup in setuppaths.sh
python database/store_test_data.py $(which psql)
python scripts/dbutil/sync_stations.py
python scripts/prism/init_daily.py --year=2024
python scripts/iemre/init_daily.py --year=2024 --domain=
python scripts/iemre/init_daily.py --year=2024 --domain=europe

curl -o /mesonet/ldmdata/gis/images/4326/USCOMP/n0q_0.json \
https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0q_0.json
curl -o /mesonet/ldmdata/gis/images/4326/USCOMP/n0r_0.json \
https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0r_0.json
