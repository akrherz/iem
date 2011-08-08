
import urllib2
from pyIEM import iemdb
import mx.DateTime
i = iemdb.iemdb()
coop = i['coop']
mesosite = i['mesosite']

stmeta = {}

def parse_lonlat( txt ):
  tokens = txt.split()
  lat = float(tokens[0]) + ((float(tokens[1]) + float(tokens[2]) / 60.0) / 60.0)
  lon = float(tokens[3]) - ((float(tokens[4]) + float(tokens[5]) / 60.0) / 60.0)
  return lon, lat

for line in open('COOP.TXT'):
  lon, lat = parse_lonlat( line[149:168] )
  elev = float( line[168:176] )
  name = line[99:129].strip()
  st = line[59:61]
  id = line[:6]
  iemid = "%s%s" % (st, id[2:])

  sql = """INSERT into stations(id, name, state, country, elevation, network, geom)
   VALUES ('%s', '%s', '%s', 'US', %s, '%sCLIMATE', 'SRID=4326;POINT(%s %s)')""" % (
   iemid, name, st, elev, st, lon, lat)
  stmeta["%s%s" % (st, id) ] = sql

for id in stmeta.keys():
  # Go checkout NCDC for data
  fp = "http://cdo.ncdc.noaa.gov/climatenormals/clim84/%s/%s.txt" % (id[:2], id)
  req = urllib2.Request(fp)
  try:
    lines = urllib2.urlopen(req).readlines()
  except:
    print 'Missing %s %s' % (id, fp)
    continue
  if len(lines) < 40:
    continue

  data = {}

  stationid = '%s%s' % (id[:2].lower(), id[4:])
  vars = ['low', 'high', 'blah','blah', 'blah', 'precip']
  pointer = -1
  try:
    for line in lines:
      tokens = line.replace("-99", "  0").strip().split()
      if line[0] in ['-', ' ']:
        continue
      if tokens[0] == "JAN":
        pointer += 1

      ts = mx.DateTime.strptime("%s-01-2001" % (tokens[0],), '%B-%d-%Y')
      days = ((ts + mx.DateTime.RelativeDateTime(months=1)) - ts).days
      for v in range(int(days)):
        ts0 = ts + mx.DateTime.RelativeDateTime(days=v)
        if not data.has_key(ts0):
          data[ts0] = {}
        val = tokens[v+1]
        data[ts0][ vars[pointer] ] = float(val)
    for ts in data.keys():
      sql = "INSERT into ncdc_climate71 (station, valid, high, low, precip) VALUES ('%s', '2000-%s', %s, %s, %s)" % (stationid, ts.strftime("%m-%d"), data[ts]['high'], data[ts]['low'], data[ts]['precip'] / 100.0)
      coop.query(sql)
    print 'Worked %s %s' % (len(data.keys()), stationid,)
  except:
    print 'Fail %s' % (id,)
    continue
  if id[:2] != 'IA':
    try:
      mesosite.query( stmeta[id] )
    except:
      pass
