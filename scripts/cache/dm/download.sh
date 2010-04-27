#!/bin/bash

DATADIR="`date --date 'last tuesday' +'%Y/%b%-d'`"
#DATADIR="`date --date 'last tuesday' +'%Y'`"
TS="`date --date 'last tuesday' +'%y%m%d'`"
TS2="`date --date 'last tuesday' +'%Y%m%d'`"
TS3="`date --date 'last tuesday' +'%m%d%y'`"
#DATAFILE="usdm${TS3}.zip"
DATAFILE="USDM${TS3}.zip"
PASSWORD=`cat passwd`

lftp -u drought,${PASSWORD} -e "get /dm/shapefiles/$DATADIR/$DATAFILE; quit" http://drought.unl.edu

unzip $DATAFILE

# Combine Coverages
/mesonet/python/bin/python combine.py $TS2

# Create combined zipfile
#zip dm_current.zip dm_$TS2.shp dm_$TS2.shx dm_$TS2.dbf
mv dm_$TS2.shp dm_current.shp
mv dm_$TS2.shx dm_current.shx
mv dm_$TS2.dbf dm_current.dbf
zip dm_current.zip dm_current.shp dm_current.shx dm_current.dbf

# Copy it to the archive
ftime="`date --date 'last tuesday' +'%Y%m%d%H'`00"
#mkdir -p $ARCHIVE
#cp dm_current.zip dm_$TS2.shp dm_$TS2.shx dm_$TS2.dbf $ARCHIVE
#/home/ldm/bin/pqinsert -p "gis ac $ftime gis/shape/4326/us/usdm/dm_current.shp GIS/usdm/dm_$TS2.shp shp" dm_$TS2.shp
#/home/ldm/bin/pqinsert -p "gis ac $ftime gis/shape/4326/us/usdm/dm_current.dbf GIS/usdm/dm_$TS2.dbf dbf" dm_$TS2.dbf
#/home/ldm/bin/pqinsert -p "gis ac $ftime gis/shape/4326/us/usdm/dm_current.shx GIS/usdm/dm_$TS2.shx shx" dm_$TS2.shx
/home/ldm/bin/pqinsert -p "zip ac $ftime gis/shape/4326/us/dm_current.zip GIS/usdm/dm_$TS2.zip zip" dm_current.zip

# Move it to the IEM GIS Data
#mv dm_$TS2.shp /mesonet/data/gis/shape/4326/us/usdm/dm_current.shp
#mv dm_$TS2.shx /mesonet/data/gis/shape/4326/us/usdm/dm_current.shx
#mv dm_$TS2.dbf /mesonet/data/gis/shape/4326/us/usdm/dm_current.dbf
#mv dm_current.zip /mesonet/data/gis/shape/4326/us/usdm/

# Cleanup
rm dm_current.shp dm_current.shx dm_current.dbf dm_current.zip
mv Drought_* USDM*zip last/

#ogr2ogr -t_srs EPSG:4326 test.shp Drought_Impacts_US.shp

#mkdir -p $ARCHIVE
#mv $DATAFILE $ARCHIVE/
#cd $ARCHIVE
#unzip $DATAFILE
