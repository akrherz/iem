
DATADIR="`date --date 'last tuesday' +'%Y/%b%-d'`"
TS="`date --date 'last tuesday' +'%Y'`"
TS2="`date --date 'last tuesday' +'%Y%m%d'`"
TS3="`date --date 'last tuesday' +'%m%d%y'`"
DATAFILE="USDM_${TS2}_M.zip"
PQI="/home/ldm/bin/pqinsert"

wget -q http://droughtmonitor.unl.edu/data/shapefiles_m/${DATAFILE}

unzip $DATAFILE

ogr2ogr -t_srs EPSG:4326 -f "ESRI Shapefile" dm_current.shp USDM_${TS2}.shp

# Create combined zipfile
zip dm_current.zip dm_current.shp dm_current.shx dm_current.dbf dm_current.prj

# Copy it to the archive
ftime="`date --date 'last tuesday' +'%Y%m%d%H'`00"
$PQI -p "zip ac $ftime gis/shape/4326/us/dm_current.zip GIS/usdm/dm_$TS2.zip zip" dm_current.zip

# Cleanup
rm dm_current.shp dm_current.shx dm_current.dbf dm_current.zip dm_current.prj
mv USDM* /mesonet/data/dm/shape/
