# Super Script to backup data to some location, run from RUN_12Z

yymmdd=$(date --date "1 day ago" +"%y%m%d")
yyyymmdd=$(date --date "1 day ago" +"%Y%m%d")
dd=$(date --date "1 day ago" +"%d")

cd /mesonet/tmp

mkdir ${dd}_backup

BACKUP_DIR=/mesonet/tmp/${dd}_backup

cd /mesonet/data/text/sao
tar -czf ${BACKUP_DIR}/sao.tgz ${yymmdd}*sao

cd /mesonet/tmp
tar -cf ${yyyymmdd}.tar ${dd}_backup/
rm -Rf ${dd}_backup/

rsync -a --remove-source-files --rsync-path "mkdir -p /stage/iemoffline/dailydata && rsync" ${yyyymmdd}.tar akrherz-desktop:/stage/iemoffline/dailydata/
