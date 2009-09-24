# Need something to generate a CSV file for harvey
# Daryl Herzmann 14 Feb 2005

from Scientific.IO import NetCDF
import mx.DateTime, re, shutil, os, sys
from pyIEM import mesonet

def sanityCheck(val, lower, upper, goodfmt, bv):
  if (val > lower and val < upper):
    return goodfmt % (val,)
  return bv


fmt = "STN,DATE,TIME,T,TD,WCI,RH,THI,DIR,SPD,GST,ALT,SLP,VIS,SKY,CEIL,CLD,SKY,CEIL,CLD,SKY,CEIL,CLD,SKY,CEIL,CLD,SKY,CEIL,CLD,SKY,CEIL,CLD,SKYSUM,PR6,PR24,WX,MINT6,MAXT6,MINT24,MAXT24,AUTO,PR1,PTMP1,PTMP2,PTMP3,PTMP4,SUBS1,SUBS2,SUBS3,SUBS4,"
format_tokens = fmt.split(",")

gmt = mx.DateTime.gmt()
fn = "/mesonet/data/madis/mesonet/%s.nc" % (gmt.strftime("%Y%m%d_%H00"),) 
if not os.path.isfile(fn):
  sys.exit()
nc = NetCDF.NetCDFFile(fn, 'r')

stations   = nc.variables["stationId"]
tmpk        = nc.variables["temperature"]
dwpk = nc.variables["dewpoint"]
drct = nc.variables["windDir"]
smps = nc.variables["windSpeed"]
alti = nc.variables["altimeter"] # in hPa
vsby = nc.variables["visibility"] # in hPa
providers  = nc.variables["dataProvider"]
lat        = nc.variables["latitude"]
lon        = nc.variables["longitude"]
ele        = nc.variables["elevation"]
snames     = nc.variables["stationName"]
p01m       = nc.variables["precipAccum"]
ptmp1      = nc.variables["roadTemperature1"]
ptmp2      = nc.variables["roadTemperature2"]
ptmp3      = nc.variables["roadTemperature3"]
ptmp4      = nc.variables["roadTemperature4"]
subs1      = nc.variables["roadSubsurfaceTemp1"]
subs2      = nc.variables["roadSubsurfaceTemp2"]
subs3      = nc.variables["roadSubsurfaceTemp3"]
subs4      = nc.variables["roadSubsurfaceTemp4"]


db = {}
for recnum in range(len(stations)):
  thisStation  = re.sub('\x00', '', stations[recnum].tostring())
  if ( nc.variables["observationTime"][recnum] > 2141347600 ):
    continue
  ts = mx.DateTime.gmtime( nc.variables["observationTime"][recnum] )
  db[thisStation] = {'STN': thisStation,
    'DATE': ts.day,
    'TIME': ts.strftime("%H%M"),
    'T': sanityCheck(mesonet.k2f( tmpk[recnum][0] ),-100, 150, '%.0f', '') ,
    'DIR': sanityCheck(drct[recnum][0],-1,361, '%.0f', '') ,
    'TD': sanityCheck(mesonet.k2f( dwpk[recnum][0] ),-100, 150, '%.0f', '') ,
    'SPD': sanityCheck(smps[recnum][0] * 1.94384449, -1, 150, '%.0f', '') ,
    'ALT': sanityCheck( alti[recnum][0]  * 29.9196 / 1013.2, 2000, 4000, '%.0f',''),
    'VIS': sanityCheck( vsby[recnum][0] * 0.000621371192, -1, 40, '%.0f',''),
    'PR1': sanityCheck( p01m[recnum][0] * 25.4, -0.01, 10, '%.0f',''),
    'SUBS1': sanityCheck(mesonet.k2f( subs1[recnum][0] ),-100, 150, '%.0f', '') ,
    'SUBS2': sanityCheck(mesonet.k2f( subs2[recnum][0] ),-100, 150, '%.0f', '') ,
    'SUBS3': sanityCheck(mesonet.k2f( subs3[recnum][0] ),-100, 150, '%.0f', '') ,
    'SUBS4': sanityCheck(mesonet.k2f( subs4[recnum][0] ),-100, 150, '%.0f', '') ,
    'PTMP1': sanityCheck(mesonet.k2f( ptmp1[recnum][0] ),-100, 150, '%.0f', '') ,
    'PTMP2': sanityCheck(mesonet.k2f( ptmp2[recnum][0] ),-100, 150, '%.0f', '') ,
    'PTMP3': sanityCheck(mesonet.k2f( ptmp3[recnum][0] ),-100, 150, '%.0f', '') ,
    'PTMP4': sanityCheck(mesonet.k2f( ptmp4[recnum][0] ),-100, 150, '%.0f', '') ,
  }
  mylat = lat[recnum][0]
  mylon = lon[recnum][0]
  sname =  re.sub('\x00', '', snames[recnum].tostring())
  thisProvider = re.sub('\x00', '', providers[recnum].tostring())
  elev = ele[recnum][0]
  #print "%s,%s,%s,%s,%s,%s" % (thisStation, sname, thisProvider, mylat, mylon, elev)

out = open('madis.csv', 'w')
out.write("%s\n" % (fmt,) )
for stid in db.keys():
  for key in format_tokens:
    if (db[stid].has_key( key )):
      out.write("%s," % (db[stid][key],)  )
    else:
      out.write(",")
  out.write("\n")

out.close()
shutil.copy("madis.csv", "/mesonet/share/pickup/fn/")
os.remove("madis.csv")
