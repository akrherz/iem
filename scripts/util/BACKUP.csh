# Super Script to backup data to some location, run from RUN_12Z
# Not really used by all that much, but need to do that schoolnet portion

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

#echo "Backup SNET"
cd /mesonet/ARCHIVE/raw/snet/${YYYY_mm}/${dd}
tar -czf ${BACKUP_DIR}/snet.tgz *.dat

cd /mesonet/tmp
#ls -l ${dd}_backup
tar -cf ${yyyymmdd}.tar ${dd}_backup/
rm -Rf ${dd}_backup/

mv ${yyyymmdd}.tar /mesonet/ARCHIVE/dailydata/
#echo "Data Backup Done"
