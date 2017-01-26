"""
 Dump a CSV file of the MADIS data, kind of sad that I do this, but alas
"""

import netCDF4
import mx.DateTime
import re
import os
import numpy.ma
import sys
import time
from pyiem.datatypes import temperature
import subprocess
import warnings
# prevent core.py:931: RuntimeWarning: overflow encountered in multiply
warnings.simplefilter("ignore", RuntimeWarning)
# prevent core.py:3785: UserWarning: Warning: converting a masked element
warnings.simplefilter("ignore", UserWarning)


def sanityCheck(val, lower, upper, goodfmt, bv):
    if (val > lower and val < upper):
        return goodfmt % (val,)
    return bv


# Wow, why did I do it this way... better not change it as I bet the
# other end is ignoring the headers...
fmt = ("STN,DATE,TIME,T,TD,WCI,RH,THI,DIR,SPD,GST,ALT,SLP,VIS,SKY,CEIL,"
       "CLD,SKY,CEIL,CLD,SKY,CEIL,CLD,SKY,CEIL,CLD,SKY,CEIL,CLD,SKY,CEIL,"
       "CLD,SKYSUM,PR6,PR24,WX,MINT6,MAXT6,MINT24,MAXT24,AUTO,PR1,PTMP1,"
       "PTMP2,PTMP3,PTMP4,SUBS1,SUBS2,SUBS3,SUBS4,")
format_tokens = fmt.split(",")

gmt = mx.DateTime.gmt()
fn = "/mesonet/data/madis/mesonet1/%s.nc" % (gmt.strftime("%Y%m%d_%H00"), )
if not os.path.isfile(fn):
    if gmt.minute > 30:
        print '%s does not exist' % (fn,)
    sys.exit()
attempt = 0
nc = None
# Loop in case the file is being written while we attempt to open it
while attempt < 3:
    try:
        nc = netCDF4.Dataset(fn, 'r')
        attempt = 3
    except:
        time.sleep(10)
        attempt += 1
if nc is None:
    print 'Numerous attempts to open MADIS netcdf %s failed!' % (fn,)
    sys.exit(0)

stations = nc.variables["stationId"][:]
tmpf = temperature(nc.variables["temperature"][:], 'K').value('F')
dwpf = temperature(nc.variables["dewpoint"][:], 'K').value('F')
drct = nc.variables["windDir"][:]
smps = nc.variables["windSpeed"][:] * 1.94384449
alti = nc.variables["altimeter"][:] * 29.9196 / 1013.2  # in hPa
vsby = nc.variables["visibility"][:] * 0.000621371192  # in hPa
providers = nc.variables["dataProvider"][:]
lat = nc.variables["latitude"][:]
lon = nc.variables["longitude"][:]
ele = nc.variables["elevation"][:]
p01m = nc.variables["precipAccum"][:] * 25.4
ptmp1 = temperature(nc.variables["roadTemperature1"][:], 'K').value('F')
ptmp2 = temperature(nc.variables["roadTemperature2"][:], 'K').value('F')
ptmp3 = temperature(nc.variables["roadTemperature3"][:], 'K').value('F')
ptmp4 = temperature(nc.variables["roadTemperature4"][:], 'K').value('F')
subs1 = temperature(nc.variables["roadSubsurfaceTemp1"][:], 'K').value('F')
subs2 = temperature(nc.variables["roadSubsurfaceTemp2"][:], 'K').value('F')
subs3 = temperature(nc.variables["roadSubsurfaceTemp3"][:], 'K').value('F')
subs4 = temperature(nc.variables["roadSubsurfaceTemp4"][:], 'K').value('F')
times = nc.variables["observationTime"][:]

db = {}

for recnum in range(len(stations)):
    thisStation = re.sub('\x00', '', stations[recnum].tostring())
    ot = times[recnum]
    if numpy.ma.is_masked(ot) or ot > 2141347600:
        continue
    ts = mx.DateTime.gmtime(times[recnum])
    db[thisStation] = {
        'STN': thisStation,
        'DATE': ts.day,
        'TIME': ts.strftime("%H%M"),
        'T': sanityCheck(tmpf[recnum], -100, 150, '%.0f', ''),
        'DIR': sanityCheck(drct[recnum], -1, 361, '%.0f', ''),
        'TD': sanityCheck(dwpf[recnum], -100, 150, '%.0f', ''),
        'SPD': sanityCheck(smps[recnum], -1, 150, '%.0f', ''),
        'ALT': sanityCheck(alti[recnum], 2000, 4000, '%.0f', ''),
        'VIS': sanityCheck(vsby[recnum], -1, 40, '%.0f', ''),
        'PR1': sanityCheck(p01m[recnum], -0.01, 10, '%.0f', ''),
        'SUBS1': sanityCheck(subs1[recnum], -100, 150, '%.0f', ''),
        'SUBS2': sanityCheck(subs2[recnum], -100, 150, '%.0f', ''),
        'SUBS3': sanityCheck(subs3[recnum], -100, 150, '%.0f', ''),
        'SUBS4': sanityCheck(subs4[recnum], -100, 150, '%.0f', ''),
        'PTMP1': sanityCheck(ptmp1[recnum], -100, 150, '%.0f', ''),
        'PTMP2': sanityCheck(ptmp2[recnum], -100, 150, '%.0f', ''),
        'PTMP3': sanityCheck(ptmp3[recnum], -100, 150, '%.0f', ''),
        'PTMP4': sanityCheck(ptmp4[recnum], -100, 150, '%.0f', '')
    }

out = open('/tmp/madis.csv', 'w')
out.write("%s\n" % (fmt,))
for stid in db.keys():
    for key in format_tokens:
        if key in db[stid]:
            out.write("%s," % (db[stid][key],))
        else:
            out.write(",")
    out.write("\n")

nc.close()
out.close()

pqstr = "data c 000000000000 fn/madis.csv bogus csv"
cmd = "/home/ldm/bin/pqinsert -p '%s' /tmp/madis.csv" % (pqstr,)
subprocess.call(cmd, shell=True)
os.remove("/tmp/madis.csv")
