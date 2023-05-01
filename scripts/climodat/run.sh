# Generate the reports, run from RUN_2AM.sh

YYYY=$(date +%Y)

python ks_yearly.py 
python ks_monthly.py

python avg_temp.py $YYYY
python precip_days.py $YYYY
python yearly_precip.py $YYYY
