# Process the apache log files generated from the IEM cluster

export yyyymm="`date --date '1 day ago' +'%Y%m'`"
export dd="`date --date '1 day ago' +'%d'`"

# Go to temp directory, that hopefully has enough space!
cd /mesonet/www/logs/tmp

MACHINES="iemvs100 iemvs101 iemvs102 iemvs103 iemvs104 iemvs105 iemvs106 iemvs107 iemvs108 iemvs109"
BASE="/mesonet/www/logs"
CONFBASE="/mesonet/www/apps/iemwebsite/scripts/webalizer"

# Step 1, move the log files out of the way and restart apache gracefully
# 130201 Graceful restarts not working! 
# https://issues.apache.org/bugzilla/show_bug.cgi?id=48949
# 130325 graceful should not fail now
# http://trac.osgeo.org/gdal/ticket/4175
for MACH in $MACHINES
do
	ssh root@$MACH "mv -f $BASE/access_log $BASE/access_log.$MACH && \
    mv -f $BASE/access_log-wepp $BASE/access_log-wepp.$MACH && \
    mv -f $BASE/access_log-idep $BASE/access_log-idep.$MACH && \
    mv -f $BASE/access_log-weather.im $BASE/access_log-weather.im.$MACH && \
    mv -f $BASE/access_log-datateam $BASE/access_log-datateam.$MACH && \
    mv -f $BASE/access_log-sustainablecorn $BASE/access_log-sustainablecorn.$MACH && \
   	mv -f $BASE/access_log-cocorahs $BASE/access_log-cocorahs.$MACH && \
    systemctl reload httpd.service"
done

# Step 2, bring all these log files back to roost
for MACH in $MACHINES
do
	# limit file transfer to 750Mbit/s
	scp -l 750000 -q root@${MACH}:${BASE}/*${MACH} .
	ssh root@$MACH "rm -f $BASE/access_log.$MACH"
done

# Step 3, merge the log files back into one
csh -c "(/usr/local/bin/mergelog access_log.iemvs* > access.log) >& /dev/null"
wc -l access_log.iemvs* 
rm -f access_log.iemvs*

csh -c "(/usr/local/bin/mergelog access_log-wepp.iemvs* > wepp_access.log) >& /dev/null"
wc -l access_log-wepp.iemvs* 
rm -f access_log-wepp.iemvs*

csh -c "(/usr/local/bin/mergelog access_log-idep.iemvs* > idep_access.log) >& /dev/null"
wc -l access_log-idep.iemvs* 
rm -f access_log-idep.iemvs*

csh -c "(/usr/local/bin/mergelog access_log-cocorahs.iemvs* > cocorahs_access.log) >& /dev/null"
wc -l access_log-cocorahs.iemvs*
rm -f access_log-cocorahs.iemvs*

csh -c "(/usr/local/bin/mergelog access_log-sustainablecorn.iemvs* > sustainablecorn_access.log) >& /dev/null"
wc -l access_log-sustainablecorn.iemvs* 
rm -f access_log-sustainablecorn.iemvs*

csh -c "(/usr/local/bin/mergelog access_log-datateam.iemvs* > datateam_access.log) >& /dev/null"
wc -l access_log-datateam.iemvs* 
rm -f access_log-datateam.iemvs*

csh -c "(/usr/local/bin/mergelog access_log-weather.im.iemvs* > weatherim_access.log) >& /dev/null"
wc -l access_log-weather.im.iemvs* 
rm -f access_log-weather.im.iemvs*

# Step 4, run webalizer against these log files
/home/mesonet/bin/webalizer -c ${CONFBASE}/mesonet.conf -T access.log
rsync -av /mesonet/www/logs/usage/mesonet.agron.iastate.edu /mesonet/share/usage/
/home/mesonet/bin/webalizer -c ${CONFBASE}/cocorahs.conf cocorahs_access.log
/home/mesonet/bin/webalizer -c ${CONFBASE}/sustainablecorn.conf sustainablecorn_access.log
/home/mesonet/bin/webalizer -c ${CONFBASE}/wepp.conf wepp_access.log
/home/mesonet/bin/webalizer -c ${CONFBASE}/idep.conf idep_access.log
/home/mesonet/bin/webalizer -c ${CONFBASE}/weatherim.conf weatherim_access.log
/home/mesonet/bin/webalizer -c ${CONFBASE}/datateam.conf datateam_access.log

grep " /agclimate" access.log > agclimate.log
/home/mesonet/bin/webalizer -c ${CONFBASE}/agclimate.conf -T agclimate.log
rm -f agclimate.log

# Step 5, archive these files
mv access.log access_log-$dd
gzip access_log-$dd
mv access_log-$dd.gz iem_access_log-${yyyymm}${dd}.gz

mv wepp_access.log wepp_access_log-$dd
gzip wepp_access_log-$dd
mv wepp_access_log-$dd.gz wepp_access_log-${yyyymm}${dd}.gz

mv idep_access.log idep_access_log-$dd
gzip idep_access_log-$dd
mv idep_access_log-$dd.gz idep_access_log-${yyyymm}${dd}.gz

mv cocorahs_access.log cocorahs_access_log-$dd
gzip cocorahs_access_log-$dd
mv cocorahs_access_log-$dd.gz cocorahs_access_log-${yyyymm}${dd}.gz

mv sustainablecorn_access.log sustainablecorn_access_log-$dd
gzip sustainablecorn_access_log-$dd
mv sustainablecorn_access_log-$dd.gz sustainablecorn_access_log-${yyyymm}${dd}.gz

mv weatherim_access.log weatherim_access_log-$dd
gzip weatherim_access_log-$dd
mv weatherim_access_log-$dd.gz wxim_access_log-${yyyymm}${dd}.gz

mv datateam_access.log datateam_access_log-$dd
gzip datateam_access_log-$dd
mv datateam_access_log-$dd.gz datateam_access_log-${yyyymm}${dd}.gz

lftp -u akrherz@iastate.edu ftps://ftp.box.com << EOM
cd IEMWWWLogs
mkdir $yyyymm
cd $yyyymm
put iem_access_log-${yyyymm}${dd}.gz
put wepp_access_log-${yyyymm}${dd}.gz
put idep_access_log-${yyyymm}${dd}.gz
put cocorahs_access_log-${yyyymm}${dd}.gz
put sustainablecorn_access_log-${yyyymm}${dd}.gz
put wxim_access_log-${yyyymm}${dd}.gz
put datateam_access_log-${yyyymm}${dd}.gz
bye
EOM

mv *_access_log-${yyyymm}${dd}.gz ../save/
tmpwatch 10d ../save
# Done!