#!/bin/bash
# Process the apache log files generated from the IEM cluster
# iem
# iemssl
# datateam
# sustainablecorn
#
# RPM requirements for this workflow
# yum -y install libdb-cxx libmaxminddb gd lftp tmpwatch

shopt -s nullglob

yyyymmddhh="$(date -u --date '1 hour ago' +'%Y%m%d%H')"
yyyy="${yyyymmddhh:0:4}"
mm="${yyyymmddhh:4:2}"

# IMPORTANT: iemapps needs to go first for wildcard matching life choices
PREFIXES=(iemapps iem datateam sustainablecorn depbackend)
MACHINES=(anticyclone iemvs35-dc iemvs36-dc iemvs37-dc iemvs38-dc iemvs39-dc \
    iemvs40-dc iemvs41-dc iemvs42-dc iemvs43-dc iemvs44-dc)
CONFBASE="/opt/iem/scripts/webalizer"

# Go to temp directory, that hopefully has enough space!
cd /mnt/webalizer/tmp || exit 1

# Step 1, bring all these log files back to roost and delete them remotely
for MACH in "${MACHINES[@]}"
do
    scp -q "root@${MACH}:/mesonet/www/logs/*-${yyyymmddhh}" .
    for filename in *-"${yyyymmddhh}"
    do
        [[ -f "$filename" ]] || continue
        mv -- "$filename" "${filename}-${MACH}"
    done
    # shellcheck disable=SC2029
    ssh "root@${MACH}" "rm -f /mesonet/www/logs/*-${yyyymmddhh}"
done

# Step 2: Merge the log files together
for PREF in "${PREFIXES[@]}"
do
    echo "============== $PREF ============="
    log_files=("${PREF}"*)
    if ((${#log_files[@]})); then
        wc -l -- "${log_files[@]}"
        # awstats merger has bugs, so using the ancient technology here
        /usr/local/bin/mergelog "${log_files[@]}" > "combined-${PREF}.log"
        rm -- "${log_files[@]}"
    else
        : > "combined-${PREF}.log"
    fi
done

# Step 3, run webalizer against these log files
timeout 1800 /home/mesonet/bin/webalizer -c "${CONFBASE}/mesonet.conf" -T combined-iem.log
timeout 300 /home/mesonet/bin/webalizer -c "${CONFBASE}/sustainablecorn.conf" combined-sustainablecorn.log
timeout 300 /home/mesonet/bin/webalizer -c "${CONFBASE}/datateam.conf" combined-datateam.log
timeout 300 /home/mesonet/bin/webalizer -c "${CONFBASE}/depbackend.conf" combined-depbackend.log

grep " /agclimate" combined-iem.log > agclimate.log || [[ $? -eq 1 ]]
timeout 300 /home/mesonet/bin/webalizer -c "${CONFBASE}/agclimate.conf" -T agclimate.log
rm -f agclimate.log

# Copy to shared NFS space
rsync -a --exclude '*webalizer*db' /mnt/webalizer/usage/. /mesonet/share/usage/

# Step 4, archive these files
for PREF in "${PREFIXES[@]}"
do
    mv -- "combined-${PREF}.log" "${PREF}-${yyyymmddhh}.log"
    gzip -- "${PREF}-${yyyymmddhh}.log"
done

# Step 6, mv files to local cache
mkdir -p "../save/${yyyy}/${mm}"
archives=(*-"${yyyymmddhh}".log.gz)
if ((${#archives[@]})); then
    mv -- "${archives[@]}" "../save/${yyyy}/${mm}/"
fi

# Step 7, delete files from local cache
cd ../save || exit 1
tmpwatch 10d .
# Done!
