#!/bin/bash

. /mesonet/nawips/Gemenviron.profile

GDFILE="grid_25_25.grd"
GDOUTF="grid_oa.grd"

rm -f "$GDFILE"
gdcfil << EOF
    GDOUTF   = $GDFILE
    PROJ     = LCC/42;-95;45
    GRDAREA  = IA
    KXKY     = 25;25
    MAXGRD   = 20
    CPYFIL   =
    ANLYSS   = 0.5
    list
    run

    exit
EOF

gpend

cp "$GDFILE" "/mesonet/data/iemplot/$GDOUTF"
