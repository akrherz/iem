"""Pull in what's available for HFMETAR MADIS data

Run from RUN_10MIN.sh
Run from RUN_40_AFTER.sh for two hours ago
"""
import datetime
import os
import sys
import warnings
from zoneinfo import ZoneInfo

import numpy as np
from metar import Metar
from metpy.units import masked_array, units
from netCDF4 import chartostring
from pyiem.observation import Observation
from pyiem.reference import TRACE_VALUE
from pyiem.util import convert_value, get_dbconn, logger, mm2inch, ncopen
from tqdm import tqdm

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.simplefilter("ignore", RuntimeWarning)
LOG = logger()


def vsbyfmt(val):
    """Tricky formatting of vis"""
    # NB: we aren't dealing with exact round numbers here akrherz/iem#255
    if val == 0:
        return 0
    if val <= 0.07:
        return "1/16"
    if val <= 0.13:
        return "1/8"
    if val <= 0.26:
        return "1/4"
    if val <= 0.38:
        return "3/8"
    if val <= 0.51:
        return "1/2"
    if val <= 1.1:
        return "1"
    if val <= 1.6:
        return "1 1/2"
    if val <= 2.1:
        return "2"
    if val <= 2.6:
        return "2 1/2"
    return int(val)


def process_sky(data, skycs, skyls):
    """Process the sky cover"""
    mtr = ""
    for i, (skyc, skyl) in enumerate(zip(skycs, skyls), start=1):
        if skyc == "":
            continue
        data[f"skyc{i}"] = skyc
        if skyc != "CLR":
            data[f"skyl{i}"] = float(np.round(skyl, 0))  # GH287
            mtr += f"{skyc}{(skyl / 100.):03.0f} "
        else:
            mtr += "CLR "
    return mtr


def process(ncfn):
    """Process this file"""
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()
    xref = {}
    icursor.execute(
        "SELECT id, network from stations where "
        "(network ~* 'ASOS' and country = 'US') or id in ('PGSN')"
    )
    for row in icursor:
        xref[row[0]] = row[1]
    icursor.close()
    nc = ncopen(ncfn)
    data = {}
    for vname in [
        "stationId",
        "observationTime",
        "temperature",
        "dewpoint",
        "altimeter",  # Pa
        "windDir",
        "windSpeed",  # mps
        "windGust",  # mps
        "visibility",  # m
        "precipAccum",
        "presWx",
        "skyCvr",
        "skyCovLayerBase",
        "autoRemark",
        "operatorRemark",
    ]:
        data[vname] = nc.variables[vname][:]
        for qc in ["QCR", "QCD"]:
            vname2 = vname + qc
            if vname2 in nc.variables:
                data[vname2] = nc.variables[vname2][:]
    for vname in ["temperature", "dewpoint"]:
        data[vname + "C"] = convert_value(data[vname], "degK", "degC")
        data[vname] = convert_value(data[vname], "degK", "degF")
    for vname in ["windSpeed", "windGust"]:
        data[vname] = (
            masked_array(data[vname], units("meter / second"))
            .to(units("knots"))
            .magnitude
        )

    data["altimeter"] = convert_value(data["altimeter"], "pascal", "inch_Hg")
    data["skyCovLayerBase"] = convert_value(
        data["skyCovLayerBase"], "meter", "foot"
    )
    data["visibility"] = convert_value(data["visibility"], "meter", "mile")
    data["precipAccum"] = mm2inch(data["precipAccum"])
    stations = chartostring(data["stationId"][:])
    presentwxs = chartostring(data["presWx"][:])
    skycs = chartostring(data["skyCvr"][:])
    autoremarks = chartostring(data["autoRemark"][:])
    opremarks = chartostring(data["operatorRemark"][:])

    def decision(i, fieldname, tolerance):
        """Our decision if we are going to take a HFMETAR value or not"""
        if data[fieldname][i] is np.ma.masked:
            return None
        if data[f"{fieldname}QCR"][i] == 0:
            return data[fieldname][i]
        # Now we have work to do
        departure = np.ma.max(np.ma.abs(data[f"{fieldname}QCD"][i, :]))
        # print("departure: %s tolerance: %s" % (departure, tolerance))
        if departure <= tolerance:
            return data[fieldname][i]
        return None

    for i, sid in tqdm(
        enumerate(stations),
        total=len(stations),
        disable=(not sys.stdout.isatty()),
    ):
        if len(sid) < 3:
            continue
        sid3 = sid[1:] if sid.startswith("K") else sid
        ts = datetime.datetime(1970, 1, 1) + datetime.timedelta(
            seconds=data["observationTime"][i]
        )
        ts = ts.replace(tzinfo=ZoneInfo("UTC"))

        mtr = f"{sid} {ts:%d%H%M}Z AUTO "
        network = xref.get(sid3, "ASOS")
        iem = Observation(sid3, network, ts)

        #  06019G23KT
        val = decision(i, "windDir", 15)
        if val is not None:
            iem.data["drct"] = int(val)
            mtr += f"{iem.data['drct']:03.0f}"
        else:
            mtr += "///"

        val = decision(i, "windSpeed", 10)
        if val is not None:
            iem.data["sknt"] = int(val)
            mtr += f"{iem.data['sknt']:02.0f}"
        else:
            mtr += "//"

        val = decision(i, "windGust", 10)
        if val is not None and val > 0:
            iem.data["gust"] = int(val)
            mtr += f"G{iem.data['gust']:02.0f}"
        mtr += "KT "

        val = decision(i, "visibility", 4)
        if val is not None:
            iem.data["vsby"] = float(val)
            mtr += f"{vsbyfmt(iem.data['vsby'])}SM "

        presentwx = presentwxs[i]
        if presentwx != "":
            # database storage is comma delimited
            iem.data["wxcodes"] = presentwx.split(" ")
            mtr += f"{presentwx} "

        mtr += process_sky(iem.data, skycs[i], data["skyCovLayerBase"][i])

        t = ""
        tgroup = "T"
        val = decision(i, "temperature", 10)
        if val is not None:
            # Recall the pain enabling this
            # iem.data['tmpf'] = float(data['temperature'][i])
            tmpc = float(data["temperatureC"][i])
            tc = tmpc if tmpc > 0 else (0 - tmpc)
            tf = "M" if tmpc < 0 else ""
            t = f"{tf}{tc:02.0f}/"
            tf = "1" if tmpc < 0 else "0"
            tgroup += f"{tf}{(tc * 10.):03.0f}"
        val = decision(i, "dewpoint", 10)
        if t != "" and val is not None:
            # iem.data['dwpf'] = float(data['dewpoint'][i])
            tmpc = float(data["dewpointC"][i])
            tc = tmpc if tmpc > 0 else (0 - tmpc)
            tf = "M" if tmpc < 0 else ""
            t = f"{t}{tf}{tc:02.0f} "
            tf = "1" if tmpc < 0 else "0"
            tgroup += f"{tf}{(tc * 10.):03.0f}"
        if len(t) > 4:
            mtr += t
        val = decision(i, "altimeter", 20)
        if val is not None:
            iem.data["alti"] = float(round(val, 2))
            mtr += f"A{(iem.data['alti'] * 100.0):.0f} "

        mtr += "RMK "
        val = decision(i, "precipAccum", 25)
        if val is not None:
            if val > 0.009:
                iem.data["phour"] = float(round(val, 2))
                mtr += f"P{(iem.data['phour'] * 100.0):04.0f} "
            elif val > 0:
                # Trace
                mtr += "P0000 "
                iem.data["phour"] = TRACE_VALUE

        if tgroup != "T":
            mtr += f"{tgroup} "

        if autoremarks[i] != "" or opremarks[i] != "":
            mtr += f"{autoremarks[i]} {opremarks[i]} "
        mtr += "MADISHF"
        # Eat our own dogfood
        try:
            Metar.Metar(mtr)
            iem.data["raw"] = mtr
        except Exception as exp:
            print(f"dogfooding extract_hfmetar {mtr} resulted in {exp}")
            continue

        for key in iem.data:
            if isinstance(iem.data[key], np.float32):
                print(f"key: {key} type: {type(iem.data[key])}")
        icursor = pgconn.cursor()
        if not iem.save(icursor, force_current_log=True, skip_current=True):
            print(
                f"extract_hfmetar: unknown station? {sid3} {network} {ts}\n"
                f"{mtr}"
            )

        icursor.close()
        pgconn.commit()


def find_fn(argv):
    """Figure out which file to run for"""
    if len(argv) == 5:
        utcnow = datetime.datetime(
            int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4])
        )
        return utcnow.strftime("/mesonet/data/madis/hfmetar/%Y%m%d_%H00.nc")
    utcnow = datetime.datetime.utcnow()
    start = 0 if len(argv) == 1 else int(argv[1])
    for i in range(start, 5):
        ts = utcnow - datetime.timedelta(hours=i)
        for j in range(300, -1, -1):
            fn = ts.strftime(f"/mesonet/data/madis/hfmetar/%Y%m%d_%H00_{j}.nc")
            if os.path.isfile(fn):
                return fn
    LOG.warning("no MADIS HFMETAR file found!")
    sys.exit()


def main(argv):
    """Do Something"""
    fn = find_fn(argv)
    process(fn)


if __name__ == "__main__":
    main(sys.argv)


def test_sky():
    """Test that we get good numbers with sky coverage."""
    res = process_sky(
        {},
        [
            "BRK",
        ],
        [
            7999.9,
        ],
    )
    assert res == "BRK080 "
