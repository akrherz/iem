# Run every minute!
/mesonet/www/apps/nwnwebsite/scripts/GEN.csh &

cd sbw
python raccoon_sbw_to_ppt.py &

cd ../GIS
python attribute2shape.py
/mesonet/python/bin/python wwShapefile.py &

cd ../ingestors
#/mesonet/python/bin/python parse0006.py &
/mesonet/python/bin/python parse0002.py &
#/mesonet/python/bin/python awos_adas.py &
/usr/bin/python ctre_bridge.py &

cd ../outgoing
/mesonet/python/bin/python snet_collect.py >& /dev/null &

cd ../ingestors/sn
/mesonet/python/bin/python parser.py >& /dev/null &

cd ../awos
/mesonet/python/bin/python dl_parse_iwapi.py


