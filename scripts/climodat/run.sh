#!/bin/sh

# Generate the reports
python drive.py
python ksYearly.py 
python ksMonthly.py
python dump.py

python avg_temp.py `date +%Y`
python precip_days.py `date +%Y`
python yearly_precip.py `date +%Y`
python plot_monthly_precip.py

cd /mesonet/share/pickup/coop_data/
zip -q coop_data.zip *.csv

cd /mesonet/share/climodat/
zip -q -r everything.zip ks reports
