#!/bin/csh
# 		HEAT_plot.csh
# Daryl Herzmann 10 November 2000
# 19 Jun 2001:	Adapted for mesonet box
# 20 Jun 2001:	Check to see if map can be made differently
# 30 Jul 2001:	Might as well be archiving this plot
#  1 Aug 2002:	Why am I not archiving this plot?
# 11 Nov 2002:	Don't archive this plot...
# 17 Feb 2003:	Use GIF driver
# 16 Oct 2003	Dont archive
########################################################

source /mesonet/nawips/Gemenviron
setenv DISPLAY localhost:1


setenv GEMCOLTBL coltbl.xwp

set yy=`date -u +%y`
set mm=`date -u +%m`
set dd=`date -u +%d`
set date=${yy}${mm}${dd}
set hh=`date -u +%H`
set ftime="`date -u +'%Y%m%d%H'`00"

rm heat.gif >& /dev/null

set DEVICE="GIF|heat.gif"

$GEMEXE/sfmap_gf << EOF > /tmp/HEAT_plot_sfmap.out
	AREA	= 40.25;-97;43.75;-90
	GAREA	= 40.25;-97;43.75;-90
 	SATFIL   =  
	RADFIL   =  
	SFPARM   =  HEAT
	COLORS   =  2
 	DATTIM   =  ${date}/${hh}
 	SFFILE   =  /mesonet/data/gempak/meso/${date}_meso.gem
	MAP	=  25//2 + 25
 	LATLON	=  0
        TITLE	=  32/-1/~ Heat Index
        CLEAR	=  no
        PANEL	=  0
        DEVICE	= ${DEVICE}
        PROJ	=  LCC
        FILTER	=  .3
        TEXT	=  1/1//hw
        LUTFIL	=
        STNPLT	=
	\$mapfil = HIPOWO.CIA + HICNUS.NWS
	list
	run

EOF


if (-e heat.gif) then
	#~/bin/logo.csh ~/plots/heat.gif
	#cp heat.gif ~/current
	#cp heat.gif ~/archive/heat_${hh}00.gif
	#mv heat.gif WEB/
  /home/ldm/bin/pqinsert -p "plot ac $ftime heat.gif heat_${hh}00.gif gif" heat.gif >& /dev/null
endif
