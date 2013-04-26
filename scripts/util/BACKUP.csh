# Super Script to backup data to some location

set YYYY_mm=`date --date "1 day ago" +"%Y_%m"`
set yymmdd=`date --date "1 day ago" +"%y%m%d"`
set yyyymmdd=`date --date "1 day ago" +"%Y%m%d"`
set dd=`date --date "1 day ago" +"%d"`

set tardate=`date --date "2 days ago" +"%m/%d/%Y"`

cd /mesonet/tmp

mkdir ${dd}_backup

set BACKUP_DIR=/mesonet/tmp/${dd}_backup

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

cd /mesonet/tmp
#ls -l ${dd}_backup
tar -cf ${yyyymmdd}.tar ${dd}_backup/
rm -Rf ${dd}_backup/

mv ${yyyymmdd}.tar /mesonet/ARCHIVE/dailydata/
#echo "Data Backup Done"

#echo "Files in home"
#cd /tmp
#tar -czf ${yyyymmdd}.tgz --exclude /home/mesonet/ARCHIVE --newer ${tardate} /home/mesonet
#ls -l ${yyyymmdd}.tgz
#mv ${yyyymmdd}.tgz /mnt/backup2/mesonethome/
#echo "Done with Files"

