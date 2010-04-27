#!/bin/csh
# Plot up RUC2 information.  Should be handy for Iowa related information
# Daryl Herzmann 30 May 2002
# 17 Feb 2003:	Use GIF driver

source /mesonet/nawips/Gemenviron
setenv DISPLAY localhost:1

#___________________________________________
# 5 cm Soil Moisture                      /
#_________________________________________/

set OUTGIF="ruc2_soim_5.gif"
rm -f ${OUTGIF}* >& /dev/null

gdplot2_gf << EOF > /tmp/${OUTGIF}.out
 restore restore/ruc2_soim
 TITLE  = 5/-1/~ RUC2 5cm Volumetric Soil Moisture
 GLEVEL = 5
 GVCORD = DPTH
 GDPFUN = SM9S(SOIM)
 DEVICE	= GIF|${OUTGIF}|650;500
 list
 run

 exit
EOF

if (-e ${OUTGIF} ) then
  /home/ldm/bin/pqinsert -p "plot c 000000000000 model/$OUTGIF bogus gif" ${OUTGIF} >& /dev/null
#        mv ${OUTGIF} /mesonet/www/html/wx/data/models/
endif

#___________________________________________
# 20 cm Soil Moisture                      /
#_________________________________________/

set OUTGIF="ruc2_soim_20.gif"
rm -f ${OUTGIF}* >& /dev/null

gdplot2_gf << EOF > /tmp/${OUTGIF}.out
 restore restore/ruc2_soim
 TITLE  = 5/-1/~ RUC2 20cm Volumetric Soil Moisture
 GLEVEL = 20
 GVCORD = DPTH
 GDPFUN = SM9S(SOIM)
 DEVICE	= GIF|${OUTGIF}|650;500
 list
 run

 exit
EOF

if (-e ${OUTGIF} ) then
  /home/ldm/bin/pqinsert -p "plot c 000000000000 model/$OUTGIF bogus gif" ${OUTGIF} >& /dev/null
#        mv ${OUTGIF} /mesonet/www/html/wx/data/models/
endif

#___________________________________________
# CAPE                                     /
#_________________________________________/

set OUTGIF="ruc2_cape_f00.gif"
rm -f ${OUTGIF}* >& /dev/null

gdplot2_gf << EOF > /tmp/${OUTGIF}.out
 restore restore/ruc2_cape
 DEVICE	= GIF|${OUTGIF}|650;500
 list
 run

 exit
EOF

if (-e ${OUTGIF} ) then
  /home/ldm/bin/pqinsert -p "plot c 000000000000 model/$OUTGIF bogus gif" ${OUTGIF} >& /dev/null
#        mv ${OUTGIF} /mesonet/www/html/wx/data/models/
endif

#___________________________________________
# LIFT                                     /
#_________________________________________/

set OUTGIF="ruc2_lift_f00.gif"
rm -f ${OUTGIF}* >& /dev/null

gdplot2_gf << EOF > /tmp/${OUTGIF}.out
 restore restore/ruc2_lift
 DEVICE	= GIF|${OUTGIF}|650;500
 list
 run

 exit
EOF

if (-e ${OUTGIF} ) then
  /home/ldm/bin/pqinsert -p "plot c 000000000000 model/$OUTGIF bogus gif" ${OUTGIF} >& /dev/null
 #       mv ${OUTGIF} /mesonet/www/html/wx/data/models/
endif

#___________________________________________
# 900w                                     /
#_________________________________________/

set OUTGIF="ruc2_900w_f00.gif"
rm -f ${OUTGIF}* >& /dev/null

gdplot2_gf << EOF > /tmp/${OUTGIF}.out
 restore restore/ruc2_900w
 DEVICE	= GIF|${OUTGIF}|650;500
 list
 run

 exit
EOF

if (-e ${OUTGIF} ) then
  /home/ldm/bin/pqinsert -p "plot c 000000000000 model/$OUTGIF bogus gif" ${OUTGIF} >& /dev/null
 #       mv ${OUTGIF} /mesonet/www/html/wx/data/models/
endif

