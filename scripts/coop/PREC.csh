#!/bin/csh
set Date=`date +'%Y%m%d'`
set ftime="`date +'%Y%m%d'`0000"

python plot_coop.py
python extract_coop_obs.py
python today_precip.py

cp /mesonet/www/apps/iemwebsite/data/gis/meta/4326.prj coop_${Date}.prj
cp data.desc coop_${Date}.txt
zip -q coop_${Date}.zip coop_${Date}.txt coop_${Date}.prj coop_${Date}.shp coop_${Date}.shx coop_${Date}.dbf 

/home/ldm/bin/pqinsert -p "zip ac $ftime gis/shape/4326/iem/coopobs.zip GIS/coop_${Date}.zip zip" coop_${Date}.zip
rm -f coop_${Date}.* 
