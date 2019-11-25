#!/bin/sh
#set -x
# Get and process files from NESDIS
# channel 5 12.0um
# channel 4 10.70um
# channel 3 6.75um
# channel 2 3.9um 
# channel 1 0.65um  Vis
# EAST -110 65.5 -29 -15
# West -180 65.5 -102 -15

# Verbose for now to check some things
#date

tm=$(python ts.py $1 %j%H%M)
tm2=$(python ts2.py $1 %j%H%M)
ftm=$(python ts.py $1 %Y%m%d%H%M)
atm=$(python ts.py $1 %H%M)
wtm=$(python wdownload.py $1)
cd /mesonet/tmp
mkdir nesdis.$ftm
cd nesdis.$ftm

BASE="http://satepsanone.nesdis.noaa.gov/pub/GIS"

function getter(){
	for i in {1..10}
		do
			wget --connect-timeout=60 -O $1 -q $2 && return
			#echo "FAIL $2"
			sleep 60
			done	
}

getter GoesWest1V${tm}.tif $BASE/GOESwest/GoesWest1V_latest.tif 
getter GoesWest1V${tm}.tfw $BASE/GOESwest/GoesWest1V_latest.tfw
getter GoesWest04I3${tm}.tif $BASE/GOESwest/GoesWest04I3_latest.tif
getter GoesWest04I3${tm}.tfw $BASE/GOESwest/GoesWest04I3_latest.tfw
getter GoesWest04I4${tm}.tif $BASE/GOESwest/GoesWest04I4_latest.tif
getter GoesWest04I4${tm}.tfw $BASE/GOESwest/GoesWest04I4_latest.tfw


pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/west1V_0.tif bogus tif" GoesWest1V${tm}.tif
pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/west1V_0.tfw bogus tfw" GoesWest1V${tm}.tfw

pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/west04I4_0.tif bogus tif" GoesWest04I4${tm}.tif
pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/west04I4_0.tfw bogus tfw" GoesWest04I4${tm}.tfw
 
pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/west04I3_0.tif bogus tif" GoesWest04I3${tm}.tif
pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/west04I3_0.tfw bogus tfw" GoesWest04I3${tm}.tfw

# Cleanup!
cd ..
rm -rf nesdis.$ftm

#DONE