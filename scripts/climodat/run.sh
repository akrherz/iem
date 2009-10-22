#!/bin/sh

/mesonet/python/bin/python drive.py
/mesonet/python/bin/python ksYearly.py 
/mesonet/python/bin/python ksMonthly.py 2009
/mesonet/python/bin/python dump.py

mv reports/* /mesonet/share/climodat/reports/
mv ks/* /mesonet/share/climodat/ks/
mv coop_data/* /mesonet/share/pickup/coop_data/

cd /mesonet/share/pickup/coop_data/
zip coop_data.zip *.csv

cd /mesonet/share/climodat/
zip -r everything.zip ks reports
