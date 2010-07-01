#!/bin/sh

/mesonet/python/bin/python drive.py
/mesonet/python/bin/python ksYearly.py 
/mesonet/python/bin/python ksMonthly.py
/mesonet/python/bin/python dump.py

mv reports/* /mesonet/share/climodat/reports/
mv ks/* /mesonet/share/climodat/ks/
mv coop_data/* /mesonet/share/pickup/coop_data/

/mesonet/python/bin/python avg_temp.py `date +%Y`
/mesonet/python/bin/python precip_days.py `date +%Y`
/mesonet/python/bin/python yearly_precip.py `date +%Y`

cd /mesonet/share/pickup/coop_data/
zip coop_data.zip *.csv

cd /mesonet/share/climodat/
zip -r everything.zip ks reports
