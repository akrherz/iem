"""
 Generate a Weather Central Formatted file of ASOS/AWOS Precip
"""

import mx.DateTime
import os
import Ngl
import numpy
import shutil
import subprocess
import iemdb
import psycopg2.extras
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor( cursor_factory=psycopg2.extras.DictCursor )
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor( cursor_factory=psycopg2.extras.DictCursor )
import network
nt = network.Table(("IA_ASOS", "AWOS"))


def compute_climate(sts, ets):
    sql = """SELECT station, sum(gdd50) as cgdd,
        sum(precip) as crain from climate WHERE valid >= '2000-%s' and 
        valid < '2000-%s' and gdd50 is not null GROUP by station""" % (
        sts.strftime("%m-%d"), ets.strftime("%m-%d"))
    ccursor.execute( sql )
    data = {}
    for row in ccursor:
        data[ row[0] ] = row
    return data

def compute_obs():
    """ Compute the GS values given a start/end time and networks to look at
    """
    sql = """
SELECT
  s.id, x(s.geom) as lon, y(s.geom) as lat,
  sum(CASE WHEN
   day = 'TODAY'::date and pday > 0 
   THEN pday ELSE 0 END) as p01,
  sum(CASE WHEN
   day IN ('TODAY'::date,'YESTERDAY'::date) and pday > 0 
   THEN pday ELSE 0 END) as p02,
  sum(CASE WHEN
    pday > 0 
   THEN pday ELSE 0 END) as p03
FROM 
  summary_%s c, stations s
WHERE
  s.network in ('IA_ASOS','AWOS') and
  s.iemid = c.iemid and 
  day IN ('TODAY'::date,'YESTERDAY'::date, 'TODAY'::date - '2 days'::interval)
GROUP by s.id, lon, lat
    """ % (mx.DateTime.now().year,)
    icursor.execute( sql )
    data = {}
    for row in icursor:
        data[row['id']] = row
    return data

def main():
    output = open('wxc_airport_precip.txt', 'w')
    output.write("""Weather Central 001d0300 Surface Data TimeStamp=%s
   6
   4 Station
   6 TODAY RAIN
   6 DAY2 RAIN
   6 DAY3 RAIN
   6 Lat
   8 Lon
""" % (mx.DateTime.gmt().strftime("%Y.%m.%d.%H%M"),))
    data = compute_obs()
    for id in data.keys():
        output.write("K%s %6.2f %6.2f %6.2f %6.3f %8.3f\n" % (id, 
        data[id]['p01'], data[id]['p02'], data[id]['p03'],
        data[id]['lat'], data[id]['lon'] ))
    output.close()
    subprocess.call("/home/ldm/bin/pqinsert -p \"wxc_airport_precip.txt\" wxc_airport_precip.txt", shell=True)
    shutil.copyfile("wxc_airport_precip.txt", "/mesonet/share/pickup/wxc/wxc_airport_precip.txt")
    os.remove("wxc_airport_precip.txt")

if __name__ == '__main__':
    main()
