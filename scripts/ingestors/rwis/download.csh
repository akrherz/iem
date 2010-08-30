#!/bin/csh

# Assign variables to download the data to
set INCOMING="/mesonet/data/incoming/rwis/"
set ARCHIVE="/mesonet/ARCHIVE/raw/rwis/"
set FTPPASS="`cat ftppasswd.txt`"

set LOCAL_FILE="${INCOMING}/rwis.txt"
set LOCAL_FILE2="${INCOMING}/rwis_sf.txt"

set GTS="`date -u +'%Y%m%d%H%M'`"
set TS=`date -u +%d%H%M`
set mm=`date +'%M'`

# Get rwis atmospheric file!
wget --timeout=60 -q -O ${LOCAL_FILE} ftp://rwis:${FTPPASS}@165.206.203.34/ExpApAirData.txt
/home/ldm/bin/pqinsert -p "plot ac $GTS rwis.txt raw/rwis/${GTS}at.txt txt" ${LOCAL_FILE} >& /dev/null

# Get rwis surface file!
wget --timeout=60 -q -O ${LOCAL_FILE2} ftp://rwis:${FTPPASS}@165.206.203.34/ExpSfData.txt
/home/ldm/bin/pqinsert -p "plot ac $GTS rwis_sf.txt raw/rwis/${GTS}sf.txt txt" ${LOCAL_FILE2} >& /dev/null

# AWOS file :)
wget --timeout=60 -q -O /mesonet/data/incoming/AWOS.DAT ftp://rwis:${FTPPASS}@165.206.203.34/AWOS.DAT
/home/ldm/bin/pqinsert -p "plot ac $GTS awos.txt raw/awos/${GTS}.txt txt" /mesonet/data/incoming/AWOS.DAT >& /dev/null

# Actually ingest the data
/mesonet/python/bin/python rawProcess.py

# Create a GEMPAK surface file...
/mesonet/python/bin/python genSFFIL.py

# Send Down to LDM
/home/ldm/bin/pqinsert -l /dev/null rwis.csv

# Process The sf file as well.
./run_rwisSF.csh 

cd /mesonet/data/metar

mv rwis.sao IArwis${TS}.sao
mv rwis2.sao IA.rwis${TS}.sao
/home/ldm/bin/pqinsert IArwis${TS}.sao 
if (`echo ${mm} | cut -c 2` == 6) then
  /home/ldm/bin/pqinsert IA.rwis${TS}.sao 
endif
rm IArwis${TS}.sao IA.rwis${TS}.sao

# Do mini and portable stuff
cd /mesonet/data/incoming/rwis
wget -nd -m -q "ftp://rwis:${FTPPASS}@165.206.203.34/*.csv"
cd /var/www/scripts/ingestors/rwis
/mesonet/python/bin/python mini_portable.py
/mesonet/python/bin/python process_traffic.py
