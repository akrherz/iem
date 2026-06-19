# Run every minute!
stamp=$(date -u --date '5 minutes ago' +'%Y-%m-%dT%H:%M:00')

cd /opt/iem/scripts/sbw || exit 1
python raccoon_sbw_to_ppt.py &

cd ../GIS || exit 1
python attribute2shape.py &
python wwa2shp.py &

cd ../ingestors || exit 1

python parse0002.py &
python dot_plows.py &

cd other || exit 1
python purpleair.py &
python parse0006.py &
python parse0010.py &

cd ../../mrms || exit 1
python mrms_rainrate_comp.py --valid=${stamp}
python mrms_lcref_comp.py
