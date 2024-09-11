# Generate the reports, run from RUN_2AM.sh

YYYY=$(date +%Y)

python ks_yearly.py 
python ks_monthly.py

python avg_temp.py --year=$YYYY
python precip_days.py --year=$YYYY
python yearly_precip.py --year=$YYYY
