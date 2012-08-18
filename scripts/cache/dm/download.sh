#!/bin/bash

DATADIR="`date --date 'last tuesday' +'%Y/%b%-d'`"
TS="`date --date 'last tuesday' +'%Y'`"
TS2="`date --date 'last tuesday' +'%y%m%d'`"
TS3="`date --date 'last tuesday' +'%m%d%y'`"
DATAFILE="usdm${TS2}m.zip"

wget -q http://droughtmonitor.unl.edu/shapefiles_combined/${TS}/usdm${TS2}m.zip

unzip $DATAFILE

ogr2ogr -t_srs EPSG:4326 -f "ESRI Shapefile" dm_current.shp usdm${TS2}.shp

# Combine Coverages
#python combine.py $TS2

# Create combined zipfile
zip dm_current.zip dm_current.shp dm_current.shx dm_current.dbf dm_current.prj

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
rm dm_current.shp dm_current.shx dm_current.dbf dm_current.zip dm_current.prj
mv usdm* last/

#ogr2ogr -t_srs EPSG:4326 test.shp Drought_Impacts_US.shp

#mkdir -p $ARCHIVE
#mv $DATAFILE $ARCHIVE/
#cd $ARCHIVE
#unzip $DATAFILE
