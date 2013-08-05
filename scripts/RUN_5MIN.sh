# Run every 5 minutes
cd cache 
sh download_wwa.sh &

cd ../ingestors/ifc
python ingest_ifc_precip.py &

cd ../../dl
python radar_composite.py 

cd ../outgoing
python dump_precip.py

cd snetnws
python snet_fe.py &

cd ../../GIS
python 24h_lsr.py 

cd ../current
python lsr_snow_mapper.py >& /dev/null
python q3_2min_rate.py &

cd ../ingestors/rwis
./download.csh &

# This could take some time, so background it
cd ../dotcams
python process.py &
