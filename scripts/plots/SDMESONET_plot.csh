#!/bin/csh

source /mesonet/nawips/Gemenviron

setenv GEMCOLTBL coltbl.xwp

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`
set yyyymmddhh_1h="`date -u --date '1 hour ago' +'%Y%m%d%H'`"
set nicetime=`date +"%b %d %I %p"`

rm mesonet.gif* >& /dev/null

set DEVICE="GIF|mesonet.gif|900;700"
set AREA="42.6;-104.5;46;-96"

# Now we plot
sfmap << EOF > /tmp/SDMESONET_sfmap.out
	AREA    = ${AREA}
	GAREA    = ${AREA}
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  skyc:.6;tmpf<120;wsym:1.2:2;alti;;dwpf<120;;;;brbk:1:1:231
	COLORS   =  32;2;32;0;4;32
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  /mesonet/data/gempak/meso/${date}_meso.gem
 	LATLON   =  0
        TITLE    =  32/-1/GMT: ~ South Dakota Mesonet Data
        CLEAR    =  yes
        PANEL    =  0
        DEVICE   = ${DEVICE}
        PROJ     =  LCC
        FILTER   =  .3
        TEXT     =  1/1//hw
        LUTFIL   =
        STNPLT   =
	MAP	= 25 + 25//2
	\$MAPFIL = HICNUS.NWS + hipowo.cia
	list
	run

	exit
EOF

set gdfile="/mesonet/data/gempak/model/rap/${yyyymmddhh_1h}_rap252.gem"
if (! -e ${gdfile}) then
set gdfile="/mesonet/data/gempak/model/rap/${yyyymmddhh_1h}_rap130.gem"
endif

gdcntr << EOF > /tmp/SDMESONET_gdcntr.out
	GAREA    = ${AREA}
	GDATTIM  = F001
	GLEVEL   = 0
	GVCORD   = NONE
	GFUNC    = SM9S(MUL(0.01,MSLMA))
GDFILE   = $gdfile
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

if (-e mesonet.gif) then
  pqinsert -p "plot c 000000000000 SD/mesonet.gif bogus gif" mesonet.gif >& /dev/null
  rm -f mesonet.gif
endif

