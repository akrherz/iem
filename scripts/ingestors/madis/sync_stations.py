"""
Extract station data from file and update any new stations we find, please

"""

import netCDF4
import mx.DateTime
import iemdb
import os
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()

fp = None
for i in range(0,9):
  ts = mx.DateTime.gmt() - mx.DateTime.RelativeDateTime(hours=i)
  testfp = ts.strftime("/mesonet/data/madis/mesonet/%Y%m%d_%H00.nc")
  if os.path.isfile(testfp):
    fp = testfp
    break

if fp is None:
  sys.exit()

nc = netCDF4.Dataset(fp)


stations   = nc.variables["stationId"]
names   = nc.variables["stationName"]
providers  = nc.variables["dataProvider"]
latitudes  = nc.variables["latitude"]
longitudes  = nc.variables["longitude"]
elevations  = nc.variables["elevation"]


MY_PROVIDERS = ["MNDOT", "KSDOT", "WIDOT", "INDOT", "NDDOT",
 "NEDOR", "WYDOT", "OHDOT", "MDDOT", "NHDOT", "WVDOT", "NVDOT",
 "AKDOT", "VTDOT", "WIDOT", "MEDOT", "VADOT","CODOT", "FLDOT",
 "GADOT", "KYTC-RWIS"]


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
