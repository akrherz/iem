# Run every 5 minutes...
cd cache 
python nws_wawa_archive.py &

cd ../isusm
python csv2ldm.py &

cd ../roads
python archive_roadsplot.py $(date -u +'%Y %m %d %H %M') &
python ingest_roads_rest.py &

cd ../ingestors/ifc
python ingest_ifc_precip.py &

cd ../../dl
python radar_composite.py &

cd ../GIS
python 24h_lsr.py 

cd ../current
python lsr_snow_mapper.py &

cd ../ingestors/rwis
csh download.csh &
python ingest_rw.py &
