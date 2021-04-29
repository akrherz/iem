# Generate the reports, run from RUN_2AM.sh

python ks_yearly.py 
python ks_monthly.py
python dump.py

python avg_temp.py `date +%Y`
python precip_days.py `date +%Y`
python yearly_precip.py `date +%Y`

cd /mesonet/share/pickup/coop_data/
zip -q coop_data.zip *.csv

cd /mesonet/share/climodat/
zip -q -r everything.zip ks
