# This process copies data around to longer term locations on a monthly basis
# run from RUN_2AM.sh on the 2nd each month
export MM="${2}"
export YY="${1}"
export YYYY="20${YY}"

# echo "Lets do SAO data!"
cd /mesonet/data/text/sao/
gzip ${YY}${MM}????.sao
mkdir -p /mesonet/ARCHIVE/raw/sao/${YYYY}_${MM}
mv ${YY}${MM}????.sao.gz /mesonet/ARCHIVE/raw/sao/${YYYY}_${MM}/

# echo "Lets go ASOS.gem"
cd /mesonet/data/gempak/asos
mkdir -p /mesonet/ARCHIVE/gempak/surface/ASOS/${YYYY}_${MM}
mv ${YY}${MM}??_asos.gem /mesonet/ARCHIVE/gempak/surface/ASOS/${YYYY}_${MM}/

# echo "Lets go meso.gem"
cd /mesonet/data/gempak/meso
mkdir -p /mesonet/ARCHIVE/gempak/surface/mesonet/${YYYY}_${MM}
mv ${YY}${MM}??_meso.gem /mesonet/ARCHIVE/gempak/surface/mesonet/${YYYY}_${MM}/

# echo "Lets go sao.gem"
cd /mesonet/data/gempak/sao
mkdir -p /mesonet/ARCHIVE/gempak/surface/sao/${YYYY}_${MM}
mv ${YY}${MM}??_sao.gem /mesonet/ARCHIVE/gempak/surface/sao/${YYYY}_${MM}/
