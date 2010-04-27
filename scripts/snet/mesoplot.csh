#!/bin/csh
# Script to plot station model of schoolnet obs
# Daryl Herzmann 11 Feb 2002
# 12 Feb 2002:	Added solar Rad
# 19 Feb 2002:	Added precip
# 05 Mar 2002:	Added Altimeter
# 09 Apr 2002:	Move DSM up a bit to get AMW, BNW
# 10 Apr 2002:	Also plot Monthly precip totals
# 18 Apr 2002:	Also plot wind gusts
# 19 Apr 2002:	We need to be further North to get Mallard
# 07 May 2002:	Also do statistics for the current page
#		Clean up mesonet plot
# 20 Jul 2002:	Change the name of the Surface Altimeter Plot
#  3 Oct 2002:	Dave doesn't want the use of the work 'Reporting'
# 21 Nov 2002:	Parkin would like a plot in inches too
# 17 Feb 2003:	Use GIF driver
# 19 Aug 2003	Don't use GIF driver
########################################################

source /mesonet/nawips/Gemenviron
setenv DISPLAY localhost:1

set yymmdd=`date -u +%y%m%d`
set hh=`date -u +%H`
set mm=`date -u +%M`
set ts=`date +'%Y%m%d%H%M'`

if (${mm} > 40 ) then
        set mm = "40"
else if (${mm} > 20) then
        set mm = "20"
else
        set mm = "00"
endif

set title="`date +'%h-%d %l:'`${mm} `date +'%p %Z'`"
set title2="`date +'%h-%d'`"


set AREA="40.50;-95.2;43.10;-92.0"
set DSMAREA="41.5;-94.3;42.1;-93.2"
set GFFILE="mesonet.gif"
set DSMFILE="DSM_mesonet.gif"
set RADFILE="solarRad.gif"
set PRECFILE="precToday.gif"
set MONPREC="precMonth.gif"
set GUSTFILE="snetGust.gif"


rm -f *.gif >& /dev/null

sfmap_gf << EOF > /tmp/mesoplot_sfmap.out
 AREA     = ${AREA}
 GAREA    = ${AREA}
 SATFIL   =  
 RADFIL   =  
 SFPARM   = ;tmpf<120;;altm;;dwpf<120;stid;;brbk:.8:.8:231
 DATTIM   = /${hh}${mm}
 SFFILE   = /mesonet/data/gempak/snet/${yymmdd}_snet.gem
 COLORS   = 2;0;4;0;32
 LATLON   = 0
 TITLE    = 32/-1/${title} SchoolNet Stations
 CLEAR    = YES
 PANEL    = 0
 DEVICE   = GIF|${GFFILE}|650;600
 PROJ     = LCC
 FILTER   = NO
 TEXT     = 0.8
 LUTFIL   =  
 STNPLT   =  
 CLRBAR   =  
 MAP     = 25 + 25//2
 \$MAPFIL = HICNUS.NWS + hipowo.cia
 list
 run

 DEVICE	= GIF|${DSMFILE}|650;500
 AREA	= ${DSMAREA}
 GAREA	= ${DSMAREA}
 TITLE    = 32/-1/${title} Near Des Moines SchoolNet 
 \$MAPFIL = HICNUS.NWS + hipowo.cia + HIISUS.NWS
 MAP     = 25 + 25//2 + 3//1
 list
 run

 AREA	= ${AREA}
 GAREA	= ${AREA}
 DEVICE	= GIF|${RADFILE}|650;600
 TITLE    = 32/-1/${title} SchoolNet Solar Rad [W m**-2]
 SFPARM	= SRAD 
 TEXT	= 1/2///s/c
 list
 run

 AREA   = ${AREA}
 GAREA  = ${AREA}
 COLORS	= 4
 DEVICE = GIF|${PRECFILE}|650;600
 TITLE    = 32/-1/${title} SchoolNet Today Prec [.01 in]
 SFPARM = P24I*100
 TEXT	= 1/2///s/c
 list
 run

 AREA   = ${AREA}
 GAREA  = ${AREA}
 COLORS = 4
 DEVICE = GIF|${MONPREC}|650;600
 TITLE    = 32/-1/SchoolNet Monthly Total ${title2}[.01 in]
 SFPARM = P31I*100
 TEXT   = 1/2///s/c
 list
 run

 SFPARM = GUSS
 TITLE	= 32/-1/SchoolNet Wind Gusts ${title2} [knts]
 DEVICE	= GIF|${GUSTFILE}|650;600
 list
 run

 exit
EOF

sfcntr_gf << EOF > /tmp/sfcntr.out
 AREA     = ${AREA}
 GAREA    = ${AREA}
 SATFIL   =  
 RADFIL   =  
 SFPARM   = ALTM
 DATTIM   = /${hh}${mm}
 SFFILE   = /mesonet/data/gempak/snet/${yymmdd}_snet.gem
 COLORS   = 32;32
 MAP     = 25 + 25//2
 \$MAPFIL = HICNUS.NWS + hipowo.cia
 LATLON   = 0
 TITLE    = 32/-1/${title} Barometer [mb]
 CLEAR    = YES
 PANEL    = 0
 DEVICE   = GIF|snet_altm.gif|650;500
 PROJ     = LCC
 FILTER   = 0
 TEXT     = 1/22/hw
 LUTFIL   =  
 STNPLT   =  
 CLRBAR   =  
 CNTRPRM  = TMPF
 GAMMA    = 0.3
 WEIGHT   =  
 LINE     = 4
 CONTUR   = 0
 NPASS    = 2
 CINT     = 2
 list
 run
 
 TITLE    = 32/-1/${title} Barometer [inch * 100]
 SFPARM  = ALTI*100
 CNTRPRM  = ALTM*100
 DEVICE   = GIF|snet_alti.gif|650;500
 list
 run

 exit
EOF

#gpend


if (-e ${GFFILE}) then
  /home/ldm/bin/pqinsert -p "plot c 000000000000 snet/${GFFILE} ${GFFILE} gif" ${GFFILE} >& /dev/null
  /home/ldm/bin/pqinsert -p "plot c 000000000000 snet/${RADFILE} ${RADFILE} gif" ${RADFILE} >& /dev/null
  /home/ldm/bin/pqinsert -p "plot c 000000000000 snet/${DSMFILE} ${DSMFILE} gif" ${DSMFILE} >& /dev/null
  /home/ldm/bin/pqinsert -p "plot ac $ts snet/${PRECFILE} snetPrec.gif gif" ${PRECFILE} >& /dev/null
  /home/ldm/bin/pqinsert -p "plot c 000000000000 snet/${MONPREC} ${MONPREC} gif" ${MONPREC} >& /dev/null
  /home/ldm/bin/pqinsert -p "plot c 000000000000 snet/${GUSTFILE} ${GUSTFILE} gif" ${GUSTFILE} >& /dev/null
  /home/ldm/bin/pqinsert -p "plot c 000000000000 snet/snet_altm.gif snet_altm.gif gif" snet_altm.gif >& /dev/null
  /home/ldm/bin/pqinsert -p "plot c 000000000000 snet/snet_alti.gif snet_alti.gif gif" snet_alti.gif >& /dev/null
  #mv ${GFFILE} ~/current/snet/
  #mv ${RADFILE} ~/current/snet/
  #mv ${DSMFILE} ~/current/snet/
  #mv ${PRECFILE} ~/current/snet/
  #mv ${MONPREC} ~/current/snet/
  #mv ${GUSTFILE} ~/current/snet/
  #mv snet_altm.gif ~/current/snet/
  #mv snet_alti.gif ~/current/snet/
endif

#####
# Lets count how many we have reporting
#sfchck << EOF > ../TMP/sfchck.out
#        SFFILE   = /mesonet/data/gempak/snet/${yymmdd}_snet.gem
#        AREA     = @IA
#        DATTIM   = /${hh}${mm}
#        OUTPUT   = f/snet.good
#        IDNTYP   = STID
#        STNTYP   = R
#        list
#        run
#
#        exit
#EOF
#
#@ GOOD_SNET=`wc -l snet.good | cut -d ' ' -f 1` - 3
#set TOTAL_SNET=`cat /mesonet/TABLES/snet.stns | grep -v "^\#" | wc -l | cut -c 6-7`
#rm -f snet.good
#
#echo "[/${hh}${mm}] ${GOOD_SNET} / ${TOTAL_SNET} " > ~/current/snet.stat
