dstr=$(date --date '1 day ago' +'%Y-%m-%d')
WEBHOST="iem.local"
PQI="pqinsert"
URI="http://${WEBHOST}/plotting/auto/plot/199"

runner () {
  fn=$1
  wget -q ${URI}/opt:${2}::date:${dstr}.png -O ${fn}.png
  magick ${fn}.png ${fn}.jpg
  magick ${fn}.jpg ${fn}.gif
  gifsicle -b -O2 ${fn}.gif
  $PQI -p "plot c 000000000000 agclimate/${fn}.png bogus png" ${fn}.png
  $PQI -p "plot c 000000000000 agclimate/${fn}.gif bogus gif" ${fn}.gif
  $PQI -p "plot c 000000000000 agclimate/${fn}.jpg bogus jpg" ${fn}.jpg
  rm -f ${fn}.jpg ${fn}.png ${fn}.gif
}

#___________________________________________________________
runner "soil-hilo-out" 1
runner "air-temp-out" 2
runner "4in-temp-out" 3
runner "rad-out" 4
runner "et-out" 5
runner "prec-out" 6
runner "pk-wind-out" 7
runner "avewind-out" 8

fp="chill-sum"
wget -q http://${WEBHOST}/GIS/apps/agclimate/chill.php -O ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
rm -f ${fp}.png

fp="mon-prec-out"
wget -q http://${WEBHOST}/GIS/apps/agclimate/month.php\?dvar=rain_in_tot -O ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
rm -f ${fp}.png

fp="mon-et-out"
wget -q http://${WEBHOST}/GIS/apps/agclimate/month.php\?dvar=dailyet -O ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
rm -f ${fp}.png

python fancy_4inch.py --days=1
python fancy_4inch.py --days=2
python fancy_4inch.py --days=3
