#!/bin/csh
#		IAMESONET_plot.csh
# Finally, the script that plots all of this good data

source /mesonet/nawips/Gemenviron

setenv GEMCOLTBL coltbl.xwp
setenv DISPLAY localhost:1

set yy=`date -u --date '1 minute' +%y`
set mm=`date -u --date '1 minute' +%m`
set dd=`date -u --date '1 minute' +%d`
set date=${yy}${mm}${dd}
set hh=`date -u --date '1 minute' +%H`
set timestamp="`date -u --date '1 minute' +'%Y%m%d%H00'`"
set yyyymmddhh_1h="`date -u --date '1 hour ago' +'%Y%m%d%H'`"

rm MWmesonet.gif* >& /dev/null

set DEVICE="GIF|MWmesonet.gif|900;700"

set AREA="37;-104;48.5;-86"

# Now we plot
sfmap << EOF > /tmp/MWmesonet_sfmap.out
	AREA    = ${AREA}
	GAREA	= ${AREA}
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  skyc:.6;tmpf;wsym:1.2:2;alti;;dwpf;;;;brbk:0.8:1:231
	COLORS   =  32;2;32;0;(50;70/4;23;23/DWPF);32
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  /mesonet/data/gempak/meso/${date}_meso.gem
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

set gdfile="/mesonet/data/gempak/model/rap/${yyyymmddhh_1h}_rap252.gem"
if (! -e ${gdfile}) then
set gdfile="/mesonet/data/gempak/model/rap/${yyyymmddhh_1h}_rap130.gem"
endif


gdcntr << EOF > /tmp/MW_MESONET_gdcntr.out
	AREA	= ${AREA}
	GAREA    = ${AREA}
	GDATTIM  = F001
	GLEVEL   = 0
	GVCORD   = NONE
	GFUNC    = SM9S(MMSL)
GDFILE   = $gdfile
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
	TITLE	= 32/-2/~ RAP MMSL
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
  pqinsert -p "plot ac $timestamp MWmesonet.gif MWmesonet_${hh}00.gif gif" MWmesonet.gif >& /dev/null
  rm MWmesonet.gif
endif

