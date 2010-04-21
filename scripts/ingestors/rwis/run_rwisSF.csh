#!/bin/csh
#	run_rwisSF.csh
# Script that inserts surface data into a gempak file
# Daryl Herzmann 04 Oct 2001
# 16 Oct 2001	Added dump back out for post processing
# 06 Nov 2001	Major reworking of now SF data is used
# 07 Nov 2001	Added then removed dump for post-process
# 26 Nov 2001	Be a bit more specific when extracting data for FN
# 30 Dec 2001:	y2k1
#  1 Aug 2002:	Use SFfe.py, much nicer!
###################################################


source /mesonet/nawips/Gemenviron

set date=`date -u +%y%m%d`
set MM=`date -u +%M`
set hh=`date -u +%H`


if (! -e /mesonet/data/gempak/pavement/${date}_rsf.gem) then
	cp /mesonet/data/gempak/pavement/template.gem /mesonet/data/gempak/pavement/${date}_rsf.gem
endif

sfedit << EOF > surface_load.out
 SFFILE	= /mesonet/data/gempak/pavement/${date}_rsf.gem
 SFEFIL	= /tmp/rwis_surface.list
 list
 run

 exit
EOF
