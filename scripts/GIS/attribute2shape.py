"""Write current storm attributes to a shapefile...

Run every minute from RUN_1MIN.sh
"""
from __future__ import print_function
import zipfile
import os
import shutil
import subprocess
import datetime

import pytz
import shapefile
import psycopg2.extras
from pyiem.util import get_dbconn

INFORMATION = """
   Iowa Environmental Mesonet
   National Weather Service NEXRAD Storm Attributes Shapefile

*** Warning: This information is provided without warranty and its future
    availability is not guaranteed by Iowa State University ***

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
             ETVS - Elevated TVS detected
  - MESO     Mesocyclone, available values below
             NONE - No MESO Detected
             3DCO - 3 Dimensional Correlated Shear Detected
             MESO - Mesocyclone Identified
             UNCO - Uncorrelated 2-D Shear Detected
             1-25 - A number between 1 and 25, not sure what this means yet
  - POSH     Probability of Severe Hail (+0.75" or larger)
  - POH      Probability of Hail
  - MAX_SIZE Maximum Hail Size in inches
  - VIL      Vertically Integrated Liquid [inches]
  - MAX_DBZ  Maximum dBZ value
  - MAX_DBZ_ Height of Maximum dBZ in thousands of feet
  - TOP      Storm Top in thousands of feet
  - DRCT     Storm movement direction [degrees from north]
  - SKNT     Storm movement velocity [knots]
  - LAT      Convenience replication of the data in the SHP file [deg North]
  - LON      Convenience replication of the data in the SHP file [deg East]

Contact Info:
  Daryl Herzmann akrherz@iastate.edu 515-294-5978
"""


def shpschema():
    """Create the schema

    C is ASCII characters
    N is a double precision integer limited to around 18 characters in length
    D is for dates in the YYYYMMDD format,
         with no spaces or hyphens between the sections
    F is for floating point numbers with the same length limits as N
    L is for logical data which is stored in the shapefile's attribute table
        as a short integer as a 1 (true) or a 0 (false).
        The values it can receive are 1, 0, y, n, Y, N, T, F
        or the python builtins True and False
    """
    shp = shapefile.Writer('current_nexattr')
    shp.field("VALID", 'C', 12, 0)
    shp.field("STORM_ID", 'C', 2, 0)
    shp.field("NEXRAD", 'C', 3, 0)
    shp.field("AZIMUTH", 'N', 3, 0)
    shp.field("RANGE", 'N', 3, 0)
    shp.field("TVS", 'C', 10, 0)
    shp.field("MESO", 'C', 10, 0)
    shp.field("POSH", 'N', 3, 0)
    shp.field("POH", 'N', 3, 0)
    shp.field("MAX_SIZE", 'F', 5, 2)
    shp.field("VIL", 'N', 3, 0)
    shp.field("MAX_DBZ", 'N', 3, 0)
    shp.field("MAX_DBZ_H", 'F', 5, 2)
    shp.field("TOP", 'F', 9, 2)
    shp.field("DRCT", 'N', 3, 0)
    shp.field("SKNT", 'N', 3, 0)
    shp.field("LAT", 'F', 10, 4)
    shp.field("LON", 'F', 10, 4)
    return shp


def main():
    """Go Main Go"""
    pgconn = get_dbconn('postgis')
    pcursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    os.chdir("/tmp")

    # Delete anything older than 20 minutes
    now = datetime.datetime.utcnow()
    now = now.replace(tzinfo=pytz.utc)
    ets = now - datetime.timedelta(minutes=20)

    shp = shpschema()

    # Less aggressively delete data
    if now.minute % 10 == 0:
        pcursor.execute("""
            DELETE from nexrad_attributes WHERE valid < %s
        """, (ets, ))
    pcursor.execute("""
        SELECT *, valid at time zone 'UTC' as utcvalid,
        ST_x(geom) as lon, ST_y(geom) as lat from nexrad_attributes
        WHERE valid > %s
    """, (ets, ))

    for row in pcursor:
        shp.point(row['lon'], row['lat'])
        shp.record(row['utcvalid'].strftime("%Y%m%d%H%M"),
                   row['storm_id'],
                   row['nexrad'],
                   row['azimuth'],
                   row['range'],
                   row['tvs'],
                   row['meso'],
                   row['posh'],
                   row['poh'],
                   row['max_size'],
                   row['vil'],
                   row['max_dbz'],
                   row['max_dbz_height'],
                   row['top'],
                   row['drct'],
                   row['sknt'],
                   row['lat'],
                   row['lon'])

    if pcursor.rowcount == 0:
        if now.minute == 1:
            print('No NEXRAD attributes found, this may be bad!')
        shp.point(0.1, 0.1)
        shp.record("200000000000",
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

    shp.close()
    shutil.copy("/opt/iem/data/gis/meta/4326.prj", "current_nexattr.prj")
    zfp = zipfile.ZipFile("current_nexattr.zip", 'w', zipfile.ZIP_DEFLATED)
    zfp.write("current_nexattr.shp")
    zfp.write("current_nexattr.shx")
    zfp.write("current_nexattr.dbf")
    zfp.write("current_nexattr.prj")

    zfp.writestr("current_nexattr.txt", INFORMATION)
    zinfo = zfp.getinfo('current_nexattr.txt')
    zinfo.external_attr = 0o664
    zfp.close()

    cmd = ("/home/ldm/bin/pqinsert -i -p \"zip c %s "
           "gis/shape/4326/us/current_nexattr.zip bogus zip\" "
           "current_nexattr.zip") % (now.strftime("%Y%m%d%H%M"),)
    subprocess.call(cmd, shell=True)

    for suffix in ['zip', 'shp', 'dbf', 'shx', 'prj']:
        os.unlink('current_nexattr.%s' % (suffix,))


if __name__ == '__main__':
    main()
