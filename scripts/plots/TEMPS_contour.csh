#!/bin/csh
# Finally, the script that plots all of this good data
# Daryl Herzmann 10 November 2000
# 19 June 2001:  Adapted for mesonet box
# 2 jul 2001:	Lets do the map correctly, Geez. One Time
# 17 Feb 2003:	Use GIF driver
#  4 Apr 2003	Set display variable

source /mesonet/nawips/Gemenviron
setenv DISPLAY localhost:1


set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`

rm temps_contour.gif* dewps_contour.gif* >& /dev/null

gddelt << EOF > TMP/TEMPS_contour_gddelt.out
        GDFILE = /mesonet/data/gempak/asos.grd
        GDATTIM = ALL
        GDNUM   = ALL
        GFUNC   = ALL
        GLEVEL  = ALL
        GVCORD  = ALL
        list
        run

        GDFILE = /mesonet/data/gempak/rwis.grd
	list
	run

EOF

gpend

oabsfc << EOF > TMP/TEMPS_contour_oabsfc.out
	DATTIM	= ${date}/${hh}00
        DTAAREA  =
        GUESS    =
        GAMMA    = .3
        SEARCH   = 20
        NPASS    = 2
        QCNTL    = 10;10;;;;;;
        SFFILE   = /mesonet/data/gempak/sao/${date}_sao.gem
        GDFILE   = /mesonet/data/gempak/asos.grd
        SFPARM   = TMPF;DWPF;ALTI
        list
        run

        SFFILE  = /mesonet/data/gempak/rwis/${date}_rwis.gem
        GDFILE  = /mesonet/data/gempak/rwis.grd
#        GUESS   = ../DATA/asos.grd*${date}/${hh}00
	GUESS   = 
        SFPARM  = TMPF;DWPF
        list
        run

        exit
EOF

gpend
gpend

set DEVICE1="GIF|temps_contour.gif"
set DEVICE2="GIF|dewps_contour.gif"


$GEMEXE/gdplot_gf << EOF > TMP/TEMPS_contour_gdcntr.out
	GAREA    = 40.25;-97;43.75;-90
	GDATTIM  = ${date}/${hh}
	GLEVEL   = 0
	GVCORD   = NONE
	GFUNC    = SM9S(TMPF+1) ! SM9S(TMPF+2)
	GDFILE   = rwis.grd + asos.grd
	CINT     = 4		!4
	LINE     = 4/1/1	!2/1/1
	TEXT     = 1/1
	DEVICE   = ${DEVICE1}
	SATFIL   =  
	RADFIL   =  
	PROJ     = LCC
	CLEAR    = no
	PANEL	= 0
	TITLE	= 32/-1/~ Temp Contours [ASOS/AWOS RED]  [RWIS BLUE]
	SCALE	= 0
	GVECT   =
	WIND    = 
	LATLON	= 0
	HILO     =  
	HLSYM    =  
	CLRBAR   = 1
	CONTUR   = 3/3
	SKIP     = 0
	FINT     = 
	FLINE    = 
	CTYPE    = C	!C
	LUTFIL   =  
	STNPLT   =
	MAP     = 25 + 25//2
	\$MAPFIL = HICNUS.NWS + hipowo.cia
	list
	run

	GFUNC    = SM9S(DWPF+1) ! SM9S(DWPF+2)
	TITLE	= 32/-1/~ Dewp Contours [ASOS/AWOS RED]  [RWIS BLUE]
	DEVICE   = ${DEVICE2}
	list
	run

	exit
EOF



if (-e temps_contour.gif) then
	#~/bin/logo.csh ~/plots/temps_contour.gif
	#~/bin/logo.csh ~/plots/dewps_contour.gif

	cp temps_contour.gif ~/current/
	cp dewps_contour.gif ~/current/
	mv temps_contour.gif WEB/
	mv dewps_contour.gif WEB/
endif
