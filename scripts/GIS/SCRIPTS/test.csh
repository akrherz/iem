#! /bin/csh 
#		compRADAR.csh
#  Makes the Composite RADAR image for our GIS Apps
#  Daryl Herzmann 24 Aug 2001
# 1 Sep 2001	Also write a temp file that other programs can see
# 17 Feb 2003:	Use GIF driver
#######################################################

source ~nawips/Gemenviron

# Go and create the grid file
cd ~/gempak/SCRIPTS
./gridRADAR.csh

cd ~/GIS/SCRIPTS


set date=`date -u +%y%m%d`
set hh=`date -u +%H`

set grid=/mesonet/data/gempak/radar.gem

rm compRADAR.gif*  compRADAR.tif* >& /dev/null

$GEMEXE/gdcntr << EOF > ../TMP/compRADAR_gdcntr.out
	GDFILE	= $grid
	GDATTIM	= LAST
	GFUNC	= N0R
	PANEL	= 0
	MAP      = 4
	CLEAR	= yes
	PROJ     = lcc
	LATLON   = 0
	GAREA    = 40.25;-97;43.75;-90

	DEVICE	= GIF|compRADAR.gif|600;450
	\$mapfil = 
	text     = 1/1/1
	TITLE    = 4/-1/~ IOWA COMPOSITE BASE REFLECTIVITY
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

gpend

convert compRADAR.gif compRADAR.tif

#convert -crop 600x520+0+40 compRADAR.tif compRADAR2.tif

#geotifcp -e compRADAR.wld compRADAR.tif /mesonet/www/html/GIS/data/images/compRADAR.tif

#diff badRad.tif /mesonet/www/html/GIS/data/images/compRADAR.tif >& /dev/null
#if ( $status != 0 ) then
#  #  echo "Files Are Different"
#else
#    cp whiteRad.tif /mesonet/www/html/GIS/data/images/compRADAR.tif
#  #  echo "Files are Similar"
#endif


