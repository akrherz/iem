# DRIVE the processing of the monthly datafile from Harry Hillaker

if [ $# -ne 2 ] 
then
  echo "Need two arguments!  sh DRIVE.sh YEAR MONTH";
  exit 1
fi

# Process
/mesonet/python/bin/python step1_texttosql.py $1 $2
# Inject into database
psql -f /tmp/harry.sql -h iemdb coop
# Estimate ia0000
/mesonet/python/bin/python ../../climodat/compute_ia0000.py $1 $2
# Compute new records
/mesonet/python/bin/python new_records.py $1 $2
