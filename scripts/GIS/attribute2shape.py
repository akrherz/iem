"""
 Write current storm attributes to a shapefile...
"""
import shapelib
import dbflib
import mx.DateTime
import zipfile
import os
import sys
import shutil
import wellknowntext
import iemdb
import subprocess
import psycopg2.extras
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor(cursor_factory=psycopg2.extras.DictCursor)

"""
 nexrad         | character(3)             |
 storm_id       | character(2)             |
 geom           | geometry                 |
 azimuth        | smallint                 |
 range          | smallint                 |
 tvs            | character varying(10)    |
 meso           | character varying(10)    |
 posh           | smallint                 |
 poh            | smallint                 |
 max_size       | real                     |
 vil            | smallint                 |
 max_dbz        | smallint                 |
 max_dbz_height | real                     |
 top            | real                     |
 drct           | smallint                 |
 sknt           | smallint                 |
 valid          | timestamp with time zone |
"""

os.chdir("/tmp")

# Delete anything older than 20 minutes
now = mx.DateTime.gmt()
eTS = mx.DateTime.gmt() - mx.DateTime.RelativeDateTime(minutes=+20)

shp = shapelib.create("current_nexattr", shapelib.SHPT_POINT)

dbf = dbflib.create("current_nexattr")
dbf.add_field("VALID", dbflib.FTString, 12, 0)
dbf.add_field("STORM_ID", dbflib.FTString, 2, 0)
dbf.add_field("NEXRAD", dbflib.FTString, 3, 0)
dbf.add_field("AZIMUTH", dbflib.FTInteger, 3, 0)
dbf.add_field("RANGE", dbflib.FTInteger, 3, 0)
dbf.add_field("TVS", dbflib.FTString, 10, 0)
dbf.add_field("MESO", dbflib.FTString, 10, 0)
dbf.add_field("POSH", dbflib.FTInteger, 3, 0)
dbf.add_field("POH", dbflib.FTInteger, 3, 0)
dbf.add_field("MAX_SIZE", dbflib.FTDouble, 5, 2)
dbf.add_field("VIL", dbflib.FTInteger, 3, 0)
dbf.add_field("MAX_DBZ", dbflib.FTInteger, 3, 0)
dbf.add_field("MAX_DBZ_H", dbflib.FTDouble, 5, 2)
dbf.add_field("TOP", dbflib.FTDouble, 5, 2)
dbf.add_field("DRCT", dbflib.FTDouble, 3, 0)
dbf.add_field("SKNT", dbflib.FTDouble, 3, 0)
dbf.add_field("LAT", dbflib.FTDouble, 10, 4)
dbf.add_field("LON", dbflib.FTDouble, 10, 4)

sql = """DELETE from nexrad_attributes WHERE valid < '%s+00'""" % (
							eTS.strftime("%Y-%m-%d %H:%M"), )
pcursor.execute( sql )
sql = """SELECT *, valid at time zone 'UTC' as utcvalid, 
	astext(geom) as tgeom, x(geom) as lon, 
       y(geom) as lat from nexrad_attributes """
pcursor.execute( sql )

cnt = 0
for row in pcursor:
    #print rs[i]
    s = row["tgeom"]
    if s == None or s == "":
        continue
    f = wellknowntext.convert_well_known_text(s)

    d = {}
    d["VALID"] = row['utcvalid'].strftime("%Y%m%d%H%M")
    d["NEXRAD"] = row['nexrad']
    d["STORM_ID"] = row['storm_id']
    d["AZIMUTH"] = float(row['azimuth'])
    d["RANGE"] = float(row['range'])
    d["TVS"] = row['tvs']
    d["MESO"] = row['meso']
    d["POSH"] = float(row['posh'])
    d["POH"] = float(row['poh'])
    d["MAX_SIZE"] = float(row['max_size'])
    d["VIL"] = float(row['vil'])
    d["MAX_DBZ"] = float(row['max_dbz'])
    d["MAX_DBZ_H"] = float(row['max_dbz_height'])
    d["TOP"] = float(row['top'])
    d["DRCT"] = float(row['drct'])
    d["SKNT"] = float(row['sknt'])
    d["LAT"] = float(row['lat'])
    d["LON"] = float(row['lon'])
    #print d
    obj = shapelib.SHPObject(shapelib.SHPT_POINT, 1, [[f,]] )
    shp.write_object(-1, obj)
    dbf.write_record(cnt, d)
    del(obj)
    cnt += 1

if (cnt == 0):
    if now.minute == 1:
        print 'No NEXRAD attributes found, this may be bad!'
    obj = shapelib.SHPObject(shapelib.SHPT_POINT, 1, [[(0.1, 0.1),]] )
    d = {}
    d["VALID"] = "200000000000"
    d["NEXRAD"] = "XXX"
    d["STORM_ID"] = "XX"
    d["AZIMUTH"] = 0
    d["RANGE"] = 0
    d["TVS"] = "NONE"
    d["MESO"] = "NONE"
    d["POSH"] = 0
    d["POH"] = 0
    d["MAX_SIZE"] = 0
    d["VIL"] = 0
    d["MAX_DBZ"] = 0
    d["MAX_DBZ_H"] = 0
    d["TOP"] = 0
    d["DRCT"] = 0
    d["SKNT"] = 0
    d["LAT"] = 0
    d["LON"] = 0

    shp.write_object(-1, obj)
    dbf.write_record(0, d)

del(shp)
del(dbf)
shutil.copy("/mesonet/data/gis/meta/4326.prj", "current_nexattr.prj")
z = zipfile.ZipFile("current_nexattr.zip", 'w', zipfile.ZIP_DEFLATED)
z.write("current_nexattr.shp")
z.write("current_nexattr.shx")
z.write("current_nexattr.dbf")
z.write("current_nexattr.prj")
information = """
   Iowa Environmental Mesonet 
   National Weather Service NEXRAD Storm Attributes Shapefile

*** Warning: This information is provided without warranty and its future
    availability is not gaurenteed by Iowa State University ***

This file contains a current snapshot of NEXRAD storm attributes from the 
last received volume scan from each NWS WSR-88D RADAR.  Any storm 
attribute from a volume scan 20+ minutes old is not included.

The DBF Columns are as follows.
  - VALID    Timestamp of the NEXRAD Volume Scan YearMonthDayHourMinute
  - NEXRAD   3 character identifier of the WSR-88D
  - STORM_ID Local WSR-88D assigned storm attribute ID
  - AZIMUTH  Direction from north of the attribute in relation to the
             NEXRAD [degree] 90 == East, 180 == South
  - RANGE    Distance away from RADAR in miles
  - TVS      Tornado Vortex Signature, available values below
             NONE - No TVS detected
             TVS  - Low Level TVS detected
             ETVS - Elevated TVS deteched
  - MESO     Mesocyclone, available values below
             NONE - No MESO Detected
             3DCO - 3 Dimensional Correlated Shear Detected
             MESO - Mesocyclone Indentified
             UNCO - Uncorrelated 2-D Shear Detected
             1-25 - A number between 1 and 25, not sure what this means yet
  - POSH     Probability of Severe Hail (+0.75" or larger)
  - POH      Probability of Hail 
  - MAX_SIZE Maximum Hail Size in inches
  - VIL      Vertically Integrated Liquid [inches]
  - MAX_DBZ  Maximum dBZ value
  - MAX_DBZ_ Height of Maxium dBZ in thousands of feet
  - TOP      Storm Top in thousands of feet
  - DRCT     Storm movement direction [degrees from north]
  - SKNT     Storm movement velocity [knots]
  - LAT      Convience replication of the data in the SHP file [deg North]
  - LON      Convience replication of the data in the SHP file [deg East]

Contact Info:
  Daryl Herzmann akrherz@iastate.edu 515-294-5978

"""
z.writestr("current_nexattr.txt", information)
z.close()

cmd = "/home/ldm/bin/pqinsert -p \"zip c %s gis/shape/4326/us/current_nexattr.zip bogus zip\" current_nexattr.zip" % (now.strftime("%Y%m%d%H%M"),)
subprocess.call(cmd, shell=True)

for suffix in ['zip', 'shp', 'dbf', 'shx', 'prj']:
	os.unlink('current_nexattr.%s' % (suffix,))
