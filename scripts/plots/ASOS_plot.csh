#!/bin/csh
# Finally, the script that plots all of this good data
# Daryl Herzmann 10 November 2000
# 08 June 2001:  Added a bit more logic to the script
# 18 Jun 2001:	updated for mesonet box
#		Added QC logic
# 20 Jun 2001:	Changed how map is displayed
# 10 Jul 2001:	Lets Append a text QA product
#		Only plot 00 Stuff
# 09 Nov 2001:	Change the Date output to only hour for webpage
#		Plot ALTM  instead of PMSL
# 04 May 2002:	Update to 50 stations
#  3 Oct 2002:	Dave did not want Reporting included!!
# 17 Feb 2003:	Switch to use the GIF driver and hopefully not a Xvfb
# 11 Feb 2004	Code Audit
#
#############################################

source /mesonet/nawips/Gemenviron

setenv DISPLAY localhost:1

set yy=`date -u +%y`
set MM=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${MM}${dd}
set hh=`date -u +%H`

set mm = "00"

rm asos.gif* >& /dev/null

set DEVICE="GF|asos.gif"


$GEMEXE/sfmap_gf << EOF > TMP/sfmap.out
	AREA    = 40.25;-97;43.75;-90
	GAREA    = 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  skyc;tmpf;wsym:1.2:2;altm;;dwpf;;;;brbk:1:2:231
	COLORS   =  32;2;32;25;4;32
 	DATTIM   =  ${date}/${hh}${mm}
 	SFFILE   =  /mesonet/data/gempak/sao/${date}_sao.gem
 	LATLON   =  0
        TITLE    =  32/-1/~ ASOS/AWOS Data 
        CLEAR    =  no
        PANEL    =  0
        DEVICE   = ${DEVICE}
        PROJ     =  LCC
        FILTER   =  .3
        TEXT     = 1.2
        LUTFIL   =
        STNPLT   =
	MAP	= 25 + 25//2
	\$mapfil = HICNUS.NWS + hipowo.cia
	list
	run

	exit
EOF


#####
# Lets count how many we have reporting
#sfchck << EOF > TMP/sfchck.out
#        SFFILE   = /mesonet/data/gempak/sao/${date}_sao.gem
#        AREA     = @IA
#        DATTIM   = ${date}/${hh}${mm}
#        OUTPUT   = f/asos.good
#        IDNTYP   = STID
#        STNTYP   = R
##        list
#        run
#
#        exit
#EOF

#@ GOOD_ASOS = `wc -l asos.good | cut -d ' ' -f 1` - 2
#set TOTAL_ASOS=`wc -l /mesonet/TABLES/iowa.stns | cut -c 6-7`


#mv asos.good WEB/
#echo "[/${hh}${mm}] ${GOOD_ASOS} / ${TOTAL_ASOS} " > ~/current/asos.stat
#echo "`date -u +%H%M` [${date}/${hh}${mm}] ${GOOD_ASOS} / ${TOTAL_ASOS} Reporting" >> ~/current/asos.log
#mv ~/current/asos.log /tmp/$$.txt
#tail -96 /tmp/$$.txt > ~/current/asos.log
#rm /tmp/$$.txt

if (-e asos.gif ) then
  #~/bin/logo.csh ~/plots/asos.gif
  #cp asos.gif ~/current/
  #mv asos.gif WEB/
  /home/ldm/bin/pqinsert -p "plot c 000000000000 asos.gif bogus gif" asos.gif >& /dev/null
endif
