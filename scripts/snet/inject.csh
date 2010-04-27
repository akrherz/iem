#!/bin/csh
#  Script to populate database with values from snet gempak file
# Daryl Herzmann 12 Feb 2002
#  3 Jan 2002:	This is probably not 2003 happy
#
#################################################################

source /mesonet/nawips/Gemenviron

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set year=`date -u +%Y`
set hh=`date -u +%H`
set mm=`date -u +%M`
set hour=${hh}

if (${mm} > 40 ) then
        set mm = "40"
else if (${mm} > 20) then
        set mm = "20"
else
        set mm = "00"
endif

set sqlDate="`date -u +'%Y-%m-%d %H'`:${mm}"

setenv DATA_DIR /mesonet/data/gempak/snet
set grid=${DATA_DIR}/${date}_snet.gem


$GEMEXE/sflist << EOF > ../TMP/RWIS_sflist.out
	SFFILE = $grid
	AREA   = DSET
	DATTIM = /${hh}${mm}
	SFPARM = TMPF>-90;DWPF>-90;DRCT;SKNT;P24I;SRAD
	OUTPUT = f/snet.fil
	IDNTYP = STID
	list
	run

	exit
EOF


if (-e snet.fil) then
	sflist_2_db.py snet.fil snet.db D t${year}

	sflist_2_db.py snet.fil snet2.db D stransfer
	sflist_2_db.py snet.fil snet3.db D current

	psql -h iem40 snet << EOF > ../TMP/inject.out
	SET TIME ZONE 'GMT';
	DELETE from t${year} WHERE valid = '${sqlDate}';
	DELETE from current;
	\c compare
	SET TIME ZONE 'GMT';
	DELETE from stransfer WHERE valid = '${sqlDate}';
	\q
EOF

	#psql -h iem40 snet < snet.db >& /dev/null
	#psql -h iem40 compare < snet2.db >& /dev/null
	#psql -h iem40 snet < snet3.db >& /dev/null

	rm -f snet.fil snet.db snet2.db snet3.db >& /dev/null
endif
