#!/bin/csh

source /mesonet/nawips/Gemenviron

setenv GEMCOLTBL coltbl.xwp
setenv DISPLAY localhost:1

set yy=$1
set mm=$2
set dd=$3
set date=${yy}${mm}${dd}
set hh=$4
set timestamp=$yy$mm$dd${hh}00

set DEVICE="GF|MWmesonet.gif|900;700"

set AREA="37;-104;48.5;-86"



gddelt  << EOF > gddelt.out
        GDFILE = midwest.grd
        GDATTIM = ALL
        GDNUM   = ALL
        GFUNC   = ALL
        GLEVEL  = ALL
        GVCORD  = ALL
        list
        run

EOF


oabsfc << EOF > oabsfc.out
        DATTIM  = ${date}/${hh}00
        DTAAREA  =
        GUESS    =
        GAMMA    = .3
        SEARCH   = 20
        NPASS    = 2
        QCNTL    = 10;10;;;;;;
        SFFILE   = ${date}.gem
        GDFILE   = midwest.grd
        SFPARM   = PMSL
 GFUNC    = PMSL
 GLEVEL   = 0
 GVCORD   = NONE
        list
        run


        exit
EOF

gpend


# Now we plot
sfmap << EOF > MWmesonet_sfmap.out
	AREA    = ${AREA}
	GAREA	= ${AREA}
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  skyc:.6;tmpf;wsym:1.2:2;alti;;dwpf;;;;brbk:0.8:1:231
	COLORS   =  32;2;32;0;(50;70/4;23;23/DWPF);32
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  ${date}.gem
 	LATLON   =  0
        TITLE    =  32/-1/~ MidWest Mesonet Data
        CLEAR    =  yes
        PANEL    =  0
        DEVICE   = ${DEVICE}
        PROJ     =  LCC
        FILTER   =  .5
        TEXT     = 1
        LUTFIL   =
        STNPLT   =
  CLRBAR = 
	MAP	= 25 + 25//2
	\$MAPFIL = HICNUS.NWS + hipowo.cia
	list
	run

	exit
EOF

gdcntr << EOF > MW_MESONET_gdcntr.out
	AREA	= ${AREA}
	GAREA    = ${AREA}
	GDATTIM  = /${hh}00
	GLEVEL   = 0
	GVCORD   = NONE
	GFUNC    = SM9S(PMSL)
	GDFILE   = midwest.grd
	CINT     = 4
	LINE     = 4
	MAP      = 0
	TEXT     = 1
	DEVICE   = ${DEVICE}
	SATFIL   =  
	RADFIL   =  
	PROJ     = LCC
	CLEAR    = no
	PANEL	= 0
	TITLE	= 32/-2/~ RUC2 MMSL
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


${GEMEXE}/gpend

if (-e MWmesonet.gif) then
  /home/ldm/bin/pqinsert -p "plot a $timestamp MWmesonet.gif MWmesonet_${hh}00.gif gif" MWmesonet.gif 
  rm MWmesonet.gif
endif

