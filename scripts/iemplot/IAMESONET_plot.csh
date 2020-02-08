#!/bin/csh
#		IAMESONET_plot.csh
# Finally, the script that plots all of this good data
# Daryl Herzmann 10 November 2000
# 19 Jun 2001:  Modified for use on the new mesonet box
#		Changed Smoothing of Pressure Field
# 02 Jul 2001:  Now we only have 1 GEMPAK file, yeah!
# 30 Jul 2001:	Lets Archive this plot, Eh?
# 31 Oct 2001:	Use 25x25 grid for Surface Contour
# 09 Nov 2001:	Plot ALTM instead of PMSL and use 50x50 grid
# 25 Feb 2002:	Place nicer timestamp on Plot
# 17 Feb 2003:	Use new GIF driver
# 23 Mar 2004	Lets filter more obs
####################################################

source /mesonet/nawips/Gemenviron

setenv GEMCOLTBL coltbl.xwp
setenv DISPLAY localhost:1

set yy=`date -u --date '1 minute' +'%y'`
set mm=`date -u --date '1 minute' +'%m'`
set dd=`date -u --date '1 minute' +'%d'`
set date=${yy}${mm}${dd}
set hh=`date -u --date '1 minute' +'%H'`
set timestamp=`date -u --date '1 minute' +'%Y%m%d%H00'`

set nicetime=`date -d "20${1}-${2}-${3} ${4}:00" +"%b %d %I %p"`
set generated=`date +"%b %d %I:%M %p"`
rm mesonet.gif* >& /dev/null

set DEVICE="GIF|mesonet.gif|900;700"
set AREA="40.15;-97.1;43.85;-89.9"

# Now we plot
sfmap << EOF > /dev/null
	AREA    = ${AREA}
	GAREA    = ${AREA}
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  skyc:.6;tmpf<120;wsym:1.2:2;alti;;dwpf<120;;;;brbk:1:1:231
	COLORS   =  32;2;32;0;4;32
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  /mesonet/data/gempak/meso/${date}_meso.gem
 	LATLON   =  0
        TITLE    =  32/-1/GMT: ~ Generated: $generated IEM Plot
        CLEAR    =  yes
        PANEL    =  0
        DEVICE   = ${DEVICE}
        PROJ     =  LCC
        FILTER   =  .5
        TEXT     =  1/1//hw
        LUTFIL   =
        STNPLT   =
	MAP	= 25 + 25//2
	\$MAPFIL = HICNUS.NWS + hipowo.cia
	list
	run

	exit
EOF


gdcntr << EOF > /tmp/IAMESONETplot_gdcntr.out
	GAREA    = ${AREA}
	GDATTIM  = ${date}/${hh}00F001
	GLEVEL   = 0
	GVCORD   = NONE
	GFUNC    = SM9S(MMSL)
	GDFILE   = /mesonet/data/iemplot/grid_25_25.grd
	CINT     = 1
	LINE     = 4
	MAP      = 0
	TEXT     = 1
	DEVICE   = ${DEVICE}
	SATFIL   =  
	RADFIL   =  
	PROJ     = LCC
	CLEAR    = no
	PANEL	= 0
	TITLE	= 32/-2/LOCAL: ${nicetime}
	SCALE    = 0
	LATLON   = 0
	HILO     =  
	HLSYM    =  
	CLRBAR   = 1
	CONTUR   = 3/3
	SKIP     = 0
	FINT     = 0
	FLINE    = 10-20
	CTYPE    = C
	LUTFIL   =  
	STNPLT   =  
	list
	run

	exit
EOF

gpend

if (-e mesonet.gif) then
	pqinsert -p "plot ac ${timestamp} mesonet.gif mesonet_${hh}00.gif gif" mesonet.gif
	rm -f mesonet.gif
endif
