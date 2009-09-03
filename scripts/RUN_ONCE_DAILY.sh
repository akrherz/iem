# Run once daily

cd qc
/mesonet/python/bin/python dailyVtec.py

cd ../outgoing
/mesonet/python/bin/python wxc_azos_gdd.py
