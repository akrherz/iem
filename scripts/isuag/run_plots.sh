dstr=`date --date '1 day ago' +'%Y-%m-%d'`
WEBHOST="iem.local"
PQI="/home/ldm/bin/pqinsert"

fp="air-temp-out"
wget -q http://${WEBHOST}/GIS/apps/agclimate/plot.php\?direct=yes\&pvar=c11,c12\&date=${dstr} -O air-temp-out.png
convert air-temp-out.png air-temp-out.jpg
convert air-temp-out.jpg air-temp-out.gif
gifsicle -b -O2 air-temp-out.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.gif bogus gif" ${fp}.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.jpg bogus jpg" ${fp}.jpg
rm -f ${fp}.jpg ${fp}.png ${fp}.gif


fp="4in-temp-out"
wget -q http://${WEBHOST}/GIS/apps/agclimate/plot.php\?direct=yes\&pvar=c30\&date=${dstr} -O 4in-temp-out.png
convert 4in-temp-out.png 4in-temp-out.jpg
convert 4in-temp-out.jpg 4in-temp-out.gif
gifsicle -b -O2 4in-temp-out.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.gif bogus gif" ${fp}.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.jpg bogus jpg" ${fp}.jpg
rm -f ${fp}.jpg ${fp}.png ${fp}.gif

fp="soil-hilo-out"
wget -q http://${WEBHOST}/GIS/apps/agclimate/plot.php\?direct=yes\&pvar=c300h,c300l\&date=${dstr} -O soil-hilo-out.png
convert soil-hilo-out.png soil-hilo-out.jpg
convert soil-hilo-out.jpg soil-hilo-out.gif
gifsicle -b -O2 soil-hilo-out.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.gif bogus gif" ${fp}.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.jpg bogus jpg" ${fp}.jpg
rm -f ${fp}.jpg ${fp}.png ${fp}.gif


fp="rad-out"
wget -q http://${WEBHOST}/GIS/apps/agclimate/plot.php\?direct=yes\&pvar=c80\&date=${dstr} -O rad-out.png
convert rad-out.png rad-out.jpg
convert rad-out.jpg rad-out.gif
gifsicle -b -O2 rad-out.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.gif bogus gif" ${fp}.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.jpg bogus jpg" ${fp}.jpg
rm -f ${fp}.jpg ${fp}.png ${fp}.gif

fp="et-out"
wget -q http://${WEBHOST}/GIS/apps/agclimate/plot.php\?direct=yes\&pvar=c70\&date=${dstr} -O et-out.png
convert et-out.png et-out.jpg
convert et-out.jpg et-out.gif
gifsicle -b -O2 et-out.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.gif bogus gif" ${fp}.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.jpg bogus jpg" ${fp}.jpg
rm -f ${fp}.jpg ${fp}.png ${fp}.gif

fp="prec-out"
wget -q http://${WEBHOST}/GIS/apps/agclimate/plot.php\?direct=yes\&pvar=c90\&date=${dstr} -O prec-out.png
convert prec-out.png prec-out.jpg
convert prec-out.jpg prec-out.gif
gifsicle -b -O2 prec-out.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.gif bogus gif" ${fp}.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.jpg bogus jpg" ${fp}.jpg
rm -f ${fp}.jpg ${fp}.png ${fp}.gif

fp="pk-wind-out"
wget -q http://${WEBHOST}/GIS/apps/agclimate/plot.php\?direct=yes\&pvar=c529\&date=${dstr} -O ${fp}.png
convert ${fp}.png ${fp}.jpg
convert ${fp}.jpg ${fp}.gif
gifsicle -b -O2 ${fp}.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.gif bogus gif" ${fp}.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.jpg bogus jpg" ${fp}.jpg
rm -f ${fp}.jpg ${fp}.png ${fp}.gif

fp="avewind-out"
wget -q http://${WEBHOST}/GIS/apps/agclimate/plot.php\?direct=yes\&pvar=c40\&date=${dstr} -O ${fp}.png
convert ${fp}.png ${fp}.jpg
convert ${fp}.jpg ${fp}.gif
gifsicle -b -O2 ${fp}.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.gif bogus gif" ${fp}.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.jpg bogus jpg" ${fp}.jpg
rm -f ${fp}.jpg ${fp}.png ${fp}.gif

fp="dwpts"
wget -q http://${WEBHOST}/GIS/apps/agclimate/plot.php\?network=ISUAG\&direct=yes\&pvar=dwpf\&date=${dstr} -O ${fp}.png
convert ${fp}.png ${fp}.jpg
convert ${fp}.jpg ${fp}.gif
gifsicle -b -O2 ${fp}.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.gif bogus gif" ${fp}.gif
$PQI -p "plot c 000000000000 agclimate/${fp}.jpg bogus jpg" ${fp}.jpg
rm -f ${fp}.jpg ${fp}.png ${fp}.gif

fp="chill-sum"
wget -q http://${WEBHOST}/GIS/apps/agclimate/chill.php\?direct=yes -O ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
rm -f ${fp}.png

fp="mon-prec-out"
wget -q http://${WEBHOST}/GIS/apps/agclimate/month.php\?dvar=rain_mm_tot\&direct=yes -O ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
rm -f ${fp}.png

fp="mon-et-out"
wget -q http://${WEBHOST}/GIS/apps/agclimate/month.php\?dvar=dailyet\&direct=yes -O ${fp}.png
$PQI -p "plot c 000000000000 agclimate/${fp}.png bogus png" ${fp}.png
rm -f ${fp}.png

python fancy_4inch.py 1
python fancy_4inch.py 2
python fancy_4inch.py 3
