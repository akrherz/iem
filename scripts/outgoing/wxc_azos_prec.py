# Generate a Weather Central Formatted file of ASOS/AWOS Precip

import mx.DateTime, os, Ngl, numpy, shutil
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

def compute_obs():
    """ Compute the GS values given a start/end time and networks to look at
    """
    sql = """
SELECT
  station, x(geom) as lon, y(geom) as lat,
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
  summary
WHERE
  network in ('IA_ASOS','AWOS') and
  day IN ('TODAY'::date,'YESTERDAY'::date, 'TODAY'::date - '2 days'::interval)
GROUP by station, lon, lat
    """
    rs = access.query(sql).dictresult()
    data = {}
    for i in range(len(rs)):
        data[rs[i]['station']] = rs[i]
    return data

def main():
    output = open('wxc_airport_precip.txt', 'w')
    output.write("""Weather Central 001d0300 Surface Data TimeStamp=%s
   5
   4 Station
   6 TODAY RAIN
   6 DAY2 RAIN
   6 DAY3 RAIN
   6 Lat
   8 Lon
""" % (mx.DateTime.gmt().strftime("%Y.%m.%d.%H%M"),))
    data = compute_obs()
    for id in data.keys():
        output.write("K%s %6.2f %6.2f %6.2f %6.3f, %8.3f\n" % (id, 
        data[id]['p01'], data[id]['p02'], data[id]['p03'],
        data[id]['lat'], data[id]['lon'] ))
    output.close()
    os.system("/home/ldm/bin/pqinsert -p \"wxc_airport_precip.txt\" wxc_airport_precip.txt")
    shutil.copyfile("wxc_airport_precip.txt", "/mesonet/share/pickup/wxc/wxc_airport_precip.txt")
    os.remove("wxc_airport_precip.txt")

if __name__ == '__main__':
    main()
