# Process the apache log files generated from the IEM cluster
# iem
# iemssl
# datateam
# sustainablecorn
# weatherim
# 
# RPM requirements for this workflow
# yum -y install libdb-cxx libmaxminddb gd lftp tcsh tmpwatch

export yyyymmdd=$(date --date '1 day ago' +'%Y%m%d')
export yyyy=$(date --date '1 day ago' +'%Y')
export mm=$(date --date '1 day ago' +'%m')
export dd=$(date --date '1 day ago' +'%d')
export yyyymm=$(date --date '1 day ago' +'%Y%m')

# IMPORTANT: iemapps needs to go first for wildcard matching life choices
PREFIXES="iemapps iem datateam sustainablecorn weatherim depbackend"
MACHINES="anticyclone iemvs35-dc iemvs36-dc iemvs37-dc iemvs38-dc \
iemvs39-dc iemvs40-dc iemvs41-dc iemvs42-dc iemvs43-dc iemvs44-dc"
CONFBASE="/opt/iem/scripts/webalizer"

# Go to temp directory, that hopefully has enough space!
cd /mnt/webalizer/tmp

# Step 1, bring all these log files back to roost and delete them remotely
for MACH in $MACHINES
do
    # limit file transfer to 750Mbit/s
    scp -l 750000 -q root@${MACH}:/mesonet/www/logs/*-${yyyymmdd} .
    ssh root@$MACH "rm -f /mesonet/www/logs/*-${yyyymmdd}"
    # rename the files so that they are unique
    for PREF in $PREFIXES
    do
        for filename in $(ls ${PREF}*${yyyymmdd}); do
            mv $filename ${filename}-${MACH}
        done
    done
done

# Step 2: Merge the log files together
for PREF in $PREFIXES
do
    echo "============== $PREF ============="
    wc -l ${PREF}*
    /usr/share/awstats/tools/logresolvemerge.pl ${PREF}* > combined-${PREF}.log
    rm -f ${PREF}*
done

# Step 3, run webalizer against these log files
/home/mesonet/bin/webalizer -c ${CONFBASE}/mesonet.conf -T combined-iem.log
/home/mesonet/bin/webalizer -c ${CONFBASE}/sustainablecorn.conf combined-sustainablecorn.log
/home/mesonet/bin/webalizer -c ${CONFBASE}/weatherim.conf combined-weatherim.log
/home/mesonet/bin/webalizer -c ${CONFBASE}/datateam.conf combined-datateam.log
# Copy to shared NFS space
rsync -a /mnt/webalizer/usage/. /mesonet/share/usage/

grep " /agclimate" combined-iem.log > agclimate.log
/home/mesonet/bin/webalizer -c ${CONFBASE}/agclimate.conf -T agclimate.log
rm -f agclimate.log

# Step 4, archive these files
for PREF in $PREFIXES
do
    if [ -e combined-${PREF}.log ]; then
        mv combined-${PREF}.log ${PREF}-${yyyymmdd}.log
        gzip ${PREF}-${yyyymmdd}.log
    fi
done

# Step 5, copy files to staging for cloud storage
rsync -a --rsync-path "mkdir -p /stage/IEMWWWLogs/$yyyy/$mm && rsync " \
 ./*-${yyyymmdd}.log.gz akrherz-desktop.agron.iastate.edu:/stage/IEMWWWLogs/$yyyy/$mm/

# Step 6, mv files to local cache
mkdir -p ../save/$yyyy/$mm
mv ./*-${yyyymmdd}.log.gz ../save/$yyyy/$mm/

# Step 7, delete files from local cache
cd ../save
tmpwatch 10d .
# Done!
