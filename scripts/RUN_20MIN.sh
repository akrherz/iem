# Run every 20 minutes please

cd ingestors/madis
python to_iemaccess.py

cd ../../outgoing
python network2wxc.py APRSWXNET bogus
