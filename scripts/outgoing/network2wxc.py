"""
 Convert a network within the MADIS mesonet file to WXC format

29 Jan 2021: Still being used :/
"""
import datetime
import os
import sys
import warnings
import subprocess

from netCDF4 import chartostring
from metpy.units import units
from metpy.calc import heat_index, windchill, relative_humidity_from_dewpoint
from pyiem.util import ncopen, utc, convert_value, logger

LOG = logger()
warnings.filterwarnings("ignore", category=DeprecationWarning)


def s(val):
    """Convert to string."""
    try:
        if val.mask:
            return "M"
    except Exception:
        pass
    return "%5.1f" % (convert_value(val, "degK", "degF"),)


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

    utcnow = utc()

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
        % (utcnow.strftime("%Y.%m.%d.%H%M"),)
    )

    fn = None
    for i in range(4):
        now = utcnow - datetime.timedelta(hours=i)
        testfn = now.strftime("/mesonet/data/madis/mesonet1/%Y%m%d_%H00.nc")
        if os.path.isfile(testfn):
            fn = testfn
            break

    if fn is None:
        LOG.debug("No MADIS data found.")
        sys.exit()

    indices = {}
    BOGUS = utc(2000, 1, 1)

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
        ts = utc(1970, 1, 1) + datetime.timedelta(seconds=ticks)

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
            t = units("degK") * nc.variables["temperature"][idx]
            d = units("degK") * nc.variables["dewpoint"][idx]
            rh = relative_humidity_from_dewpoint(t, d)
            heat = "%5.1f" % (
                heat_index(t, rh, mask_undefined=False).to(units("degF")).m,
            )
        drct = s2(nc.variables["windDir"][idx])
        smps = s2(nc.variables["windSpeed"][idx])
        sped = "M"
        if smps != "M":
            sped = "%5.1f" % (nc.variables["windSpeed"][idx] * 2.23694,)

        wcht = "M"
        if tmpf != "M" and sped != "M":
            t = units("degK") * nc.variables["temperature"][idx]
            sped = units("meter / second") * nc.variables["windSpeed"][idx]
            wcht = "%5.1f" % (
                windchill(t, sped, mask_undefined=False).to(units("degF")).m,
            )

        ts = indices[sid]["ts"]

        out.write(
            (
                "%5.5s %25.25s %8.4f %10.4f "
                "%02i %02i %5s %5s %5s %5s %5s %5s\n"
            )
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
    subprocess.call("pqinsert -p '%s' %s" % (pqstr, wxcfn), shell=True)
    os.remove(wxcfn)


if __name__ == "__main__":
    main(sys.argv)
