# Run every 5 minutes...
export STAMP=$(date -u +'%Y %m %d %H %M')

cd cache 
python nws_wawa_archive.py &

cd ../isusm
python csv2ldm.py &

cd ../roads
python archive_roadsplot.py $STAMP &
python ingest_roads_rest.py &

cd ifc
python ingest_ifc_precip.py &

cd ../../dl
python radar_composite.py $STAMP &

cd ../GIS
python 24h_lsr.py 

cd ../current
python lsr_snow_mapper.py &

cd ../ingestors/rwis
python process_rwis.py &
python process_soil.py &
python ingest_rw.py
