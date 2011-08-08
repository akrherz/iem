# 

from pyIEM import iemdb
i = iemdb.iemdb()
mesosite = i['mesosite']
mesosite.query("BEGIN;")

def toLALO( s ):
  tokens = s.split(":")
  return float(tokens[0]) + (float(tokens[1])/60.0)
def toLALO2( s ):
  tokens = s.split(":")
  return float(tokens[0]) - (float(tokens[1])/60.0)

o = open('5321234136207stn.txt', 'r')
for line in o:
  name = line[17:48].strip()
  stid = "ms"+ line[2:6]
  tokens = line[48:].split()
  elev = tokens[-1]
  lon = toLALO2( tokens[-2] )
  lat = toLALO( tokens[-3] )
  sql = """INSERT into stations (id, network, geom, state, plot_name,
        elevation, country, online) VALUES ('%s', 'MSCLIMATE', 
        'SRID=4326;POINT(%s %s)', 'MS', '%s', %s, 'US','t')""" % (stid,
        lon, lat, name, elev)
  print stid
  mesosite.query( sql )

mesosite.query("COMMIT;")
