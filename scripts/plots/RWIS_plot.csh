#!/bin/csh
# Finally, the script that plots all of this good data
# Daryl Herzmann 10 November 2000
# 19 Jun 2001:	Added QC to the end
# 20 Jun 2001:	Mod for better Map display
# 10 Jul 2001:	Lets make a log File as well
# 08 Nov 2001:	Change output of date for the web
#  3 Oct 2002:	Dave doesn't want Reporting Included...
# 17 Feb 2003:	Use GIF driver
########################################################

source /mesonet/nawips/Gemenviron
setenv DISPLAY localhost:1

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`
set MM=`date -u +%M`

if (${MM} > 40 ) then
        set MM = "40"
else if (${MM} > 30) then
        set MM = "20"
else
        set MM = "00"
endif


rm -f rwis.gif >& /dev/null

set DEVICE="GF|rwis.gif|650;500"


$GEMEXE/sfmap_gf << EOF > /tmp/RWIS_plot_sfmap.out
	AREA	 = 40.25;-97;43.75;-90
	GAREA    = 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  ;tmpf<120;dwpf<120;;;;;;;brbk:1:2:231
	COLORS   =  2;4;32
 	DATTIM   =  ${date}/${hh}${MM}
 	SFFILE   =  /mesonet/data/gempak/rwis/${date}_rwis.gem
 	LATLON   =  0
        TITLE    =  32/-1/~ RWIS Data 
        CLEAR    =  no
        PANEL    =  0
        DEVICE   = ${DEVICE}
        PROJ     =  LCC
        FILTER   =  .3
        TEXT     =  1/1//hw
        LUTFIL   =
        STNPLT   =
	MAP	= 25 + 25//3
	\$mapfil = HICNUS.NWS + hipowo.cia
	list
	run

	exit
EOF


###
# If RWIS data is not there
#if (! -e rwis.good ) then
#	set GOOD_RWIS = 0
#	set TOTAL_RWIS=`wc -l /mesonet/TABLES/RWIS.stns | cut -c 6-7`
#else
#	@ GOOD_RWIS=`wc -l rwis.good | cut -d ' ' -f 1` - 2 
#	set TOTAL_RWIS=`wc -l /mesonet/TABLES/RWIS.stns | cut -c 6-7`
#
#	mv rwis.good WEB/
#endif

#echo "[/${hh}${MM}] ${GOOD_RWIS} / ${TOTAL_RWIS} " > ~/current/rwis.stat
#echo "`date -u +%H%M` [${date}/${hh}${MM}] ${GOOD_RWIS} / ${TOTAL_RWIS} Reporting" >> ~/current/rwis.log
#mv ~/current/rwis.log /tmp/$$.txt
#tail -96 /tmp/$$.txt > ~/current/rwis.log
#rm /tmp/$$.txt


if (-e rwis.gif) then
	#~/bin/slogo.csh ~/plots/rwis.gif
	#cp rwis.gif ~/current/
	#mv rwis.gif WEB/
  /home/ldm/bin/pqinsert -p "plot c 000000000000 rwis.gif rwis.gif gif" rwis.gif
endif
