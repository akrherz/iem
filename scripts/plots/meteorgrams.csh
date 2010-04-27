#!/bin/csh -f
#		meteorgrams.csh				#
# Script that plots the comparison Meteorgrams		#
# Daryl Herzmann 8 June 2001				#
# 18 Jun 2001: Updated for use on Mesonet box		#
# 17 Feb 2003:	Use GIF driver	
#  4 Apr 2003	Set a display variable
########################################################

source /mesonet/nawips/Gemenviron
setenv DISPLAY localhost:1

set DEVICE1="GIF|dsm.gif"
set DEVICE2="GIF|cbf.gif"
set DEVICE3="GIF|cid.gif"

rm tst.gif dsm.gif cbf.gif cid.gif >& /dev/null

#setenv DISPLAY localhost:1
mv coltbl.xwp coltbl.xwp.ORIG

$GEMEXE/sfgram_gf << EOF > /tmp/meteorgrams_sfgram.out
	SFFILE   = /mesonet/data/gempak/24hour.gem
	DATTIM   = ALL
	STATION  = DSM;RDES;DSM;RDES
	TRACE1   = TMPF;DWPF:2/2;3
	TRACE2   = TMPF;DWPF:4/2;3
	TRACE3   = SKNT/4!DRCT/1/0;360
	TRACE4   = SKNT/4!DRCT/1/0;360
	TRACE5   = 
	NTRACE   = 4
	TAXIS    =  
	BORDER   = 1
	MARKER   = 0
	TITLE	= 1
#	TITLE	= 5/-1/~ Meteorgram comparison DSM RDES
	CLEAR    = YES
	DEVICE   = ${DEVICE1}
	PANEL    = 0
	TEXT     = 1
	list
	run

	STATION  = CBF;RCOU;CBF;RCOU
	DEVICE   = ${DEVICE2}
	TITLE	= 1
	list
	run

	STATION  = CID;RCID;CID;RCID
	DEVICE   = ${DEVICE3}
	TITLE	= 1
	list
	run

	exit
EOF

mv coltbl.xwp.ORIG coltbl.xwp

if (-e dsm.gif) then
	#cp dsm.gif WEB/
	#mv dsm.gif ~/current/dsm_sfgram.gif
 /home/ldm/bin/pqinsert -p "plot c 000000000000 dsm_sfgram.gif bogus gif" dsm.gif >& /dev/null
endif

if (-e cbf.gif) then
	#cp cbf.gif WEB/
	#mv cbf.gif ~/current/cbf_sfgram.gif
 /home/ldm/bin/pqinsert -p "plot c 000000000000 cbf_sfgram.gif bogus gif" cbf.gif >& /dev/null
endif

if (-e cid.gif) then
	#cp cid.gif WEB/
	#mv cid.gif ~/current/cid_sfgram.gif
 /home/ldm/bin/pqinsert -p "plot c 000000000000 cid_sfgram.gif bogus gif" cid.gif >& /dev/null
endif
# Done :)
