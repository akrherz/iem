# Run every 20 minutes please

# Wait two minutes please
sleep 120
cd current
/mesonet/python/bin/python 24h_change.py

cd ../ingestors/rwis
/mesonet/python/bin/python acquireClarus.py

cd ../madis
/mesonet/python/bin/python to_iemaccess.py

cd ../../snet
./RUN.csh
