# Run every minute!
cd /mesonet/www/apps/nwnwebsite/scripts
php drive_lsd_generation.php &

cd /opt/iem/scripts/sbw
python raccoon_sbw_to_ppt.py &

cd ../GIS
python attribute2shape.py &
python wwa2shp.py &

cd ../ingestors

python parse0002.py &
python parse0007.py &
python dot_plows.py &
python ctre_bridge.py &

cd ../outgoing
python snet_collect.py &

cd ../mrms
python mrms_rainrate_comp.py 
python mrms_lcref_comp.py
