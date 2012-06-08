# Run every minute!
/mesonet/www/apps/nwnwebsite/scripts/GEN.csh &

cd sbw
python raccoon_sbw_to_ppt.py &

cd ../GIS
python attribute2shape.py
python wwa2shp.py &

cd ../ingestors
#/mesonet/python/bin/python parse0006.py &
/mesonet/python/bin/python parse0002.py &
#/mesonet/python/bin/python awos_adas.py &
python ctre_bridge.py &

cd ../outgoing
python snet_collect.py &

#cd ../awos
#/mesonet/python/bin/python dl_parse_iwapi.py


