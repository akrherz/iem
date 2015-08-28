# DRIVE the processing of the monthly datafile from Harry Hillaker

if [ $# -ne 2 ] 
then
  echo "Need two arguments!  sh DRIVE.sh YEAR MONTH";
  exit 1
fi

# Process
python step1_texttosql.py $1 $2
# Inject into database
psql -f /tmp/harry.sql -h iemdb coop
# Fill missing data
python fill_month.py $1 $2
# Need to produce estimates of temperatures were there are none
echo "Generating estimates for missing data"
python ../../coop/estimate_missing.py IA
echo "Redoing estimates, this will take a bit!"
# Estimate ia0000
python ../../climodat/compute_0000.py $1 $2 >& /dev/null
# Compute new records
python new_records.py $1 $2
echo "Redoing MERRA Solar Estimates"
python ../../coop/merra_solarrad.py $1 $2
echo "Redoing NARR Solar Estimates"
python ../../coop/narr_solarrad.py $1 $2
echo "Redoing HRRR Solar Estimates"
python ../../coop/hrrr_solarrad.py $1 $2