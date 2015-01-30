# COOP related scripts that are run at :10 after between 6-10 AM
cd current
python coop_precip.py
python coop_snow.py

cd ../outgoing
python wxc_azos_gdd.py
php wxc_coop.php

cd ../coop
csh PREC.csh
python 12z_precip.py
