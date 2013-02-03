"""
  Corrects the often poor precip data from the ISUAG network
"""

import sys
import iemre
import datetime
import netCDF4
import numpy
import pytz
import iemdb
import psycopg2.extras
ISUAG = iemdb.connect('isuag', bypass=True)
icursor = ISUAG.cursor(cursor_factory=psycopg2.extras.DictCursor)
icursor2 = ISUAG.cursor(cursor_factory=psycopg2.extras.DictCursor)

SKIP = ['A134759', # Lewis
        'A133259',
        'A135849', #Muscatine
        'A135879', #Nashua
        'A134309', #Kanawha
]

import network
nt = network.Table("ISUAG")

def fix_daily(ts):
    """
    Instead of using the IEMRE value, we should total up the hourly
    data, so to confuse people less
    """
    # Find ISUAG Data
    icursor.execute("""SELECT sum(c900) as rain, station from hourly 
	WHERE date(valid) = '%s' GROUP by station""" % (ts.strftime("%Y-%m-%d"),))
    for row in icursor:
        stid = row['station']
        if stid in SKIP:
            continue
        rain = row['rain']
        # Fix it
        sql = """UPDATE daily SET c90 = %.2f, c90_f = 'e' WHERE valid = '%s'
              and station = '%s'""" % (rain, ts.strftime("%Y-%m-%d"),
              stid)
        icursor2.execute(sql)

def fix_hourly(ts):

    """
    Fix the hourly precipitation values, just hard code the stupid IEMRE value
    """
    nc = netCDF4.Dataset("/mnt/mesonet/data/iemre/%s_mw_hourly.nc" % (
                                                            ts.year,),'r')
    p01m = nc.variables['p01m']
    offset = iemre.hour_idx(ts)
    # Find ISUAG Data
    icursor.execute("SELECT * from hourly WHERE valid = '%s+00'" % (
                                                ts.strftime("%Y-%m-%d"),))
    for row in icursor:
        stid = row['station']
        if stid in SKIP:
            continue
        lat = nt.sts[ stid ]['lat']
        lon = nt.sts[ stid ]['lon']
        # Lookup IEMRE data
        ix,jy = iemre.find_ij(lon, lat)
        estimate = 0.
        if not numpy.ma.is_masked( p01m[offset,jy,ix] ):
            estimate = p01m[offset,jy,ix] / 25.4
        if estimate > 100:
            estimate = 0
            print "Missing Estimate", ts
        if row['c900'] > 0 or estimate > 0:
            print "%s %s %-20.20s Ob: %5.2f F: %s E: %5.2f" % (
                  ts.strftime("%m%d/%H"), stid, nt.sts[stid]['name'],
                  row['c900'], row['c900_f'], estimate)
        # Fix it
        sql = """UPDATE hourly SET c900 = %.2f, c900_f = 'e' 
              WHERE valid = '%s+00'
              and station = '%s'""" % (estimate, ts.strftime("%Y-%m-%d %H:%M"),
              stid)
        icursor2.execute(sql)
    nc.close()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        ts = datetime.datetime( int(sys.argv[1]),int(sys.argv[2]),
                           int(sys.argv[3]) )
    else:
        gmt = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        ts = gmt.replace(hour=0,minute=0,second=0,microsecond=0)
    ts = ts.replace(tzinfo=pytz.timezone("America/Chicago"))
    for hr in range(24):
        now = ts.replace(hour=hr)
        fix_hourly( ts.astimezone( pytz.timezone("UTC") ) )
    fix_daily(ts)
    icursor.close()
    icursor2.close()
    ISUAG.commit()
    ISUAG.close()