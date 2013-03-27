"""
 Convert a network within the MADIS mesonet file to WXC format
"""
import netCDF4
import datetime
import pytz
import os
import sys
import mesonet
import subprocess
import shutil

network = sys.argv[1]
wxcfn = sys.argv[2]

utc = datetime.datetime.utcnow()
#utc = datetime.datetime(2013,3,9,22)
utc = utc.replace(tzinfo=pytz.timezone("UTC"))


out = open(wxcfn, 'w')
out.write("""Weather Central 001d0300 Surface Data TimeStamp=%s
   10
   5 Station
   25 Station Name
   8 Lat
   10 Lon
   2 Hour
   2 Minute
   5 Air Temperature F
   5 Dew Point F
   5 Wind Direction deg
   5 Wind Speed mph
""" % (utc.strftime("%Y.%m.%d.%H%M"),))


fn = None
for i in range(4):
    now= utc - datetime.timedelta(hours=i)
    testfn = now.strftime("/mesonet/data/madis/mesonet/%Y%m%d_%H00.nc")
    if os.path.isfile(testfn):
        fn = testfn
        break

if fn is None:
    sys.exit()
    
indices = {}
BOGUS = datetime.datetime(2000,1,1)
BOGUS = BOGUS.replace(tzinfo=pytz.timezone("UTC"))
    
nc = netCDF4.Dataset(fn, 'r')
for i,provider in enumerate(nc.variables["dataProvider"][:]):
    if provider.tostring().replace('\x00','') != network:
        continue
    sid = nc.variables["stationId"][i].tostring().replace('\x00','')
    # We have an ob!
    ticks = nc.variables["observationTime"][i]
    ts = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds = ticks)
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))

    if ts > indices.get(sid, {'ts': BOGUS})['ts']:
        indices[sid] = {'ts': ts, 'idx': i}

def s(val):
    try:
        if val.mask:
            return 'M'
    except:
        pass
    return "%5.1f" % (mesonet.k2f(val),)

for sid in indices:
    idx = indices[sid]['idx']
    name = nc.variables["stationName"][idx].tostring().replace('\x00','')
    latitude = nc.variables['latitude'][idx]
    longitude = nc.variables['longitude'][idx]
    tmpf = s( nc.variables['temperature'][idx] )
    dwpf = s( nc.variables['dewpoint'][idx] )
    drct = s( nc.variables['windDir'][idx])
    smps = s( nc.variables['windSpeed'][idx])
    sped = "M"
    if smps != "M":
        sped = "%5.1f" % (nc.variables['windSpeed'][idx] * 2.23694,)
    ts = indices[sid]['ts']
    
    out.write("%5.5s %25.25s %8.4f %10.4f %02i %02i %5s %5s %5s %5s\n" % (sid, name, latitude,
                                                   longitude, ts.hour,
                                                   ts.minute, tmpf, dwpf,
                                                   drct, sped))
    
nc.close()
out.close()
subprocess.call("/home/ldm/bin/pqinsert -p \"wxc_%s.txt\" %s" % (
                            network.lower(), wxcfn), shell=True)
shutil.copyfile(wxcfn, 
                "/mesonet/share/pickup/wxc/wxc_%s.txt" % (network.lower(),))
os.remove(wxcfn)