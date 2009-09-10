#!/bin/sh

./drive.py
./ksYearly.py 
./ksMonthly.py 2009
./dump.py

mv reports/* /mesonet/share/climodat/reports/
mv ks/* /mesonet/share/climodat/ks/
mv coop_data/* /mesonet/share/pickup/coop_data/

cd /mesonet/share/pickup/coop_data/
zip coop_data.zip *.csv

cd /mesonet/share/climodat/
zip -r everything.zip ks reports
