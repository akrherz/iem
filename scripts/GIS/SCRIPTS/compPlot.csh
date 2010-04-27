#! /bin/csh 
#		compRADAR.csh
#  Makes the Composite RADAR image for our GIS Apps
#  Daryl Herzmann 24 Aug 2001
# 1 Sep 2001	Also write a temp file that other programs can see
# 07 Mar 2002:	Cleanup and do the right file this time
#  8 Aug 2002:	Place files in new location...
#  4 Jan 2003:	Hush on the errors
# 17 Feb 2003:	Use GIF driver
# 19 Jun 2003	Back to GF driver, make this standard proj, png format
#####################################################

source /mesonet/nawips/Gemenviron

# Go and create the grid file
cd /mesonet/scripts/gempak/SCRIPTS
./gridRADAR.csh

cd /mesonet/scripts/GIS/SCRIPTS

setenv DISPLAY localhost:1

set date=`date -u +%y%m%d`
set hh=`date -u +%H`

set grid=/mesonet/data/gempak/radar.gem


rm compRADAR.gif* compRADAR.png* >& /dev/null

set MYDATE=`date +"%d %b %I:%M %p"`

$GEMEXE/gdcntr_gf << EOF > ../TMP/compRADAR_gdcntr.out
	GDFILE	= $grid
	GDATTIM	= LAST
	GFUNC	= N0R
	PANEL	= 0
	MAP      = 0
	CLEAR	= yes
	PROJ     = lcc
	LATLON   = 0
	GAREA    = 40.25;-97;43.75;-90

	DEVICE	= GF|compRADAR.gif|600;450
	\$mapfil = 
	text     = 1/1/1
	TITLE    = 0
	GLEVEL   = 0
	GVCORD   = none
	CTYPE    = F
	PANEL    = 0
	SKIP     = 0
	SCALE    = 0
	CONTUR   = 0
	HILO     =
	LATLON   = 0
	STNPLT   =
	SATFIL   =
	RADFIL   =
	LUTFIL   =
	STREAM   =
	POSN     = 0
	COLORS   = 1
	MARKER   = 0
	GRDLBL   = 0
	FILTER   = YES
	FINT     = 10;15;20;25;30;35;40;45;50;55;60;65;70;75;85
	FLINE    = 0;26;24;21;22;23;20;18-16;14-10;0
	CLRBAR   = 0
	list
	run

	exit
EOF


if (-e compRADAR.gif) then
  convert compRADAR.gif compRADAR.png
  mv compRADAR.png /mesonet/data/gis/images/26915/IOWA_N0R.png

endif

exit

rm *.gif compRADAR.tif >& /dev/null

set TMPVAR=`grep "NONE N0R" ../TMP/compRADAR_gdcntr.out`
set RADTIME=`echo ${TMPVAR} | cut -d " " -f 1`

cd /mesonet/www/html/GIS/apps/IAoverlay

cat ia_top.edit > ia_top.html
echo "<P><TABLE><TR><TD>RADAR valid at:</TD><TD> ${RADTIME} </TD></TR>" >> ia_top.html

echo ${RADTIME} > /tmp/compRADAR.time
