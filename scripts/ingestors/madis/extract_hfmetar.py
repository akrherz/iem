"""Pull in what's available for HFMETAR MADIS data

Run from RUN_10MIN.sh
Run from RUN_40_AFTER.sh for two hours ago
"""
from __future__ import print_function
import os
import sys
import datetime
import warnings

import pytz
import numpy as np
from tqdm import tqdm
from metar import Metar
from netCDF4 import chartostring
from metpy.units import units, masked_array
from pyiem.datatypes import temperature, distance, pressure
from pyiem.observation import Observation
from pyiem.util import get_dbconn, ncopen, logger
from pyiem.reference import TRACE_VALUE

warnings.simplefilter("ignore", RuntimeWarning)
LOG = logger()


def vsbyfmt(val):
    """ Tricky formatting of vis"""
    # NB: we aren't dealing with exact round numbers here akrherz/iem#255
    if val == 0:
        return 0
    if val <= 0.07:
        LOG.debug("found 1/16 mile vis %s", val)
        return "1/16"
    if val <= 0.13:
        LOG.debug("found 1/8 mile vis %s", val)
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


def process(ncfn):
    """Process this file """
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()
    xref = {}
    icursor.execute(
        """
        SELECT id, network from stations where
        network ~* 'ASOS' or network = 'AWOS' and country = 'US'
    """
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
        data[vname + "C"] = temperature(data[vname], "K").value("C")
        data[vname] = temperature(data[vname], "K").value("F")
    for vname in ["windSpeed", "windGust"]:
        data[vname] = (
            masked_array(data[vname], units("meter / second"))
            .to(units("knots"))
            .magnitude
        )

    data["altimeter"] = pressure(data["altimeter"], "PA").value("IN")
    data["skyCovLayerBase"] = distance(data["skyCovLayerBase"], "M").value(
        "FT"
    )
    data["visibility"] = distance(data["visibility"], "M").value("MI")
    data["precipAccum"] = distance(data["precipAccum"], "MM").value("IN")
    stations = chartostring(data["stationId"][:])
    presentwxs = chartostring(data["presWx"][:])
    skycs = chartostring(data["skyCvr"][:])
    autoremarks = chartostring(data["autoRemark"][:])
    opremarks = chartostring(data["operatorRemark"][:])

    def decision(i, fieldname, tolerance):
        """Our decision if we are going to take a HFMETAR value or not"""
        if data[fieldname][i] is np.ma.masked:
            return None
        if data["%sQCR" % (fieldname,)][i] == 0:
            return data[fieldname][i]
        # Now we have work to do
        departure = np.ma.max(np.ma.abs(data["%sQCD" % (fieldname,)][i, :]))
        # print("departure: %s tolerance: %s" % (departure, tolerance))
        if departure <= tolerance:
            return data[fieldname][i]
        return None

    for i, sid in tqdm(
        enumerate(stations),
        total=len(stations),
        disable=(not sys.stdout.isatty()),
    ):
        sid3 = sid[1:] if sid[0] == "K" else sid
        ts = datetime.datetime(1970, 1, 1) + datetime.timedelta(
            seconds=data["observationTime"][i]
        )
        ts = ts.replace(tzinfo=pytz.UTC)

        mtr = "%s %sZ AUTO " % (sid, ts.strftime("%d%H%M"))
        network = xref.get(sid3, "ASOS")
        iem = Observation(sid3, network, ts)

        #  06019G23KT
        val = decision(i, "windDir", 15)
        if val is not None:
            iem.data["drct"] = int(val)
            mtr += "%03i" % (iem.data["drct"],)
        else:
            mtr += "///"

        val = decision(i, "windSpeed", 10)
        if val is not None:
            iem.data["sknt"] = int(val)
            mtr += "%02i" % (iem.data["sknt"],)
        else:
            mtr += "//"

        val = decision(i, "windGust", 10)
        if val is not None and val > 0:
            iem.data["gust"] = int(val)
            mtr += "G%02i" % (iem.data["gust"],)
        mtr += "KT "

        val = decision(i, "visibility", 4)
        if val is not None:
            iem.data["vsby"] = float(val)
            mtr += "%sSM " % (vsbyfmt(iem.data["vsby"]),)

        presentwx = presentwxs[i]
        if presentwx != "":
            # database storage is comma delimited
            iem.data["wxcodes"] = presentwx.split(" ")
            mtr += "%s " % (presentwx,)

        for _i, (skyc, _l) in enumerate(
            zip(skycs[i], data["skyCovLayerBase"][i])
        ):
            if skyc != "":
                iem.data["skyc%s" % (_i + 1,)] = skyc
                if skyc != "CLR":
                    iem.data["skyl%s" % (_i + 1,)] = int(_l)
                    mtr += "%s%03i " % (skyc, int(_l) / 100)
                else:
                    mtr += "CLR "

        t = ""
        tgroup = "T"
        val = decision(i, "temperature", 10)
        if val is not None:
            # Recall the pain enabling this
            # iem.data['tmpf'] = float(data['temperature'][i])
            tmpc = float(data["temperatureC"][i])
            t = "%s%02i/" % (
                "M" if tmpc < 0 else "",
                tmpc if tmpc > 0 else (0 - tmpc),
            )
            tgroup += "%s%03i" % (
                "1" if tmpc < 0 else "0",
                (tmpc if tmpc > 0 else (0 - tmpc)) * 10.0,
            )
        val = decision(i, "dewpoint", 10)
        if val is not None:
            # iem.data['dwpf'] = float(data['dewpoint'][i])
            tmpc = float(data["dewpointC"][i])
            if t != "":
                t = "%s%s%02i " % (
                    t,
                    "M" if tmpc < 0 else "",
                    tmpc if tmpc > 0 else 0 - tmpc,
                )
                tgroup += "%s%03i" % (
                    "1" if tmpc < 0 else "0",
                    (tmpc if tmpc > 0 else (0 - tmpc)) * 10.0,
                )
        if len(t) > 4:
            mtr += t
        val = decision(i, "altimeter", 20)
        if val is not None:
            iem.data["alti"] = float(round(val, 2))
            mtr += "A%4i " % (iem.data["alti"] * 100.0,)

        mtr += "RMK "
        val = decision(i, "precipAccum", 25)
        if val is not None:
            if val >= 0.01:
                iem.data["phour"] = float(round(val, 2))
                mtr += "P%04i " % (iem.data["phour"] * 100.0,)
            elif val > 0:
                # Trace
                mtr += "P0000 "
                iem.data["phour"] = TRACE_VALUE

        if tgroup != "T":
            mtr += "%s " % (tgroup,)

        if autoremarks[i] != "" or opremarks[i] != "":
            mtr += "%s %s " % (autoremarks[i], opremarks[i])
        mtr += "MADISHF"
        # Eat our own dogfood
        try:
            Metar.Metar(mtr)
            iem.data["raw"] = mtr
        except Exception as exp:
            print("dogfooding extract_hfmetar %s resulted in %s" % (mtr, exp))
            continue

        for key in iem.data:
            if isinstance(iem.data[key], np.float32):
                print("key: %s type: %s" % (key, type(iem.data[key])))
        icursor = pgconn.cursor()
        if not iem.save(icursor, force_current_log=True, skip_current=True):
            print(
                ("extract_hfmetar: unknown station? %s %s %s\n%s")
                % (sid3, network, ts, mtr)
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
    else:
        utcnow = datetime.datetime.utcnow()
        start = 0 if len(argv) == 1 else int(argv[1])
        for i in range(start, 5):
            ts = utcnow - datetime.timedelta(hours=i)
            fn = ts.strftime("/mesonet/data/madis/hfmetar/%Y%m%d_%H00.nc")
            if os.path.isfile(fn):
                return fn
        sys.exit()


def main(argv):
    """Do Something"""
    fn = find_fn(argv)
    process(fn)


if __name__ == "__main__":
    main(sys.argv)
