
from Scientific.IO.NetCDF import *
import string, re, mx.DateTime, os, sys
from pyIEM import iemAccess, iemAccessOb, mesonet
iemaccess = iemAccess.iemAccess()


files = os.listdir("/mesonet/data/madis/mesonet/")
files.sort()
 
if  (files[-1][-2:] == "gz"):
  sys.exit()
nc = NetCDFFile("/mesonet/data/madis/mesonet/"+ files[-1])

def sanityCheck(val, lower, upper, rt):
  if (val > lower and val < upper):
    return val
  return rt

stations   = nc.variables["stationId"]
providers  = nc.variables["dataProvider"]
tmpk        = nc.variables["temperature"]
tmpk_dd     = nc.variables["temperatureDD"]
obTime      = nc.variables["observationTime"]
pressure    = nc.variables["stationPressure"]
altimeter   = nc.variables["altimeter"]
slp         = nc.variables["seaLevelPressure"]
dwpk        = nc.variables["dewpoint"]
drct        = nc.variables["windDir"]
smps        = nc.variables["windSpeed"]
gmps        = nc.variables["windGust"]
gmps_drct   = nc.variables["windDirMax"]
pcpn        = nc.variables["precipAccum"]
rtk1        = nc.variables["roadTemperature1"]
rtk2        = nc.variables["roadTemperature2"]
rtk3        = nc.variables["roadTemperature3"]
rtk4        = nc.variables["roadTemperature4"]
subk1       = nc.variables["roadSubsurfaceTemp1"]

db = {}

for recnum in range(len(providers)):
  thisProvider = re.sub('\x00', '', providers[recnum].tostring())
  thisStation  = re.sub('\x00', '', stations[recnum].tostring())
  if (thisProvider == "MNDOT" or thisProvider == "KSDOT" or thisProvider == "RAWS" or thisProvider == "WIDOT" or thisProvider == "INDOT" or thisProvider == "NDDOT" or thisProvider == "NEDOR" or thisProvider == "GLDNWS" or thisProvider == "WYDOT" or thisProvider == "OHDOT" or thisProvider == "MDDOT" or thisProvider == "NHDOT"):
    db[thisStation] = {}
    ticks = obTime[recnum]
    ts = mx.DateTime.gmtime(ticks)
    db[thisStation]['ts'] = ts
    db[thisStation]['pres'] = sanityCheck(pressure[recnum][0], 0, 1000000, -99)
    db[thisStation]['tmpk'] = sanityCheck(tmpk[recnum][0], 0, 500, -99)
    db[thisStation]['dwpk'] = sanityCheck(dwpk[recnum][0], 0, 500, -99)
    db[thisStation]['tmpk_dd'] = tmpk_dd[recnum][0]
    db[thisStation]['drct'] = sanityCheck(drct[recnum][0], -1, 361, -99)
    db[thisStation]['smps'] = sanityCheck(smps[recnum][0], -1, 200, -99)
    db[thisStation]['gmps'] = sanityCheck(gmps[recnum][0], -1, 200, -99)
    db[thisStation]['rtk1'] = sanityCheck(rtk1[recnum][0], 0, 500, -99)
    db[thisStation]['rtk2'] = sanityCheck(rtk2[recnum][0], 0, 500, -99)
    db[thisStation]['rtk3'] = sanityCheck(rtk3[recnum][0], 0, 500, -99)
    db[thisStation]['rtk4'] = sanityCheck(rtk4[recnum][0], 0, 500, -99)
    db[thisStation]['subk'] = sanityCheck(subk1[recnum][0],0,500,-99)
    db[thisStation]['pday'] = sanityCheck(pcpn[recnum][0],-1,5000,-99)

for sid in db.keys():
  iem = iemAccessOb.iemAccessOb(sid)
  iem.setObTimeGMT( db[sid]['ts'] )
  iem.data['tmpf'] = mesonet.k2f( db[sid]['tmpk'] )
  iem.data['dwpf'] = mesonet.k2f( db[sid]['dwpk'] )
  if (db[sid]['drct'] >= 0):
    iem.data['drct'] = db[sid]['drct']
  if (db[sid]['smps'] >= 0):
    iem.data['sknt'] = db[sid]['smps'] * (1/0.5148)
  if (db[sid]['gmps'] >= 0):
    iem.data['gust'] = db[sid]['gmps'] * (1/0.5148)
  if (db[sid]['pres'] > 0):
    iem.data['pres'] = (float(db[sid]['pres']) / 100.00 ) * 0.02952
  if (db[sid]['rtk1'] > 0):
    iem.data['tsf0'] = mesonet.k2f( db[sid]['rtk1'] )
  if (db[sid]['rtk2'] > 0):
    iem.data['tsf1'] = mesonet.k2f( db[sid]['rtk2'] )
  if (db[sid]['rtk3'] > 0):
    iem.data['tsf2'] = mesonet.k2f( db[sid]['rtk3'] )
  if (db[sid]['rtk4'] > 0):
    iem.data['tsf3'] = mesonet.k2f( db[sid]['rtk4'] )
  if (db[sid]['subk'] > 0):
    iem.data['rwis_subf'] = mesonet.k2f( db[sid]['subk'] )
  if (db[sid]['pday'] >= 0):
    iem.data['pday'] = float(db[sid]['pday']) * (1.00/25.4)
  iem.updateDatabase(iemaccess.iemdb)
  del(iem)
