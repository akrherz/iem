# Jobs run at 00 UTC

cd util
python make_ridge_dirs.py

# Wait a bit, so that more obs can come in
sleep 300

cd ../00z
python awos_rtp.py

cd ../ingestors
python elnino.py

# nexrad N0R and N0Q composites
cd ../summary
python max_reflect.py

# Rerun today
cd ../dbutil
python rwis2archive.py $(date -u --date '1 days ago' +'%Y %m %d')
python ot2archive.py $(date -u --date '1 days ago' +'%Y %m %d')
python snet2archive.py

cd ../iemre
python stage4_12z_adjust.py

cd ../dl
# at 0z, -6 days is available, hopefully!
python download_narr.py $(date -u --date '6 days ago' +'%Y %m %d')
python download_narr.py $(date -u --date '30 days ago' +'%Y %m %d')
cd ../coop
python narr_solarrad.py $(date -u --date '7 days ago' +'%Y %m %d')
python narr_solarrad.py $(date -u --date '31 days ago' +'%Y %m %d')

cd ../qc
python check_n0q.py
