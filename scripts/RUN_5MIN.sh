# Run every 5 minutes...
VALID=$(date -u +'%Y-%m-%dT%H:%M'):00

cd cache 
python nws_wawa_archive.py &

cd ../isusm
python agg_precip.py &
python csv2ldm.py &

cd ../roads
python archive_roadsplot.py --valid=$VALID &
python ingest_roads_rest.py &

cd ../ingestors/ifc
python ingest_ifc_precip.py &

cd ../../dl
python radar_composite.py --valid=$VALID &

cd ../GIS
python 24h_lsr.py 

cd ../current
python lsr_snow_mapper.py &

cd ../ingestors/rwis
python process_rwis.py &
python process_soil.py &
python ingest_rw.py
