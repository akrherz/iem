#!/bin/csh

source /mesonet/nawips/Gemenviron
set yy=`date +%y`
set mm=`date  +%m`
set dd=`date +%d`
set date=${yy}${mm}${dd}
set Date=`date +'%Y%m%d'`
set ftime="`date +'%Y%m%d'`0000"


/mesonet/python/bin/python extractPrecip.py
/mesonet/python/bin/python today_precip.py

cp /mesonet/data/gis/meta/4326.prj coop_${Date}.prj
cp data.desc coop_${Date}.txt
zip -q coop_${Date}.zip coop_${Date}.txt coop_${Date}.prj coop_${Date}.shp coop_${Date}.shx coop_${Date}.dbf 

/home/ldm/bin/pqinsert -p "zip ac $ftime gis/shape/4326/iem/coopobs.zip GIS/coop_${Date}.zip zip" coop_${Date}.zip
rm -f coop_${Date}.* 

sfdelt << EOF > /tmp/PREC_sfdelt.out
	SFFILE	= coop.gem
	DATTIM	= ALL
	SFPARM	= ALL
	AREA	= DSET
	list
	run

	exit
EOF

sfedit << EOF > /tmp/PREC_sfedit.out
	SFFILE	= coop.gem
	SFEFIL	= coop_obs.fil
	list
	run

	exit
EOF

gddelt << EOF > /tmp/PREC_gddelt.out
        GDFILE	= coop.grd
        GDATTIM = ALL
        GDNUM   = ALL
        GFUNC   = ALL
        GLEVEL  = ALL
        GVCORD  = ALL
        list
        run

EOF

oabsfc << EOF > /tmp/PREC_oabsfc.out
        SFFILE   = coop.gem
        GDFILE   = coop.grd
        SFPARM   = P24I
        DATTIM   = ${date}/1200
        DTAAREA  =
        GUESS    =
        GAMMA    = .3
        SEARCH   = 20
        NPASS    = 2
        QCNTL    = 
        list
        run

EOF

gpend

rm coopPrec.gif* >& /dev/null

$GEMEXE/gdplot << EOF > /tmp/PREC_gdplot1.out
        GDFILE  = coop.grd
        GDATTIM = ${date}/1200
        PANEL	= 0
        MAP	= 25/1/1
        CLEAR	= yes
        CLRBAR	= 1
        PROJ	= lcc
        LATLON	= 0
        TEXT	= 1.0/2//hw
        GAREA	= 40.25;-97;43.75;-90

        DEVICE  = GIF|coopPrec.gif|900;700
        GLEVEL   = 0
        GVCORD   = none
        SKIP     =
        SCALE    = 0
        GFUNC    = P24I
        CTYPE    = c/f
        CONTUR   = 
        CINT     = .1
        LINE     = 32/1/1
	FINT    = 0.01;0.10;0.25;0.50;0.75;1.0;1.25;1.5;1.75;2.0;2.25;2.50;2.75;3.0
	FLINE   = 0;21-23;26-31;14;15;2;5
        HILO     = 
        HLSYM    = 2;1.5//21//hw
        GVECT    = 
        WIND     =
        REFVEC   = 
        TITLE    = 32/-1/~ COOP 24h PRECIP [.01 inches]
        SATFIL   = 
        RADFIL   = 
        STNPLT   = 
        list
        run

        exit
EOF

rm coopPrecPlot.gif* >& /dev/null
rm coopSnowPlot.gif* >& /dev/null

$GEMEXE/sfmap << EOF > /tmp/PREC_sfmap.out
        AREA    = 40.25;-97;43.75;-90
        GAREA    = 40.25;-97;43.75;-90
        SATFIL   =  
        RADFIL   =  
        SFPARM   =  MARK;STID;P24I*100>-1
        COLORS   =  25;25;4
        DATTIM   =  ${date}/1200
        SFFILE   =  coop.gem
        MAP      =  25//2 + 25
        LATLON   =  0
        TITLE    =  32/-1/~ COOP PRECIP REPORTS [.01 inch]
        CLEAR    =  no
        PANEL    =  0
        DEVICE   = GIF|coopPrecPlot.gif|900;700
        PROJ     =  LCC
        FILTER   =  .3
        TEXT     =  1/1//hw
        LUTFIL   =
        STNPLT   =
        \$mapfil = HIPOWO.CIA + HICNUS.NWS
        list
        run

	SFPARM	= MARK;STID;SNOW>-1
	TITLE	=  32/-1/~ COOP SNOW REPORTS [inches]
	DEVICE	= GIF|coopSnowPlot.gif|900;700
	list
	run

	SFPARM	= MARK;STID;SNOD>-1
	TITLE   =  32/-1/~ NWS COOP SNOW DEPTH REPORTS [inches]
	DEVICE  = GIF|coopSnowDepth.gif|900;700
        list
        run

	SFPARM	= MARK;TMPX;STID;;;TMPN>-50
	COLORS	= 25;2;25;4
	TITLE	= 32/-1/~ NWS COOP HIGH AND LOW TEMPS [F]
	DEVICE	= GIF|coopHighLow.gif|900;700
	list
	run

	exit
EOF


rm coopMonthPlot.gif* >& /dev/null
rm coopMonthSPlot.gif* >& /dev/null

$GEMEXE/sfmap << EOF > /tmp/PREC_sfmap2.out
        AREA    = 40.25;-97;43.75;-90
        GAREA    = 40.25;-97;43.75;-90
        SATFIL   =
        RADFIL   =
        SFPARM   =  MARK;STID;PMOI*100>-1
        COLORS   =  25;25;4
        DATTIM   =  ${date}/1200
        SFFILE   =  coop.gem
        MAP      =  25//2 + 25
        LATLON   =  0
        TITLE    =  32/-1/~ COOP PRECIP ACCUM THIS MONTH [.01 inch]
        CLEAR    =  no
        PANEL    =  0
        DEVICE   = GIF|coopMonthPlot.gif|900;700
        PROJ     =  LCC
        FILTER   =  .3
        TEXT     =  1/1//hw
        LUTFIL   =
        STNPLT   =
        \$mapfil = HIPOWO.CIA + HICNUS.NWS
        list
        run

	SFPARM	= MARK;STID;SMOI*100>-1
	TITLE    =  32/-1/~ COOP SNOW ACCUM THIS MONTH [.01 inch]
	DEVICE	= GIF|coopMonthSPlot.gif|900;700
	list
	run

        exit
EOF

gpend

if (-e coopPrecPlot.gif ) then
/home/ldm/bin/pqinsert -p "plot ac $ftime coopPrecPlot.gif coopPrecPlot.gif gif" coopPrecPlot.gif >& /dev/null
/home/ldm/bin/pqinsert -p "plot ac $ftime coopSnowPlot.gif coopSnowPlot.gif gif" coopSnowPlot.gif >& /dev/null
/home/ldm/bin/pqinsert -p "plot ac $ftime coopSnowDepth.gif coopSnowDepth.gif gif" coopSnowDepth.gif >& /dev/null
/home/ldm/bin/pqinsert -p "plot ac $ftime coopHighLow.gif coopHighLow.gif gif" coopHighLow.gif >& /dev/null
else
	echo "COOP Precip Plot did not get made" | mail -s "[MESONET] COOP Problem" akrherz@iastate.edu
endif

if (-e coopPrec.gif ) then
/home/ldm/bin/pqinsert -p "plot c $ftime coopPrec.gif coopPrec.gif gif" coopPrec.gif >& /dev/null
	#mv coopPrec.gif ~/current
endif 

if (-e coopMonthPlot.gif ) then
/home/ldm/bin/pqinsert -p "plot c $ftime coopMonthPlot.gif coopMonthPlot.gif gif" coopMonthPlot.gif >& /dev/null
/home/ldm/bin/pqinsert -p "plot c $ftime coopMonthSPlot.gif coopMonthSPlot.gif gif" coopMonthSPlot.gif >& /dev/null
	#mv coopMonthPlot.gif ~/current
	#mv coopMonthSPlot.gif ~/current
endif

/mesonet/python/bin/python monthPrecip.py
/home/ldm/bin/pqinsert -p 'plot c 000000000000 text/IEMNWSMPR.txt bogus txt' IEMNWSMPR.txt >& /dev/null

/mesonet/python/bin/python yearPrecip.py
/home/ldm/bin/pqinsert -p 'plot c 000000000000 text/IEMNWSYPR.txt bogus txt' IEMNWSYPR.txt >& /dev/null

/mesonet/python/bin/python dayPrecip.py
/home/ldm/bin/pqinsert -p "plot ac $ftime text/IEMNWSDPR.txt coopobs.txt txt" IEMNWSDPR.txt >& /dev/null
