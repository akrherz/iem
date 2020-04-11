# Process RWIS

set FTPPASS="`python get_rwis_ftp_password.py`"
set GTS="`date -u +'%Y%m%d%H%M'`"

# Process AWOS METAR file
# FILE ON SERVER IS BAD!
# python process_idot_awos.py

# Actually ingest the data
python process_rwis.py $GTS

# Do mini and portable stuff
cd /mesonet/data/incoming/rwis
wget -nd -m -q "ftp://rwis:${FTPPASS}@165.206.203.34/*.csv"
/home/ldm/bin/pqinsert -i -p "plot ac $GTS rwis_probe.txt raw/rwis/${GTS}probe.txt txt" DeepTempProbeFile.csv
cd /opt/iem/scripts/ingestors/rwis
python mini_portable.py
python process_soil.py
