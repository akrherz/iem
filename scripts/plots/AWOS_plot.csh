#!/bin/csh
#			AWOS_plot.csh
# Script that plots AWOS data.
# Daryl Herzmann 09 Jul 2001
# 31 Jul 2001:	Since I have a true AWOS file now,
#		the process is much more ez
# 08 Oct 2001:	Make things look a bit nicer
# 09 Nov 2001:	Change the date reporting for webpage
#		Plot ALTM, not PMSL
# 22 Apr 2002:	Piggy back CEIL
# 04 May 2002:	Update to 35 stations
# 28 May 2002:	Make sure that the ceil.gif is removed...
#  3 Oct 2002:  Dave did not want Reporting included...
#  4 Nov 2002:	Andy wanted wind barbs on the Ceiling plot...
# 17 Feb 2003:	Use GIF driver
# 21 Jan 2004	Code Audit
####################################################

source /mesonet/nawips/Gemenviron

set yy=`date -u --date '1 minute' +%y`
set MM=`date -u --date '1 minute' +%m`
set dd=`date -u --date '1 minute' +%d`
set date=${yy}${MM}${dd}
set hh=`date -u --date '1 minute' +%H`
set mm=`date -u --date '1 minute' +%M`


if (${mm} > 40 ) then
        set mm = "40"
else if (${mm} > 20) then
        set mm = "20"
else
        set mm = "00"
endif

setenv DISPLAY localhost:1

rm awos.gif* ceil.gif* >& /dev/null

set DEVICE="GF|awos.gif|650;500"
set DEVICE2="GF|ceil.gif|650;500"


$GEMEXE/sfmap_gf << EOF > /tmp/awos_plot_sfmap.out
 \$RESPOND = YES
	AREA    = 40.25;-97;43.75;-90
	GAREA    = 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  skyc;tmpf;wsym:1.2:2;;;dwpf;;;;brbk:1:2:111
	COLORS   =  32;2;32;4;32
 	DATTIM   =  ${date}/${hh}${mm}
	SFFILE   =  /mesonet/data/gempak/awos/${date}_awos.gem
 	LATLON   =  0
        TITLE    =  32/-1/~ AWOS Data 
        CLEAR    =  no
        PANEL    =  0
        DEVICE   = ${DEVICE}
        PROJ     =  LCC
        FILTER   =  .3
        TEXT     =  1/1//hw
        LUTFIL   =
        STNPLT   =
	MAP	= 25 + 25//2
	\$mapfil = HICNUS.NWS + hipowo.cia
	list
	run

	SFFILE	= /mesonet/data/gempak/meso/${date}_meso.gem
	DEVICE	= ${DEVICE2}
	SFPARM	= ;CEIL;wsym:1.2:2;;;;;;;brbk:1:2:111
	TITLE	= 32/-1/~ ASOS/AWOS Ceiling 100ft
	CLEAR	= yes
	list
	run

	exit
EOF

#gpend

#@ GOOD_AWOS=`wc -l awos.good | cut -d ' ' -f 1` - 3
#set TOTAL_AWOS=`wc -l /mesonet/TABLES/awos.stns | cut -c 6-7`


#mv awos.good WEB/
#echo "[/${hh}${mm}] ${GOOD_AWOS} / ${TOTAL_AWOS} " > ~/current/awos.stat
#echo "`date -u +%H%M` [${date}/${hh}${mm}] ${GOOD_AWOS} / ${TOTAL_AWOS} Reporting" >> ~/current/awos.log
#mv ~/current/awos.log /tmp/$$.txt
#tail -75 /tmp/$$.txt > ~/current/awos.log
#rm /tmp/$$.txt


if (-e awos.gif ) then
 # ~/bin/slogo.csh ~/plots/awos.gif
  #cp awos.gif ~/current/
  #mv ceil.gif ~/current/
  #mv awos.gif WEB/
  /home/ldm/bin/pqinsert -p "plot c 000000000000 awos.gif bogus gif" awos.gif
  /home/ldm/bin/pqinsert -p "plot c 000000000000 ceil.gif bogus gif" ceil.gif
endif
