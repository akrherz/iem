#!/bin/csh
#	RWIS_SF_plot.csh
# Plots RWIS SF stuff
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


rm -f rwis_sf.gif* >& /dev/null

set DEVICE="GF|rwis_sf.gif|800;600"


$GEMEXE/sfmap_gf << EOF > TMP/rwis_sf_sfmap.out
	AREA	 = 40.25;-97;43.75;-90
	GAREA    = 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  stid;tcs0;;tcs1;;tcs2;tcs3;;subc
	COLORS   =  25;2;2;2;2;4
 	DATTIM   =  /${hh}${MM}
 	SFFILE   =  /mesonet/data/gempak/pavement/${date}_rsf.gem
 	LATLON   =  0
        TITLE    =  32/-1/~ RWIS Pavement Sfc Temps (red) Sub-Surface (blue) [F]
        CLEAR    =  no
        PANEL    =  0
        DEVICE   = ${DEVICE}
        PROJ     =  LCC
        FILTER   =  .5
        TEXT     =  .7/1//hw
        LUTFIL   =
        STNPLT   =
	MAP	= 25 + 25//3
	\$mapfil = HICNUS.NWS + hipowo.cia
	list
	run

	exit
EOF

if (-e rwis_sf.gif) then
 /home/ldm/bin/pqinsert -p "plot c 000000000000 rwis_sf.gif rwis_sf.gif gif" rwis_sf.gif >& /dev/null
 rm rwis_sf.gif
endif
