#!/bin/csh

# Super Script to backup data to some location
# 11 Mar 2002:	Don't use /tmp/files, since it is strubbed
# 12 Apr 2003	Also backup shef data 
#		mount directories as needed...
# 19 Aug 2003	Don't worry about SCAN data anymore
# 20 Mar 2005	Adopt for main mesonet server

mount /mnt/backup2

set YYYY_mm=`date --date "1 day ago" +"%Y_%m"`
set yymmdd=`date --date "1 day ago" +"%y%m%d"`
set yyyymmdd=`date --date "1 day ago" +"%Y%m%d"`
set dd=`date --date "1 day ago" +"%d"`

set tardate=`date --date "2 days ago" +"%m/%d/%Y"`

cd /tmp

mkdir ${dd}_backup

set BACKUP_DIR=/tmp/${dd}_backup

#echo "Backup SAO RAW"
cd /mesonet/data/text/sao
tar -czf ${BACKUP_DIR}/sao.tgz ${yymmdd}*sao

#echo "Backup RWIS RAW"
#cd /mesonet/ARCHIVE/raw/rwis/${YYYY_mm}/${dd}
#tar -czf ${BACKUP_DIR}/rwis.tgz *.dat

#echo "Backup SCAN"
#cd /mesonet/ARCHIVE/raw/scan/${YYYY_mm}/
#tar -czf ${BACKUP_DIR}/scan.tgz 2031_${yyyymmdd}.txt

#echo "Backup SNET"
cd /mesonet/ARCHIVE/raw/snet/${YYYY_mm}/${dd}
tar -czf ${BACKUP_DIR}/snet.tgz *.dat

#echo "Backup SHEF"
#cd /mesonet/data/text/RRS/
#tar -czf ${BACKUP_DIR}/snef.tgz ${yyyymmdd}.rrs

cd /tmp
#ls -l ${dd}_backup
tar -cf ${yyyymmdd}.tar ${dd}_backup/
rm -Rf ${dd}_backup/

mv ${yyyymmdd}.tar /mnt/backup2/dailydata/
#echo "Data Backup Done"

#echo "Files in home"
#cd /tmp
#tar -czf ${yyyymmdd}.tgz --exclude /home/mesonet/ARCHIVE --newer ${tardate} /home/mesonet
#ls -l ${yyyymmdd}.tgz
#mv ${yyyymmdd}.tgz /mnt/backup2/mesonethome/
#echo "Done with Files"

umount /mnt/backup2
