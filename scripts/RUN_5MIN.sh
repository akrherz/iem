# Run every 5 minutes...
VALID=$(date -u +'%Y-%m-%dT%H:%M'):00

cd cache || exit 1
python nws_wawa_archive.py &

cd ../dbutil || exit 1
python mine_telemetry.py &

cd ../isusm || exit 1
python agg_precip.py &
python csv2ldm.py &

cd ../roads || exit 1
python archive_roadsplot.py --valid=$VALID &
python ingest_roads_rest.py &

cd ../ingestors/ifc || exit 1
python ingest_ifc_precip.py &

cd ../../dl || exit 1
python radar_composite.py --valid=$VALID &

cd ../GIS || exit 1
python 24h_lsr.py

cd ../current || exit 1
python lsr_snow_mapper.py &

cd ../ingestors/rwis || exit 1
python process_rwis.py &
python process_soil.py

cd ../../sbw || exit 1
python compute_shared_border_pct.py --year=$(date -u +%Y)
