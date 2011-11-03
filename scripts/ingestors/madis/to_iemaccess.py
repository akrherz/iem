"""
Suck in MADIS data into the iemdb
$Id: $:
"""
import netCDF3
import string, re, mx.DateTime, os, sys
import access
import iemdb
import mesonet
IEM = iemdb.connect('iem')
icursor = IEM.cursor()

fp = None
for i in range(0,4):
  ts = mx.DateTime.gmt() - mx.DateTime.RelativeDateTime(hours=i)
  testfp = ts.strftime("/mesonet/data/madis/mesonet/%Y%m%d_%H00.nc")
  if os.path.isfile(testfp):
    fp = testfp
    break

if fp is None:
  sys.exit()

nc = netCDF3.Dataset(fp)

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

MY_PROVIDERS = ["MNDOT", "KSDOT", "WIDOT", "INDOT", "NDDOT",
 "NEDOR", "WYDOT", "OHDOT", "MDDOT", "NHDOT", "WVDOT"]

def provider2network(p):
  return '%s_RWIS' % (p[:2],)

for recnum in range(len(providers)):
  thisProvider = ''.join( providers[recnum] )
  thisStation  = ''.join( stations[recnum] )
  if not thisProvider in MY_PROVIDERS:
    continue
  db[thisStation] = {}
  ticks = obTime[recnum]
  ts = mx.DateTime.gmtime(ticks)
  db[thisStation]['ts'] = ts
  db[thisStation]['network'] = provider2network(thisProvider)
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
  iem = access.Ob(sid, db[sid]['network'], icursor)
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
  iem.updateDatabase()
  del(iem)

nc.close()
icursor.close()
IEM.commit()
IEM.close()
