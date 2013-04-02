#  This process copies data around to longer term locations on a monthly basis
#

set MM="${2}"
set YY="${1}"
set YYYY="20${YY}"

echo "Lets do SAO data!"
cd /mesonet/data/text/sao/
gzip ${YY}${MM}????.sao
mkdir -p /mesonet/ARCHIVE/raw/sao/${YYYY}_${MM}
mv ${YY}${MM}????.sao.gz /mesonet/ARCHIVE/raw/sao/${YYYY}_${MM}/

echo "Lets go ASOS.gem"
cd /mesonet/data/gempak/asos
mkdir -p /mesonet/ARCHIVE/gempak/surface/ASOS/${YYYY}_${MM}
mv ${YY}${MM}??_asos.gem /mesonet/ARCHIVE/gempak/surface/ASOS/${YYYY}_${MM}/

echo "Lets go AWOS.gem"
cd /mesonet/data/gempak/awos
mkdir -p /mesonet/ARCHIVE/gempak/surface/AWOS/${YYYY}_${MM}
mv ${YY}${MM}??_awos.gem /mesonet/ARCHIVE/gempak/surface/AWOS/${YYYY}_${MM}/

echo "Lets go meso.gem"
cd /mesonet/data/gempak/meso
mkdir -p /mesonet/ARCHIVE/gempak/surface/mesonet/${YYYY}_${MM}
mv ${YY}${MM}??_meso.gem /mesonet/ARCHIVE/gempak/surface/mesonet/${YYYY}_${MM}/

echo "Lets go rwis.gem"
cd /mesonet/data/gempak/rwis
mkdir -p /mesonet/ARCHIVE/gempak/surface/RWIS/${YYYY}_${MM}
mv ${YY}${MM}??_rwis.gem /mesonet/ARCHIVE/gempak/surface/RWIS/${YYYY}_${MM}/

echo "Lets go sao.gem"
cd /mesonet/data/gempak/sao
mkdir -p /mesonet/ARCHIVE/gempak/surface/sao/${YYYY}_${MM}
mv ${YY}${MM}??_sao.gem /mesonet/ARCHIVE/gempak/surface/sao/${YYYY}_${MM}/

echo "Lets go snet.gem"
cd /mesonet/data/gempak/snet
mkdir -p /mesonet/ARCHIVE/gempak/surface/snet/${YYYY}_${MM}
mv ${YY}${MM}??_snet.gem /mesonet/ARCHIVE/gempak/surface/snet/${YYYY}_${MM}/
