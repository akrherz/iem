"""
 Convert a network within the MADIS mesonet file to WXC format
"""
from __future__ import print_function
import datetime
import os
import sys
import subprocess

from netCDF4 import chartostring
import pytz
from pyiem.datatypes import temperature, speed
from pyiem import meteorology
from pyiem.util import ncopen


def s(val):
    """Convert to string."""
    try:
        if val.mask:
            return "M"
    except Exception:
        pass
    return "%5.1f" % (temperature(val, "K").value("F"),)


def s2(val):
    """Convert to string."""
    try:
        if val.mask:
            return "M"
    except Exception:
        pass
    return "%5.1f" % (val,)


def main(argv):
    """Go Main Go"""
    network = argv[1]
    wxcfn = argv[2]

    utc = datetime.datetime.utcnow()
    utc = utc.replace(tzinfo=pytz.UTC)

    out = open(wxcfn, "w")
    out.write(
        """Weather Central 001d0300 Surface Data TimeStamp=%s
   12
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
   5 Heat Index F
   5 Wind Chill F
"""
        % (utc.strftime("%Y.%m.%d.%H%M"),)
    )

    fn = None
    for i in range(4):
        now = utc - datetime.timedelta(hours=i)
        testfn = now.strftime("/mesonet/data/madis/mesonet1/%Y%m%d_%H00.nc")
        if os.path.isfile(testfn):
            fn = testfn
            break

    if fn is None:
        sys.exit()

    indices = {}
    BOGUS = datetime.datetime(2000, 1, 1)
    BOGUS = BOGUS.replace(tzinfo=pytz.UTC)

    nc = ncopen(fn)

    providers = chartostring(nc.variables["dataProvider"][:])
    stations = chartostring(nc.variables["stationId"][:])
    names = chartostring(nc.variables["stationName"][:])
    for i, provider in enumerate(providers):
        if provider != network:
            continue
        sid = stations[i]
        # We have an ob!
        ticks = int(nc.variables["observationTime"][i])
        ts = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=ticks)
        ts = ts.replace(tzinfo=pytz.UTC)

        if ts > indices.get(sid, {"ts": BOGUS})["ts"]:
            indices[sid] = {"ts": ts, "idx": i}

    for sid in indices:
        idx = indices[sid]["idx"]
        name = names[idx]
        latitude = nc.variables["latitude"][idx]
        longitude = nc.variables["longitude"][idx]
        tmpf = s(nc.variables["temperature"][idx])
        dwpf = s(nc.variables["dewpoint"][idx])
        qcd = nc.variables["temperatureQCD"][idx][0]
        if qcd < -10 or qcd > 10:
            tmpf = "M"
            dwpf = "M"
        heat = "M"
        if tmpf != "M" and dwpf != "M":
            t = temperature(nc.variables["temperature"][idx], "K")
            d = temperature(nc.variables["dewpoint"][idx], "K")
            # relh = meteorology.relh(t, d).value("%")
            heat = "%5.1f" % (meteorology.heatindex(t, d).value("F"),)
        drct = s2(nc.variables["windDir"][idx])
        smps = s2(nc.variables["windSpeed"][idx])
        sped = "M"
        if smps != "M":
            sped = "%5.1f" % (nc.variables["windSpeed"][idx] * 2.23694,)

        wcht = "M"
        if tmpf != "M" and sped != "M":
            t = temperature(nc.variables["temperature"][idx], "K")
            sped = speed(nc.variables["windSpeed"][idx], "MPS")
            wcht = "%5.1f" % (meteorology.windchill(t, sped).value("F"),)

        ts = indices[sid]["ts"]

        out.write(
            ("%5.5s %25.25s %8.4f %10.4f " "%02i %02i %5s %5s %5s %5s %5s %5s\n")
            % (
                sid,
                name,
                latitude,
                longitude,
                ts.hour,
                ts.minute,
                tmpf,
                dwpf,
                drct,
                sped,
                heat,
                wcht,
            )
        )

    nc.close()
    out.close()
    pqstr = "data c 000000000000 wxc/wxc_%s.txt bogus txt" % (network.lower(),)
    subprocess.call("/home/ldm/bin/pqinsert -p '%s' %s" % (pqstr, wxcfn), shell=True)
    os.remove(wxcfn)


if __name__ == "__main__":
    main(sys.argv)
