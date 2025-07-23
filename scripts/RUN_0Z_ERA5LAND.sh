# ERA5Land is very slow to download, so we need to isolate this processing
HH=$(date -u +%H)
if [ "$HH" -ne "00" ]
    then
        exit
fi
D6=$(date -u --date '6 days ago' +'%Y-%m-%d')
D7=$(date -u --date '7 days ago' +'%Y-%m-%d')

cd era5
python fetch_era5.py --date=$D6

cd ../climodat
python era5land_extract.py --date=$D7

# So fetch_era5 got files from six days ago from 1z on
cd ../iemre
for domain in "europe" "sa" "china"; do
    for hr in {0..23}; do
        python precip_ingest.py --domain=$domain --valid="${D6}T${hr}:00:00"
    done
done
