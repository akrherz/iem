#!/bin/sh

# Generate the reports
python drive.py
python ksYearly.py 
python ksMonthly.py
python dump.py

mv reports/* /mesonet/share/climodat/reports/
mv ks/* /mesonet/share/climodat/ks/
mv coop_data/* /mesonet/share/pickup/coop_data/

python avg_temp.py `date +%Y`
python precip_days.py `date +%Y`
python yearly_precip.py `date +%Y`
python plot_monthly_precip.py

cd /mesonet/share/pickup/coop_data/
zip coop_data.zip *.csv

cd /mesonet/share/climodat/
zip -r everything.zip ks reports
