"""
 Generate a Weather Central Formatted file of Growing Degree Days
 for our beloved ASOS/AWOS network
"""
import datetime
import os
import Ngl
import numpy as np
import shutil
import sys
import psycopg2
import subprocess
import network
nt = network.Table("ISUAG")

ACCESS = psycopg2.connect(database='iem', host='iemdb', user='nobody')
acursor = ACCESS.cursor()

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

MESOSITE = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
mcursor = MESOSITE.cursor()

ISUAG = psycopg2.connect(database='isuag', host='iemdb', user='nobody')
icursor = ISUAG.cursor()

def sampler(xaxis, yaxis, vals, x, y):
    ''' This is lame sampler, should replace '''
    i = 0
    while (xaxis[i] < x):
        i += 1
    j = 0
    while (yaxis[j] < y):
        j += 1
    return vals[i,j]


def load_soilt(data):
    soil_obs = []
    lats = [] 
    lons = []
    valid = datetime.date.today() - datetime.timedelta(days=1)
    if datetime.datetime.now().hour < 7:
        valid -= datetime.timedelta(days=1)
    icursor.execute("""SELECT station, c30 from daily WHERE 
         valid = %s""", (valid,) )
    for row in icursor:
        stid = row[0]
        if not nt.sts.has_key(stid):
            continue
        soil_obs.append( row[1] )
        lats.append( nt.sts[stid]['lat'] )
        lons.append( nt.sts[stid]['lon'] )
    if len(lons) < 4:
        print 'No ISUAG Data for %s' % (valid,)
        sys.exit()
    numxout = 40
    numyout = 40
    xmin    = min(lons) - 1.
    ymin    = min(lats) - 1.
    xmax    = max(lons) + 1.
    ymax    = max(lats) + 1.
    xc      = (xmax-xmin)/(numxout-1)
    yc      = (ymax-ymin)/(numyout-1)

    xo = xmin + xc* np.arange(0,numxout)
    yo = ymin + yc* np.arange(0,numyout)

    analysis = Ngl.natgrid(lons, lats, soil_obs, list(xo), list(yo))
    for sid in data.keys():
        data[sid]['soilt'] = sampler(xo,yo,analysis, data[sid]['lon'], 
                                     data[sid]['lat'])


def build_xref():
    mcursor.execute("""SELECT id, climate_site from stations 
    WHERE network in ('IA_ASOS','AWOS')""")
    data = {}
    for row in mcursor:
        data[row[0]] = row[1]
    return data

def compute_climate(sts, ets):
    sql = """SELECT station, sum(gdd50) as cgdd,
    sum(precip) as crain from climate WHERE valid >= '2000-%s' and 
    valid < '2000-%s' and gdd50 is not null GROUP by station""" % (
                                sts.strftime("%m-%d"), ets.strftime("%m-%d"))
    ccursor.execute(sql)
    data = {}
    for row in ccursor:
        data[row[0]] = {'cgdd': row[1], 'crain': row[2]}
    return data

def compute_obs(sts, ets):
    """ Compute the GS values given a start/end time and networks to look at
    """
    sql = """
SELECT
  id, x(s.geom) as lon, y(s.geom) as lat,
  sum( case when max_tmpf = -99 THEN 1 ELSE 0 END) as missing,
  sum( gdd50(max_tmpf, min_tmpf) ) as gdd,
  sum( case when pday > 0 THEN pday ELSE 0 END ) as precip
FROM 
  summary_%s c, stations s
WHERE
  s.network in ('IA_ASOS','AWOS') and
  day >= '%s' and day < '%s' and
  c.iemid = s.iemid
GROUP by s.id, lon, lat
    """ % (sts.year, sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d"))
    acursor.execute(sql)
    data = {}
    for row in acursor:
        data[ row[0] ] = {'id': row[0], 'lon': row[1], 'lat': row[2],
                          'missing': row[3], 'gdd': row[4], 
                          'precip': row[5]}
    return data

def main():
    sts = datetime.datetime.now()
    sts =  sts.replace(month=5,day=1)
    ets = datetime.datetime.now()
    if sts > ets:
        return

    output = open('wxc_iem_agdata.txt', 'w')
    output.write("""Weather Central 001d%s00 Surface Data
   8
   4 Station
   4 GDD_MAY1
   4 GDD_MAY1_NORM
   5 PRECIP_MAY1
   5 PRECIP_MAY1_NORM
   5 SOIL_4INCH
   6 Lat
   8 Lon
""" % (ets.strftime("%H"),))
    days = (ets - sts).days
    data = compute_obs( sts, ets )
    load_soilt(data)
    cdata = compute_climate( sts, ets )
    xref = build_xref()
    for sid in data.keys():
        if data[sid]['missing'] > (days * 0.1):
            continue
        csite = xref[sid]
        output.write("K%s %4.0f %4.0f %5.2f %5.2f %5.1f %6.3f %8.3f\n" % (sid, 
                    data[sid]['gdd'], cdata[ csite ]['cgdd'],
                    data[sid]['precip'], cdata[ csite ]['crain'], data[sid]['soilt'],
                    data[sid]['lat'], data[sid]['lon'] ))
    output.close()
    subprocess.call(("/home/ldm/bin/pqinsert -p \"wxc_iem_agdata.txt\""
                     +" wxc_iem_agdata.txt"), shell=True)
    shutil.copyfile("wxc_iem_agdata.txt", "/mesonet/share/pickup/wxc/wxc_iem_agdata.txt")
    os.remove("wxc_iem_agdata.txt")

if __name__ == '__main__':
    main()
