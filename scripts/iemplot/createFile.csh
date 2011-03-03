#!/bin/csh

source /mesonet/nawips/Gemenviron

# PROJ     = LCC/40;-90;44
rm grid_25_25.grd 
which gdcfil
gdcfil << EOF
 GDOUTF   = grid_25_25.grd
 PROJ     = LCC/42;-95;45
 GRDAREA  = IA
 KXKY     = 25;25
 MAXGRD   = 20
 CPYFIL   =  
 ANLYSS   = 0.5/2;2;2;2
 list
 run

 exit
EOF

gpend

cp grid_25_25.grd grid_oa.grd
