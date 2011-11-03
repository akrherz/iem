"""
Extract station data from file and update any new stations we find, please
$Id: $:
"""

import netCDF3
import mx.DateTime
import iemdb
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()

nc = netCDF3.Dataset('/mesonet/data/madis/mesonet/20111103_1800.nc')

stations   = nc.variables["stationId"]
names   = nc.variables["stationName"]
providers  = nc.variables["dataProvider"]
latitudes  = nc.variables["latitude"]
longitudes  = nc.variables["longitude"]
elevations  = nc.variables["elevation"]


MY_PROVIDERS = ["MNDOT", "KSDOT", "WIDOT", "INDOT", "NDDOT",
 "NEDOR", "WYDOT", "OHDOT", "MDDOT", "NHDOT", "WVDOT"]

for recnum in range(len(providers)):
  thisProvider = ''.join(providers[recnum])
  if not thisProvider in MY_PROVIDERS:
    continue
  stid = ''.join(stations[recnum])
  name = (''.join(names[recnum])).replace("'", "")
  network = '%s_RWIS' % (thisProvider[:2],)
  mcursor.execute("""SELECT * from stations where id = %s and network = %s""",
  (stid, network))
  if mcursor.rowcount > 0:
    continue
  print 'Adding network: %s station: %s' % (network, stid)
  sql = """INSERT into stations(id, network, synop, country, plot_name,
   name, state, elevation, online, geom) VALUES ('%s', '%s', 9999, 'US',
   '%s', '%s', '%s', %s, 't', 'SRID=4326;POINT(%s %s)')""" % (stid,
   network, name, name, network[:2], elevations[recnum][0], longitudes[recnum][0],
   latitudes[recnum][0])
  mcursor.execute(sql)
nc.close()
mcursor.close()
MESOSITE.commit()
MESOSITE.close()
