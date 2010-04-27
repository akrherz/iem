#!/bin/csh
# 		WCHT_plot.csh
# Daryl Herzmann 08 Oct 2001
# 12 Nov 2001:	Ahhh, renamed WCHT_plot.csh
#  1 Aug 2002:	Why is this getting archived?
# 11 Nov 2002:	Why isn't it getting archived?
# 17 Feb 2003:	Update to the GIF driver
# 16 Oct 2003	Archive!
########################################################

source /mesonet/nawips/Gemenviron

setenv GEMCOLTBL coltbl.xwp

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`
set ftime="`date -u +'%Y%m%d%H'`00"

rm wceq.gif >& /dev/null

set DEVICE="GIF|wcht.gif|650;500"

setenv DISPLAY localhost:1

$GEMEXE/sfmap << EOF > TMP/WCHT_plot_sfmap.out
	AREA	= 40.25;-97;43.75;-90
	GAREA	= 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  WCHT
	COLORS   =  4
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  /mesonet/data/gempak/meso/${date}_meso.gem
	MAP	=  25//2 + 25
 	LATLON	=  0
        TITLE	=  32/-1/~ NWS Wind Chill Index
        CLEAR	=  no
        PANEL	=  0
        DEVICE	= ${DEVICE}
        PROJ	=  LCC
        FILTER	=  .8
        TEXT	=  1/1//hw
        LUTFIL	=
        STNPLT	=
	\$mapfil = HIPOWO.CIA + HICNUS.NWS
	list
	run

EOF

gpend

if (-e wcht.gif) then
	#~/bin/slogo.csh ~/plots/wcht.gif
	#cp wcht.gif ~/current
	#cp wcht.gif ~/archive/wceq_${hh}00.gif
	#mv wcht.gif WEB/
  /home/ldm/bin/pqinsert -p "plot ac $ftime wcht.gif wceq_${hh}00.gif gif" wcht.gif >& /dev/null
endif
