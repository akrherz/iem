# COOP related scripts that are run at :10 after between 6-10 AM
# set -x

cd outgoing
python wxc_azos_gdd.py
php wxc_coop.php

cd ../coop
csh PREC.csh
python plot_precip_12z.py
python year_precip.py
python month_precip.py
python day_precip.py
