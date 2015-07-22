#!/bin/csh
# Create a mesoplot!
#set echo
set YYYY="$1"
set mm="$2"
set dd="$3"
set date=${YYYY}${mm}${dd}
set hh="$4"
set timestamp="$1$2$3/${4}00"
set ldmstamp="$1$2$3${4}00"

set DEVICE="GIF|HI_${ldmstamp}.gif|900;700"
set AREA="18.5;-162;22.5;-153"

rm -f HImesonet.gif

gddelt << EOF > gddelt.out
  GDFILE   = metar.grd
  GDATTIM  = ALL
  GLEVEL   = ALL
  GVCORD   = ALL
  GFUNC    = ALL
  run
  
  exit
EOF

oabsfc << EOF > oabsfc.out
 SFFILE = metar.gem
 GDFILE   = metar.grd
 SFPARM   = PMSL
 DATTIM   = ${timestamp}
 DTAAREA  = ${AREA}
 GUESS    =
 GUESFUN = 
 GAMMA    = .3
 SEARCH   = 10/EX
 NPASS    = 2
 QCNTL    = 3
 GDATTIM  = ${timestamp}
 GLEVEL = 0
 GVCORD = NONE
 GFUNC = MMSL
 list
 run

  exit
EOF

sfmap << EOF > sfmap.out
	AREA    = ${AREA}
	GAREA	= ${AREA}
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  skyc:.6;tmpf;wsym:1.2:2;alti;;dwpf;;;;brbk:0.8:1:231
	COLORS   =  32;2;32;0;(50;70/4;23;23/DWPF);32
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  metar.gem
 	LATLON   =  0
        TITLE    =  32/-1/~ Hawaii Data
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


gdcntr << EOF > gdcntr.out
	AREA	= ${AREA}
	GAREA    = ${AREA}
	GDATTIM  = ${date}/${hh}
	GLEVEL   = 0
	GVCORD   = NONE
	GFUNC    = SM9S(MMSL)
	GDFILE   = metar.grd
	CINT     = 1
	LINE     = 4
	MAP      = 0
	TEXT     = 1
	DEVICE   = ${DEVICE}
	SATFIL   =  
	RADFIL   =  
	PROJ     = LCC/20;-160;24
	CLEAR    = no
	PANEL	= 0
	TITLE	= 
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

