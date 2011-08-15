import iemdb
import os
HADS = iemdb.connect('hads')
hcursor = HADS.cursor()
hcursor2 = HADS.cursor()
MESOSITE = iemdb.connect('mesosite')

missing = []
hcursor.execute("""
SELECT distinct nwsli from unknown WHERE network ~* 'DCP'
""")
for row in hcursor:
  missing.append( row[0] )

stations = {}
for line in open('IFLOWSStation.txt'):
  tokens = line.split("|")
  if len(tokens) < 7:
    continue

  stations[tokens[1]] = {
    'name': tokens[2].replace('"', '').replace("'","").title(),
    'state': (tokens[7].split(",")[1]).strip(),
    'lon' : tokens[3],
    'lat' : tokens[4],
    'id': tokens[1]
    }

for miss in missing:
  if not stations.has_key(miss):
    print 'Unknown', miss
    continue
  data = stations[miss]
  sql = "INSERT into stations(id, synop, name, state, country, network, online,\
         geom, plot_name \
         ) VALUES ('%(id)s', 99999, '%(name)s', '%(state)s', 'US', '%(state)s_DCP', 't',\
         'SRID=4326;POINT(%(lon)s %(lat)s)',  '%(name)s')" % data

  mcursor = MESOSITE.cursor()
  try:
    mcursor.execute(sql)
  except:
    mcursor.close()
  MESOSITE.commit()


  cmd = "/mesonet/python/bin/python /mesonet/www/apps/iemwebsite/scripts/util/addSiteMesosite.py %s_DCP %s" % (data['state'], miss)
  os.system(cmd)

  hcursor2.execute("""
  DELETE from unknown where nwsli = %s
  """, (miss,))

HADS.commit()
