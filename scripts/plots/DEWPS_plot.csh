#!/bin/csh
# Finally, the script that plots all of this good data
# Daryl Herzmann 10 November 2000
# 19 Jun 2001:	Adapted for mesonet box
# 2 Jul 2001:  Make the outline of the state a bit nicer
# 17 Sep 2001:	Adjust title to fit on screen
# 17 Feb 2003:	Use GIF driver

source /mesonet/nawips/Gemenviron

setenv GEMCOLTBL coltbl.xwp

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`

# rm temps.gif*

set DEVICE="GIF|dewps.gif"

$GEMEXE/sfmap << EOF > TMP/DEWPS_plot_sfmap.out
	AREA    = 40.25;-97;43.75;-90
	GAREA    = 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  dwpf<120
	COLORS   =  2
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  /mesonet/data/gempak/sao/${date}_sao.gem
 	LATLON   =  0
        TITLE    =  32/-1/~ Dew Point Comp [ASOS/AWOS red]  [RWIS blue]
        CLEAR    =  no
        PANEL    =  0
        DEVICE   = ${DEVICE}
        PROJ     =  LCC
        FILTER   =  .3
        TEXT     =  1/1//hw
        LUTFIL   =
        STNPLT   =
	MAP     = 25 + 25//2
	\$MAPFIL = HICNUS.NWS + hipowo.cia
	list
	run

EOF

$GEMEXE/sfmap << EOF > TMP/DEWPS_plot_sfmap2.out
	COLORS  =  4
	SFFILE	= /mesonet/data/gempak/rwis/${date}_rwis.gem
	TITLE	= 0
	MAP	= 0
	CLEAR	= no
        DEVICE   = ${DEVICE}
	list	
	run

	exit
EOF

$GEMEXE/gpend

if (-e dewps.gif) then
	#cp dewps.gif ~/current
	#mv dewps.gif WEB/
/home/ldm/bin/pqinsert -p "plot c 000000000000 dewps.gif dewps.gif gif" dewps.gif >& /dev/null
endif
