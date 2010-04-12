#!/bin/csh
#  Master Control for the dumping of 1 minute AWOS data
# Daryl Herzmann 3 Oct 2002
# 10 Oct 2002:	If we drop the indexes before the massive insert, that
#		would speed things up a lot!
#

set YEAR="${1}"
set MONTH="${2}"
set zipfile="awos${MONTH}`echo ${YEAR} | cut -c 3-4`.zip"
set tablename="t${YEAR}_${MONTH}"

# Delete any old files
rm -f X716/P0001/AWOS/* station/* DB/* >& /dev/null

# First we unzip the file 
#unzip /u1/ARCHIVE/awos/${YEAR}/${zipfile}
#unzip ${zipfile}
#unzip awos111205.zip

# Then we split the results
#set datafile=`ls -1 X716/P0001/AWOS/*`
set datafile="SEP09"

./split.csh ${datafile}


# Now we process the station Data
./parse.py ${YEAR} ${MONTH}

# Lets make sure the table is created and deleted and what not
psql -h iemdb awos << EOF
 create table ${tablename}() inherits (alldata);
 delete from ${tablename};
 drop index ${tablename}_valid_idx;
 drop index ${tablename}_stn_idx;
 grant select on ${tablename} to nobody;
 \q
EOF


# And we are ready to dump
./dump.csh

### Now, we build the indexes!
psql -h iemdb awos << EOF
 create index ${tablename}_valid_idx on ${tablename}(valid);
 create index ${tablename}_stn_idx on ${tablename}(station);
 \q
EOF

# Adjust summary data
/mesonet/python/bin/python update_summary.py ${YEAR} ${MONTH}
