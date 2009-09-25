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
  (CASE WHEN pday < 0 THEN 0 ELSE pday END) as rain
FROM 
  summary
WHERE
  network in ('IA_ASOS','AWOS') and
  day = 'TODAY'
    """
    rs = access.query(sql).dictresult()
    data = {}
    for i in range(len(rs)):
        data[rs[i]['station']] = rs[i]
    return data

def main():
    output = open('wxc_airport_precip.txt', 'w')
    output.write("""Weather Central 001d0300 Surface Data
   4
   4 Station
   6 TODAY RAIN
   6 Lat
   8 Lon
""")
    data = compute_obs()
    for id in data.keys():
        output.write("K%s %6.2f %6.3f %8.3f\n" % (id, 
        data[id]['rain'], 
        data[id]['lat'], data[id]['lon'] ))
    output.close()
    os.system("/home/ldm/bin/pqinsert -p \"wxc_airport_precip.txt\" wxc_airport_precip.txt")
    shutil.copyfile("wxc_airport_precip.txt", "/mesonet/share/pickup/wxc/wxc_airport_precip.txt")
    os.remove("wxc_airport_precip.txt")

if __name__ == '__main__':
    main()
