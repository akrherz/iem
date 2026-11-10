#!/bin/bash
# Ensure we error out
set -x -e
# Paths are setup in setuppaths.sh
python .github/ci_db_testdata.py
python scripts/mrms/init_daily_mrms.py --year=2024
python scripts/mrms/init_mrms_dailyc.py
python scripts/prism/init_daily.py --year=2024
python scripts/iemre/init_daily.py --year=2022 --domain=conus
python scripts/iemre/init_daily.py --year=2023 --ci
python scripts/iemre/init_daily.py --year=2024 --domain=conus
python scripts/iemre/init_daily.py --year=2024 --domain=europe
python scripts/iemre/init_daily.py --year=2024 --domain=sa
python scripts/iemre/init_hourly.py --year=2023 --ci
python scripts/iemre/init_dailyc.py
python scripts/iemre/init_stage4_hourly.py --year=2024 --ci
python scripts/iemre/init_stage4_daily.py --year=2024 --ci
python scripts/iemre/init_daily_ifc.py --year=2024 --ci

curl --fail --show-error --location -o /mesonet/share/features/2022/03/220325.png \
    https://mesonet.agron.iastate.edu/onsite/features/2022/03/220325.png

curl --fail --show-error --location -o /mesonet/ldmdata/gis/images/4326/USCOMP/n0q_0.json \
    https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0q_0.json
curl --fail --show-error --location -o /mesonet/ldmdata/gis/images/4326/USCOMP/n0r_0.json \
    https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0r_0.json

curl --fail --show-error --location -o /mesonet/share/pickup/yieldfx/ames.met \
    https://mesonet.agron.iastate.edu/pickup/yieldfx/ames.met

curl --fail --show-error --location -o /mesonet/data/iemre/ndfd_current.nc \
    https://mesonet.agron.iastate.edu/onsite/iemre/ndfd_current.nc

curl --fail --show-error --location -o /mesonet/data/iemre/gfs_current.nc \
    https://mesonet.agron.iastate.edu/onsite/iemre/gfs_current.nc

curl --fail --show-error --location -o /opt/iem/htdocs/vtec/assets.json \
    https://mesonet.agron.iastate.edu/vtec/assets.json

# A corrupted RTMA file
mkdir -p /mesonet/ARCHIVE/data/2024/01/01/model/rtma/00
echo > /mesonet/ARCHIVE/data/2024/01/01/model/rtma/00/rtma2p5_ru.t0000z.2dvaranl_ndfd.grb2

# A corrupted HRRR refd file
mkdir -p /mesonet/ARCHIVE/data/2024/01/01/model/hrrr/00
echo > /mesonet/ARCHIVE/data/2024/01/01/model/hrrr/00/hrrr.t00z.refd.grib2

# A valid HRRR refd file
mkdir -p /mesonet/ARCHIVE/data/2025/09/12/model/hrrr/11
curl --fail --show-error --location -o /mesonet/ARCHIVE/data/2025/09/12/model/hrrr/11/hrrr.t11z.refd.grib2 \
    https://mesonet.agron.iastate.edu/archive/data/2025/09/12/model/hrrr/11/hrrr.t11z.refd.grib2

# A valid RTMA file
mkdir -p /mesonet/ARCHIVE/data/2025/09/09/model/rtma/00
curl --fail --show-error --location -o /mesonet/ARCHIVE/data/2025/09/09/model/rtma/00/rtma.t00z.awp2p5f000.grib2 \
    https://mesonet.agron.iastate.edu/archive/data/2025/09/09/model/rtma/00/rtma.t00z.awp2p5f000.grib2

# A valid MRMS PNG
mkdir -p /mesonet/ARCHIVE/data/2016/04/13/GIS/mrms
curl --fail --show-error --location -o /mesonet/ARCHIVE/data/2016/04/13/GIS/mrms/p1h_201604131800.png \
    https://mesonet.agron.iastate.edu/archive/data/2016/04/13/GIS/mrms/p1h_201604131800.png
curl --fail --show-error --location -o /mesonet/ARCHIVE/data/2016/04/13/GIS/mrms/p1h_201604131800.wld \
    https://mesonet.agron.iastate.edu/archive/data/2016/04/13/GIS/mrms/p1h_201604131800.wld

# A valid IEM Mosaic PNG
mkdir -p /mesonet/ARCHIVE/data/2017/10/25/GIS/uscomp
curl --fail --show-error --location -o /mesonet/ARCHIVE/data/2017/10/25/GIS/uscomp/n0r_201710251200.png \
    https://mesonet.agron.iastate.edu/archive/data/2017/10/25/GIS/uscomp/n0r_201710251200.png
curl --fail --show-error --location -o /mesonet/ARCHIVE/data/2017/10/25/GIS/uscomp/n0r_201710251200.wld \
    https://mesonet.agron.iastate.edu/archive/data/2017/10/25/GIS/uscomp/n0r_201710251200.wld

