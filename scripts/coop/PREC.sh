# Tasks
# set -x
DATE=$(date +'%Y%m%d')
FTIME=$(date +'%Y%m%d')0000

python plot_coop.py
python extract_coop_obs.py
python today_precip.py

cp /opt/iem/data/gis/meta/4326.prj coop_${DATE}.prj
cp data.desc coop_${DATE}.txt
zip -q coop_${DATE}.zip coop_${DATE}.txt coop_${DATE}.prj coop_${DATE}.shp coop_${DATE}.shx coop_${DATE}.dbf 

/home/ldm/bin/pqinsert -p "zip ac $FTIME gis/shape/4326/iem/coopobs.zip GIS/coop_${DATE}.zip zip" coop_${DATE}.zip
rm -f coop_${DATE}.* 
