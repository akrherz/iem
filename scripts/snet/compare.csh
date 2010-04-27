#!/bin/csh
# Daryl Herzmann 11 Feb 2002
# 05 Mar 2002:	Added Altimeter
# 19 Jul 2002:	Make sure ASOS/AWOS are using correct values
#  5 Dec 2002:	Also do one in inches
# 17 Feb 2003:	Use GIF driver
#####################################

source /mesonet/nawips/Gemenviron
setenv DISPLAY localhost:1

set yymmdd=`date -u +%y%m%d`
set hh=`date -u +%H`
set mm=`date -u +%M`
set mm=`expr $mm + 0`

if (${mm} > 40 ) then
        set mm = "40"
else if (${mm} > 20) then
        set mm = "20"
else
        set mm = "00"
endif

set title="`date +'%h-%d %l:'`${mm} `date +'%p %Z'`"


setenv DISPLAY localhost:1
set AREA="40.50;-95.2;42.85;-92.0"
set GFFILE="Tcompare.gif"
set GFFILE2="Dcompare.gif"
set GFFILE3="Pcompare.gif"
set GFFILE4="P2compare.gif"


rm -f ${GFFILE} ${GFFILE2} ${GFFILE3} ${GFFILE4} >& /dev/null

sfmap << EOF > ../TMP/compare_sfmap.out
 AREA     = ${AREA}
 GAREA    = ${AREA}
 SATFIL   =  
 RADFIL   =  
 SFPARM   = tmpf
 DATTIM   = /${hh}${mm}
 SFFILE   = /mesonet/data/gempak/snet/${yymmdd}_snet.gem
 COLORS   = 2
 LATLON   = 0
 TITLE    = 2/-2/${title} Temp Compare SchoolNet [red] 
 CLEAR    = YES
 PANEL    = 0
 DEVICE   = GF|${GFFILE}|650;600
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

 TITLE    = 4/-1/  ASOS/AWOS [blue]
 CLEAR	= no
 MAP = 0
 \$mapfil = 
 SFPARM = TMPF
 COLORS = 4
 SFFILE = /mesonet/data/gempak/sao/${yymmdd}_sao.gem
 list
 run

 SFPARM	= DWPF
 TITLE	= 2/-2/${title} Dew P Compare SchoolNet [red]
 CLEAR	= YES
 DEVICE	= GF|${GFFILE2}|650;600
 COLORS	= 2
 MAP	= 25 + 25//2
 \$MAPFIL = HICNUS.NWS + hipowo.cia
 SFFILE	= /mesonet/data/gempak/snet/${yymmdd}_snet.gem
 list
 run
 
 TITLE    = 4/-1/  ASOS/AWOS [blue]
 CLEAR	= no
 MAP = 0
 \$mapfil = 
 SFPARM = DWPF
 COLORS = 4
 SFFILE = /mesonet/data/gempak/sao/${yymmdd}_sao.gem
 list
 run

 SFPARM = ALTM
 TITLE  = 2/-2/${title} Barometer SchoolNet [red]
 CLEAR  = YES
 DEVICE = GF|${GFFILE3}|650;600
 COLORS = 2
 MAP    = 25 + 25//2
 \$MAPFIL = HICNUS.NWS + hipowo.cia
 SFFILE = /mesonet/data/gempak/snet/${yymmdd}_snet.gem
 list
 run

 TITLE    = 4/-1/  ASOS/AWOS [blue]
 CLEAR  = no
 MAP = 0
 \$mapfil = 
 SFPARM = ALTM
 COLORS = 4
 SFFILE = /mesonet/data/gempak/sao/${yymmdd}_sao.gem
 list
 run

 SFPARM = ALTI*100
 TITLE  = 2/-2/${title} Barometer SchoolNet [red]
 CLEAR  = YES
 DEVICE = GF|${GFFILE4}|650;600
 COLORS = 2
 MAP    = 25 + 25//2
 \$MAPFIL = HICNUS.NWS + hipowo.cia
 SFFILE = /mesonet/data/gempak/snet/${yymmdd}_snet.gem
 list
 run

 TITLE    = 4/-1/  ASOS/AWOS [blue]
 CLEAR  = no
 MAP = 0
 \$mapfil =
 SFPARM = ALTI*100
 COLORS = 4
 SFFILE = /mesonet/data/gempak/sao/${yymmdd}_sao.gem
 list
 run

 exit
EOF

gpend

if (-e ${GFFILE}) then
  /home/ldm/bin/pqinsert -p "plot c 000000000000 snet/${GFFILE} ${GFFILE} gif" ${GFFILE} >& /dev/null
  /home/ldm/bin/pqinsert -p "plot c 000000000000 snet/${GFFILE2} ${GFFILE2} gif" ${GFFILE2} >& /dev/null
  /home/ldm/bin/pqinsert -p "plot c 000000000000 snet/${GFFILE3} ${GFFILE3} gif" ${GFFILE3} >& /dev/null
  /home/ldm/bin/pqinsert -p "plot c 000000000000 snet/${GFFILE4} ${GFFILE4} gif" ${GFFILE4} >& /dev/null
  #mv ${GFFILE} ~/current/snet/
  #mv ${GFFILE2} ~/current/snet/
  #mv ${GFFILE3} ~/current/snet/
  #mv ${GFFILE4} ~/current/snet/
endif

