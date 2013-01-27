# Run every minute!
cd /mesonet/www/apps/nwnwebsite/scripts
php drive_lsd_generation.php &

cd /mesonet/www/apps/iemwebsite/scripts/sbw
python raccoon_sbw_to_ppt.py &

cd ../GIS
python attribute2shape.py &
python wwa2shp.py &

cd ../ingestors

python parse0002.py &
python parse0007.py &

python ctre_bridge.py &

cd ../outgoing
python snet_collect.py &



