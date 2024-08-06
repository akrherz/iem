# ERA5Land is very slow to download, so we need to isolate this processing
HH=$(date -u +%H)
if [ "$HH" -ne "00" ]
    then
        exit
fi
D6=$(date -u --date '6 days ago' +'%Y-%m-%d')
D7=$(date -u --date '7 days ago' +'%Y-%m-%d')

cd era5
python fetch_era5.py --date=$D6 --domain=
python fetch_era5.py --date=$D6 --domain=china
python fetch_era5.py --date=$D6 --domain=europe

cd ../climodat
python era5land_extract.py --date=$D7
