# Super Script to backup data to some location, run from RUN_12Z

export YYYY_mm=$(date --date "1 day ago" +"%Y_%m")
export yymmdd=$(date --date "1 day ago" +"%y%m%d")
export yyyymmdd=$(date --date "1 day ago" +"%Y%m%d")
export dd=$(date --date "1 day ago" +"%d")

export tardate=$(date --date "2 days ago" +"%m/%d/%Y")

cd /mesonet/tmp

mkdir ${dd}_backup

set BACKUP_DIR=/mesonet/tmp/${dd}_backup

cd /mesonet/data/text/sao
tar -czf ${BACKUP_DIR}/sao.tgz ${yymmdd}*sao

cd /mesonet/tmp
tar -cf ${yyyymmdd}.tar ${dd}_backup/
rm -Rf ${dd}_backup/

rsync -a --remove-source-files --rsync-path "mkdir -p /stage/iemoffline/dailydata && rsync" ${yyyymmdd}.tar metl60:/stage/iemoffline/dailydata/
