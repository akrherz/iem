#! /bin/csh 

source /mesonet/nawips/Gemenviron

setenv DISPLAY localhost:1

set date=`date -u +%y%m%d`
set hh=`date -u +%H`
set hhmm="`date -u +%H`00"
set ftime="`date -u +'%Y%m%d%H'`00"

set grid1=/mesonet/data/gempak/surface50x50.grd

$GEMEXE/gdplot2_gf << EOF > /tmp/sf_gdplot1.out
	GDFILE	= $grid1
	GDATTIM	= ${date}/${hh}00
	PANEL	= 0
	MAP      = 15/1/2
	CLEAR	= yes
	CLRBAR  = 31
	PROJ     = lcc
	LATLON   = 0
	TEXT     = 1.0/2//hw
	GAREA    = 40.25;-97;43.75;-90

	DEVICE	= GF|surfaceTW.gif|720;540
	GLEVEL   = 0
	GVCORD   = none
	SKIP     = /1/1
	SCALE    = 0
	GDPFUN	= tmpf ! KNTV(WND)
	TYPE    = c/f	!B
	CONTUR   = 
	CINT     = 2
	LINE     = 32/1/1
	FINT     = 2
	FLINE    = 28-16--1;14-8--1;28-16--1
	HILO     = 
	HLSYM    = 2;1.5//21//hw
	CLRBAR   = 1
	WIND     = bk32/1.0/2
	REFVEC   = 
	TITLE    = 31/-2/~ SURFACE TEMPERATURE (F) AND WINDS
	SATFIL   = 
	RADFIL   = 
	STNPLT   = 
	list
	run

	exit
EOF

$GEMEXE/gdplot2_gf << EOF > /tmp/sf_gdplot2.out
	GLEVEL	= 0
	DEVICE	= GF|surfaceDW.gif|720;540
	GAREA	= 40.25;-97;43.75;-90
	GVCORD	= none
	PANEL	= 0
	SKIP	= /4/4
	SCALE	= 0
	GDPFUN	= dwpf	!KNTV(WND)
	TYPE	= c/f	!B
	CONTUR	= 
	CINT	= 2
	LINE	= 32/1/1
	FINT	= 2
	FLINE	= 28-16--1;14-8--1;28-16--1
	HILO	= 
	HLSYM	= 2;1.5//21//hw
	CLRBAR	= 1
	WIND	= bk32/1.0/2
	REFVEC	= 
	TITLE	= 31/-2/~ SURFACE DEW POINT (F) AND WINDS
	SATFIL	= 
	RADFIL	= 
	PROJ	= lcc
	LATLON	= 0
	STNPLT	= 
	list
	run

	exit
EOF

$GEMEXE/gdplot2_gf << EOF > /tmp/sf_gdplot3.out
	GLEVEL	= 0
	DEVICE	= GF|surfaceMD.gif|720;540
	GAREA	= 40.25;-97;43.75;-90
	GVCORD	= none
	PANEL	= 0
	SKIP     = /4/4
	SCALE    = 0
	GDPFUN	= mul(div((smul(mixr(dwpc,pmsl),wnd)),1000000) ! KNTV(WND)
	TYPE    = c/f	! B
	CONTUR   = 
	LINE     = 32/1/1
	FLINE    = 29-12--1
CINT=-2;-1.6;-1.2;-0.8;-0.4;-0.3;-0.2;-0.1;0;0.1;0.2;0.3;0.4;0.8;1.2;1.6;2
FINT=-2;-1.6;-1.2;-0.8;-0.4;-0.3;-0.2;-0.1;0;0.1;0.2;0.3;0.4;0.8;1.2;1.6;2
	HILO     = 
	HLSYM    = 2;1.5//21//hw
	CLRBAR   = 32
	WIND     = bk32/1.0/2
	REFVEC   = 
	TITLE    = 31/-2/~ SURFACE MOISTURE DIVERGENCE
	CLEAR    = yes
	SATFIL   = 
	RADFIL   = 
	PROJ     = lcc
	LATLON   = 0
	STNPLT   = 
	list
	run

	exit
EOF

$GEMEXE/gdplot2_gf << EOF > /tmp/sf_DIV.out
        GLEVEL  = 0
        DEVICE  = GF|surfaceDIV.gif|720;540
        GAREA   = 40.25;-97;43.75;-90
        GVCORD  = none
        PANEL   = 0
        SKIP     = /4/4
        SCALE    = 0
        GDPFUN  = mul(div(wnd),10000) ! KNTV(WND)
        TYPE    = c/f   ! B
        CONTUR   = 
CINT=-2;-1.6;-1.2;-0.8;-0.4;-0.3;-0.2;-0.1;0;0.1;0.2;0.3;0.4;0.8;1.2;1.6;2
        LINE     = 32/1/1
FINT=-2;-1.6;-1.2;-0.8;-0.4;-0.3;-0.2;-0.1;0;0.1;0.2;0.3;0.4;0.8;1.2;1.6;2
        FLINE    = 29-12--1
        HILO     = 
        HLSYM    = 2;1.5//21//hw
        CLRBAR   = 1
        WIND     = bk32/1.0/2
        REFVEC   = 
        TITLE    = 31/-2/~ SURFACE DIVERGENCE
        CLEAR    = yes
        SATFIL   = 
        RADFIL   = 
        PROJ     = lcc
        LATLON   = 0
        STNPLT   = 
        list
        run

        exit
EOF

$GEMEXE/gdplot2_gf << EOF > /tmp/sf_gdplot4.out
	GLEVEL   = 0
	DEVICE	= GF|surfaceTE.gif|720;540
	GAREA	= 40.25;-97;43.75;-90 
	GVCORD   = none
	PANEL    = 0
	SKIP     = /4/4
	SCALE    = 0
	GDPFUN	= thte(pmsl,tmpc,dwpc)	!KNTV(WND)
	CTYPE    = c/f	!B
	CONTUR   = 
	CINT     = 4
	LINE     = 32/1/1
	FINT     = 4  
	FLINE    = 28-16--1;14-8--1;28-16--1
	HILO     = 
	HLSYM    = 2;1.5//21//hw
	CLRBAR   = 1
	WIND     = bk32/1.0/2
	REFVEC	= 
	TITLE	= 31/-2/~ SURFACE THETA-E (K)
	CLEAR    = yes
	SATFIL   = 
	RADFIL   = 
	PROJ     = lcc
	LATLON   = 0
	STNPLT   = 
	list
	run

	exit
EOF

$GEMEXE/gdplot2_gf << EOF > /tmp/sf_gdplot4.out
        GLEVEL   = 0
        DEVICE  = GF|surfaceFRNT.gif|720;540
        GAREA   = 40.25;-97;43.75;-90 
        GVCORD   = none
        PANEL    = 0
        SKIP     = /4/4
        SCALE    = 0
        GDPFUN  = FRNT(THTA(tmpc,pmsl),VECN(UWND,VWND))
        CTYPE    = c/f  !B
        CONTUR   = 
        CINT     = 1
        LINE     = 32/1/1
        FINT     = 4  
        FLINE    = 28-16--1;14-8--1;28-16--1
        HILO     = 
        HLSYM    = 2;1.5//21//hw
        CLRBAR   = 1
        WIND     = bk32/1.0/2
        REFVEC  = 
        TITLE   = 31/-2/~ SURFACE FRONTOGENSIS
        CLEAR    = yes
        SATFIL   = 
        RADFIL   = 
        PROJ     = lcc
        LATLON   = 0
        STNPLT   = 
        list
        run

        exit
EOF


if (-e surfaceTW.gif ) then
pqinsert -p "plot ar $ftime surfaceTW surfaceTW_${hhmm}.gif gif" surfaceTW.gif >& /dev/null
rm surfaceTW.gif
endif

if (-e surfaceDW.gif ) then
pqinsert -p "plot ar $ftime surfaceDW surfaceDW_${hhmm}.gif gif" surfaceDW.gif >& /dev/null
rm surfaceDW.gif
endif

if (-e surfaceMD.gif ) then
pqinsert -p "plot ar $ftime surfaceMD surfaceMD_${hhmm}.gif gif" surfaceMD.gif >& /dev/null
rm surfaceMD.gif
endif

if (-e surfaceTE.gif ) then
pqinsert -p "plot ar $ftime surfaceTE surfaceTE_${hhmm}.gif gif" surfaceTE.gif >& /dev/null
rm surfaceTE.gif
endif

if (-e surfaceDIV.gif ) then
pqinsert -p "plot ar $ftime surfaceDIV surfaceDIV_${hhmm}.gif gif" surfaceDIV.gif >& /dev/null
rm surfaceDIV.gif
endif

if (-e surfaceFRNT.gif ) then
pqinsert -p "plot ar $ftime surfaceFRNT surfaceFRNT_${hhmm}.gif gif" surfaceFRNT.gif >& /dev/null
rm surfaceFRNT.gif
endif

