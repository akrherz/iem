"""
 Write current storm attributes to a shapefile...
"""
import shapefile
import mx.DateTime
import zipfile
import os
import shutil
from pyiem import wellknowntext
import subprocess
import psycopg2.extras
POSTGIS = psycopg2.connect(database='postgis', host='iemdb')
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

w = shapefile.Writer(shapefile.POINT)
w.field("VALID", 'S', 12, 0)
w.field("STORM_ID", 'S', 2, 0)
w.field("NEXRAD", 'S', 3, 0)
w.field("AZIMUTH", 'N', 3, 0)
w.field("RANGE", 'N', 3, 0)
w.field("TVS", 'S', 10, 0)
w.field("MESO", 'S', 10, 0)
w.field("POSH", 'N', 3, 0)
w.field("POH", 'N', 3, 0)
w.field("MAX_SIZE", 'F', 5, 2)
w.field("VIL", 'N', 3, 0)
w.field("MAX_DBZ", 'N', 3, 0)
w.field("MAX_DBZ_H", 'F', 5, 2)
w.field("TOP", 'F', 5, 2)
w.field("DRCT", 'F', 3, 0)
w.field("SKNT", 'F', 3, 0)
w.field("LAT", 'F', 10, 4)
w.field("LON", 'F', 10, 4)

sql = """
DELETE from nexrad_attributes WHERE valid < '%s+00'
""" % (eTS.strftime("%Y-%m-%d %H:%M"), )
pcursor.execute(sql)
sql = """SELECT *, valid at time zone 'UTC' as utcvalid,
    ST_astext(geom) as tgeom, ST_x(geom) as lon,
       ST_y(geom) as lat from nexrad_attributes """
pcursor.execute(sql)

for row in pcursor:
    s = row["tgeom"]
    if s is None or s == "":
        continue
    f = wellknowntext.convert_well_known_text(s)
    w.point(f[0], f[1])
    w.record(row['utcvalid'].strftime("%Y%m%d%H%M"),
             row['storm_id'],
             row['nexrad'],
             float(row['azimuth']),
             float(row['range']),
             row['tvs'],
             row['meso'],
             float(row['posh']),
             float(row['poh']),
             float(row['max_size']),
             float(row['vil']),
             float(row['max_dbz']),
             float(row['max_dbz_height']),
             float(row['top']),
             float(row['drct']),
             float(row['sknt']),
             float(row['lat']),
             float(row['lon']))

if pcursor.rowcount == 0:
    if now.minute == 1:
        print 'No NEXRAD attributes found, this may be bad!'
    w.point(0.1, 0.1)
    w.record("200000000000",
             "XX",
             "XXX",
             0,
             0,
             "NONE",
             "NONE",
             0,
             0,
             0,
             0,
             0,
             0,
             0,
             0,
             0,
             0,
             0)

w.save('current_nexattr')
shutil.copy("/opt/iem/data/gis/meta/4326.prj", "current_nexattr.prj")
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
zinfo = z.getinfo('current_nexattr.txt')
zinfo.external_attr = 0664 << 16
z.close()

cmd = ("/home/ldm/bin/pqinsert -p \"zip c %s "
       "gis/shape/4326/us/current_nexattr.zip bogus zip\" "
       "current_nexattr.zip") % (now.strftime("%Y%m%d%H%M"),)
subprocess.call(cmd, shell=True)

for suffix in ['zip', 'shp', 'dbf', 'shx', 'prj']:
    os.unlink('current_nexattr.%s' % (suffix,))
