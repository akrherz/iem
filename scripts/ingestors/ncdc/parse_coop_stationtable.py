# 
import sys
from pyIEM import iemdb
i = iemdb.iemdb()
mesosite = i['mesosite']
mesosite.query("BEGIN;")
ST = sys.argv[1]

def toLALO2( s ):
  tokens = s.split(":")
  return float(tokens[0]) - (float(tokens[1])/60.0)
def toLALO( s ):
  s = s.strip()
  return float(s[:2]) + (float("%s%s" % (s[2],s[4]))/60.0)

o = open('%s_stn.txt' % (ST,), 'r')
for line in o:
  name = line[17:48].strip()
  stid = "%s%s" %(ST, line[2:6])
  tokens = line[48:].split()
  elev = tokens[-1]
  lon = toLALO2( tokens[-2] )
  lat = toLALO( tokens[-3] )
  sql = """SELECT * from stations where id = '%s' and network = '%sCLIMATE'
        """ % (stid, ST)
  rows = mesosite.query( sql ).dictresult()
  if len(rows) == 0:
    sql = """INSERT into stations (id, network, geom, state, plot_name,
        elevation, country, online) VALUES ('%s', '%sCLIMATE', 
        'SRID=4326;POINT(%s %s)', '%s', '%s', %s, 'US','t')""" % (stid, ST,
        lon, lat, ST, name, elev)
    print 'Adding ID: %s %6.2f %6.2f' % (stid,lon, lat)
    mesosite.query( sql )

mesosite.query("COMMIT;")
