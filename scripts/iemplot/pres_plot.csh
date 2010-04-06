#!/bin/csh
#####################################################

source /mesonet/nawips/Gemenviron

setenv GEMCOLTBL coltbl.xwp
setenv DISPLAY localhost:1

set yy=`date -u --date '1 minute' +'%y'`
set mm=`date -u --date '1 minute' +'%m'`
set dd=`date -u --date '1 minute' +'%d'`
set hh=`date -u --date '1 minute' +'%H'`
set date=${yy}${mm}${dd}
set timestamp=`date -u --date '1 minute' +'%Y%m%d%H00'`

set nicetime=`date -d "20${1}-${2}-${3} ${4}:00" +"%b %d %I %p"`

rm mesonet_altm.gif* >& /dev/null

set DEVICE="GF|mesonet_altm.gif|900;700"
set AREA="40.15;-97.1;43.85;-89.9"
#set AREA="38.15;-99.1;45.85;-87.9"

# Now we plot
sfmap << EOF > /tmp/pres_plot_sfmap.out
	AREA    = ${AREA}
	GAREA    = ${AREA}
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  STID;;;altm>100;;;;;;;brbk:1:1:231
	COLORS   =  2;32
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  /mesonet/data/gempak/meso/${date}_meso.gem
 	LATLON   =  0
        TITLE    =  32/-1/GMT: ~ Iowa Mesonet Altimeter Plot
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


gdcntr << EOF > /tmp/pres_plot_gdcntr.out
	GAREA    = ${AREA}
	GDATTIM  = ${date}/${hh}
	GLEVEL   = 0
	GVCORD   = NONE
	GFUNC    = SM9S(ALTM)
	GDFILE   = grid_25_25.grd
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


if (-e mesonet_altm.gif) then
#  ~/bin/logo.csh /mesonet/scripts/iemplot/mesonet_altm.gif
  /home/ldm/bin/pqinsert -p "plot ac ${timestamp} mesonet_altm.gif mesonet_altm_${hh}00.gif gif" mesonet_altm.gif >& /dev/null
  #cp mesonet_altm.gif ~/archive/mesonet_altm_${hh}00.gif
  #mv mesonet_altm.gif ~/current
endif
