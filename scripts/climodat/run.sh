# Generate the reports, run from RUN_2AM.sh

python ks_yearly.py 
python ks_monthly.py

python avg_temp.py `date +%Y`
python precip_days.py `date +%Y`
python yearly_precip.py `date +%Y`
