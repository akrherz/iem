"""
 Dump a CSV file of the MADIS data, kind of sad that I do this, but alas
"""
from __future__ import print_function
import os
import sys
import subprocess
import warnings
import datetime

from netCDF4 import chartostring  # @UnresolvedImport
import numpy.ma
import pytz
from pyiem.util import ncopen
from pyiem.datatypes import temperature
# prevent core.py:931: RuntimeWarning: overflow encountered in multiply
warnings.simplefilter("ignore", RuntimeWarning)
# prevent core.py:3785: UserWarning: Warning: converting a masked element
warnings.simplefilter("ignore", UserWarning)


def sanity_check(val, lower, upper, goodfmt, default):
    """Simple formatter"""
    if lower < val < upper:
        return goodfmt % (val,)
    return default


def main():
    """Go main"""
    # Wow, why did I do it this way... better not change it as I bet the
    # other end is ignoring the headers...
    fmt = ("LAT,LONG,STN,DATE,TIME,T,TD,WCI,RH,THI,DIR,SPD,GST,ALT,SLP,VIS,"
           "SKY,CEIL,CLD,SKYSUM,PR6,PR24,WX,MINT6,MAXT6,MINT24,MAXT24,AUTO,"
           "PR1,PTMP1,PTMP2,PTMP3,PTMP4,SUBS1,SUBS2,SUBS3,SUBS4,STATIONNAME,")
    format_tokens = fmt.split(",")

    utc = datetime.datetime.utcnow()
    fn = "/mesonet/data/madis/mesonet1/%s.nc" % (utc.strftime("%Y%m%d_%H00"), )
    if not os.path.isfile(fn):
        if utc.minute > 30:
            print('madis2csv %s does not exist' % (fn,))
        sys.exit()
    nc = ncopen(fn, 'r', timeout=300)
    if nc is None:
        print(("madis2csv Numerous attempts to open MADIS netcdf %s failed!"
               ) % (fn,))
        sys.exit(0)

    stations = chartostring(nc.variables["stationId"][:])
    stationname = chartostring(nc.variables["stationName"][:])
    tmpf = temperature(nc.variables["temperature"][:], 'K').value('F')
    dwpf = temperature(nc.variables["dewpoint"][:], 'K').value('F')
    drct = nc.variables["windDir"][:]
    smps = nc.variables["windSpeed"][:] * 1.94384449
    alti = nc.variables["altimeter"][:] * 29.9196 / 1013.2  # in hPa
    vsby = nc.variables["visibility"][:] * 0.000621371192  # in hPa
    providers = chartostring(nc.variables["dataProvider"][:])
    lat = nc.variables["latitude"][:]
    lon = nc.variables["longitude"][:]
    # ele = nc.variables["elevation"][:]
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
    nc.close()

    db = {}

    for recnum in range(len(stations)-1, -1, -1):
        station = stations[recnum]
        if station in db:
            continue
        ot = times[recnum]
        if numpy.ma.is_masked(ot) or ot > 2141347600:
            continue
        ts = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=ot)
        ts = ts.replace(tzinfo=pytz.UTC)
        db[station] = {
            'STN': station,
            'PROVIDER': providers[recnum],
            'LAT': lat[recnum],
            'LONG': lon[recnum],
            'STATIONNAME': stationname[recnum].replace(",", " "),
            'DATE': ts.day,
            'TIME': ts.strftime("%H%M"),
            'T': sanity_check(tmpf[recnum], -100, 150, '%.0f', ''),
            'DIR': sanity_check(drct[recnum], -1, 361, '%.0f', ''),
            'TD': sanity_check(dwpf[recnum], -100, 150, '%.0f', ''),
            'SPD': sanity_check(smps[recnum], -1, 150, '%.0f', ''),
            'ALT': sanity_check(alti[recnum], 2000, 4000, '%.0f', ''),
            'VIS': sanity_check(vsby[recnum], -1, 40, '%.0f', ''),
            'PR1': sanity_check(p01m[recnum], -0.01, 10, '%.0f', ''),
            'SUBS1': sanity_check(subs1[recnum], -100, 150, '%.0f', ''),
            'SUBS2': sanity_check(subs2[recnum], -100, 150, '%.0f', ''),
            'SUBS3': sanity_check(subs3[recnum], -100, 150, '%.0f', ''),
            'SUBS4': sanity_check(subs4[recnum], -100, 150, '%.0f', ''),
            'PTMP1': sanity_check(ptmp1[recnum], -100, 150, '%.0f', ''),
            'PTMP2': sanity_check(ptmp2[recnum], -100, 150, '%.0f', ''),
            'PTMP3': sanity_check(ptmp3[recnum], -100, 150, '%.0f', ''),
            'PTMP4': sanity_check(ptmp4[recnum], -100, 150, '%.0f', '')
        }

    out = open('/tmp/madis.csv', 'w')
    out.write("%s\n" % (fmt,))
    for stid in db:
        for key in format_tokens:
            if key in db[stid]:
                out.write("%s" % (db[stid][key],))
            out.write(",")
        out.write("\n")
    out.close()

    pqstr = "data c %s fn/madis.csv bogus csv" % (utc.strftime("%Y%m%d%H%M"),)
    cmd = "/home/ldm/bin/pqinsert -i -p '%s' /tmp/madis.csv" % (pqstr,)
    subprocess.call(cmd, shell=True)
    os.remove("/tmp/madis.csv")

    out = open('/tmp/madis.csv', 'w')
    out.write("%s\n" % (fmt,))
    for stid in db:
        if db[stid]['PROVIDER'] in ['IADOT', 'NEDOR']:
            for key in format_tokens:
                if key in db[stid]:
                    out.write("%s" % (db[stid][key],))
                out.write(",")
            out.write("\n")
    out.close()

    pqstr = "data c %s fn/madis_iamn.csv bogus csv" % (
        utc.strftime("%Y%m%d%H%M"),)
    cmd = "/home/ldm/bin/pqinsert -i -p '%s' /tmp/madis.csv" % (pqstr,)
    subprocess.call(cmd, shell=True)
    os.remove("/tmp/madis.csv")


if __name__ == '__main__':
    main()
