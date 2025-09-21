# cronscript for 50 minutes after the hour

python dl/download_rtma_ru.py --valid=$(date -u --date '1 hour ago' +'%Y-%m-%dT%H'):00:00 &

python dl/download_ndfd.py &

cd ingestors/madis
python to_iemaccess.py --valid=$(date -u --date '1 hour ago' +'%Y-%m-%dT%H:%M:00')
python to_iemaccess.py --valid=$(date -u --date '3 hours ago' +'%Y-%m-%dT%H:%M:00')
python extract_hfmetar.py --hours=2 &


cd ../../gfs
python gfs2iemre.py --valid=$(date -u --date '7 hours ago' +'%Y-%m-%dT%H'):00:00 &

# Run HRRR radiation ingest at 10 PM, so that we have this available
# for ISUSM et al
HH=$(date +%H)
if [ "$HH" -eq "22" ]
    then
        cd ../climodat
        python hrrr_solarrad.py --date=$(date +'%Y-%m-%d')
fi

# END
