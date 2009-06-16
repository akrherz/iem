# Scripts to run for summary type plots
# Run this only a couple of times per day, probably

cd gdd
/mesonet/python/bin/python normal_may1.py

cd ../climate
/mesonet/python/bin/python today_hilo.py
/mesonet/python/bin/python today_rec_hilo.py
