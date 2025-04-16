# Ensure we error out
set -x -e
# Paths are setup in setuppaths.sh
python .github/ci_db_testdata.py
python scripts/dbutil/sync_stations.py
python scripts/mrms/init_daily_mrms.py --year=2024
python scripts/mrms/init_mrms_dailyc.py
python scripts/prism/init_daily.py --year=2024
python scripts/iemre/init_daily.py --year=2022 --domain=
python scripts/iemre/init_daily.py --year=2023 --ci
python scripts/iemre/init_daily.py --year=2024 --domain=
python scripts/iemre/init_daily.py --year=2024 --domain=europe
python scripts/iemre/init_daily.py --year=2024 --domain=sa
python scripts/iemre/init_hourly.py --year=2023 --ci
python scripts/iemre/init_dailyc.py
python scripts/iemre/init_stage4_hourly.py --year=2024 --ci
python scripts/iemre/init_stage4_daily.py --year=2024 --ci
python scripts/iemre/init_daily_ifc.py --year=2024 --ci

curl -o /mesonet/share/features/2022/03/220325.png \
https://mesonet.agron.iastate.edu/onsite/features/2022/03/220325.png

curl -o /mesonet/ldmdata/gis/images/4326/USCOMP/n0q_0.json \
https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0q_0.json
curl -o /mesonet/ldmdata/gis/images/4326/USCOMP/n0r_0.json \
https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0r_0.json

curl -o /mesonet/share/pickup/yieldfx/ames.met \
https://mesonet.agron.iastate.edu/pickup/yieldfx/ames.met

curl -o /mesonet/data/iemre/ndfd_current.nc \
https://mesonet.agron.iastate.edu/onsite/iemre/ndfd_current.nc

curl -o /mesonet/data/iemre/gfs_current.nc \
https://mesonet.agron.iastate.edu/onsite/iemre/gfs_current.nc

# A corrupted RTMA file
mkdir -p /mesonet/ARCHIVE/data/2024/01/01/model/rtma/00
echo > /mesonet/ARCHIVE/data/2024/01/01/model/rtma/00/rtma2p5_ru.t0000z.2dvaranl_ndfd.grb2
