# Process the apache log files generated from the IEM cluster

export yyyymm="`date --date '1 day ago' +'%Y%m'`"
export dd="`date --date '1 day ago' +'%d'`"


MACHINES="iemvs100 iemvs101 iemvs102 iemvs103 iemvs104 iemvs105 iemvs106 iemvs107 iemvs108"
BASE="/mesonet/www/logs"

# Step 1, move the log files out of the way and restart apache gracefully
# 130201 Graceful restarts not working! 
# https://issues.apache.org/bugzilla/show_bug.cgi?id=48949
for MACH in $MACHINES
do
	ssh root@$MACH "mv -f $BASE/access_log $BASE/access_log.$MACH && \
    mv -f $BASE/access_log-wepp $BASE/access_log-wepp.$MACH && \
    mv -f $BASE/access_log-sustainablecorn $BASE/access_log-sustainablecorn.$MACH && \
   	mv -f $BASE/access_log-cocorahs $BASE/access_log-cocorahs.$MACH && \
    service httpd restart"
done

# Step 2, bring all these log files back to roost
for MACH in $MACHINES
do
	scp -q root@${MACH}:${BASE}/*${MACH} .
	ssh root@$MACH "rm -f $BASE/access_log.$MACH"
done

# Step 3, merge the log files back into one
csh -c "(/usr/local/bin/mergelog access_log.iemvs* > access.log) >& /dev/null"
wc -l access_log.iemvs* access.log
rm -f access_log.iemvs*

csh -c "(/usr/local/bin/mergelog access_log-wepp.iemvs* > wepp_access.log) >& /dev/null"
wc -l access_log-wepp.iemvs* wepp_access.log 
rm -f access_log-wepp.iemvs*

csh -c "(/usr/local/bin/mergelog access_log-cocorahs.iemvs* > cocorahs_access.log) >& /dev/null"
wc -l access_log-cocorahs.iemvs* cocorahs_access.log
rm -f access_log-cocorahs.iemvs*

csh -c "(/usr/local/bin/mergelog access_log-sustainablecorn.iemvs* > sustainablecorn_access.log) >& /dev/null"
wc -l access_log-sustainablecorn.iemvs* sustainablecorn_access.log
rm -f access_log-sustainablecorn.iemvs*

# Step 4, run webalizer against these log files
/home/mesonet/bin/webalizer -c mesonet.conf -T access.log
/usr/bin/webalizer -c cocorahs.conf cocorahs_access.log
/usr/bin/webalizer -c sustainablecorn.conf sustainablecorn_access.log
/usr/bin/webalizer -c wepp.conf wepp_access.log

grep " /agclimate" access.log > agclimate.log
/home/mesonet/bin/webalizer -c agclimate.conf -T agclimate.log
rm -f agclimate.log

# Step 5, archive these files
mkdir -p /mesonet/www/logs/old_logs/$yyyymm
mv access.log access_log-$dd
gzip access_log-$dd
mv access_log-$dd.gz /mesonet/www/logs/old_logs/$yyyymm/

mv wepp_access.log wepp_access_log-$dd
gzip wepp_access_log-$dd
mv wepp_access_log-$dd.gz /mesonet/www/logs/old_logs/$yyyymm/

mv cocorahs_access.log cocorahs_access_log-$dd
gzip cocorahs_access_log-$dd
mv cocorahs_access_log-$dd.gz /mesonet/www/logs/old_logs/$yyyymm/

mv sustainablecorn_access.log sustainablecorn_access_log-$dd
gzip sustainablecorn_access_log-$dd
mv sustainablecorn_access_log-$dd.gz /mesonet/www/logs/old_logs/$yyyymm/

# Done!