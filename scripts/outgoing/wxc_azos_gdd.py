# Generate a Weather Central Formatted file of Growing Degree Days
# for our beloved ASOS/AWOS network

import mx.DateTime, os
from pyIEM import iemdb
i = iemdb.iemdb()
access = i['iem']
coop = i['coop']
mesosite = i['mesosite']

def build_xref():
    rs = mesosite.query("SELECT id, climate_site from stations WHERE network in ('IA_ASOS','AWOS')").dictresult()
    data = {}
    for i in range(len(rs)):
        data[rs[i]['id']] = rs[i]['climate_site']
    return data

def compute_climate(sts, ets):
    sql = """SELECT station, sum(gdd50) as cgdd,
    sum(precip) as crain from climate WHERE valid >= '2000-%s' and valid < '2000-%s' and gdd50 is not null GROUP by station""" % (sts.strftime("%m-%d"), ets.strftime("%m-%d"))
    rs = coop.query(sql).dictresult()
    data = {}
    for i in range(len(rs)):
        data[rs[i]['station']] = rs[i]
    return data

def compute_obs(sts, ets):
    """ Compute the GS values given a start/end time and networks to look at
    """
    sql = """
SELECT
  station, x(geom) as lon, y(geom) as lat,
  sum( case when max_tmpf = -99 THEN 1 ELSE 0 END) as missing,
  sum( gdd50(max_tmpf, min_tmpf) ) as gdd,
  sum( case when pday > 0 THEN pday ELSE 0 END ) as precip
FROM 
  summary_%s
WHERE
  network in ('IA_ASOS','AWOS') and
  day >= '%s' and day < '%s'
GROUP by station, lon, lat
    """ % (sts.year, sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d"))
    rs = access.query(sql).dictresult()
    data = {}
    for i in range(len(rs)):
        data[rs[i]['station']] = rs[i]
    return data

def main():
    output = open('wxc_iem_agdata.txt', 'w')
    output.write("""Weather Central 001d0300 Surface Data
   7
   4 Station
   4 GDD_MAY1
   4 GDD_MAY1_NORM
   5 PRECIP_MAY1
   5 PRECIP_MAY1_NORM
   6 Lat
   8 Lon
""")
    sts =  mx.DateTime.DateTime(2009,5,1)
    ets = mx.DateTime.now()
    days = (ets - sts).days
    data = compute_obs( sts, ets )
    cdata = compute_climate( sts, ets )
    xref = build_xref()
    for id in data.keys():
        if data[id]['missing'] > (days * 0.1):
            continue
        csite = xref[id].lower()
        output.write("K%s %4.0f %4.0f %5.2f %5.2f %6.3f %8.3f\n" % (id, 
        data[id]['gdd'], cdata[ csite ]['cgdd'],
        data[id]['precip'], cdata[ csite ]['crain'],
        data[id]['lat'], data[id]['lon'] ))
    output.close()
    os.system("/home/ldm/bin/pqinsert -p \"wxc_iem_agdata.txt\" wxc_iem_agdata.txt")
    os.remove("wxc_iem_agdata.txt")

if __name__ == '__main__':
    main()
