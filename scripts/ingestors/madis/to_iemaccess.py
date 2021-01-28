"""Suck in MADIS data into the iemdb"""
import datetime
import os
import sys
import warnings
import subprocess

import numpy as np
import pytz
import psycopg2.extras
from netCDF4 import chartostring
from pyiem.observation import Observation
from pyiem.util import get_dbconn, ncopen, logger, convert_value, mm2inch

LOG = logger()
MY_PROVIDERS = ["KYTC-RWIS", "KYMN", "NEDOR", "MesoWest"]
warnings.filterwarnings("ignore", category=DeprecationWarning)


def find_file():
    """Find the most recent file"""
    fn = None
    for i in range(0, 4):
        ts = datetime.datetime.utcnow() - datetime.timedelta(hours=i)
        testfn = ts.strftime("/mesonet/data/madis/mesonet1/%Y%m%d_%H00.nc")
        if os.path.isfile(testfn):
            LOG.debug("processing %s", testfn)
            fn = testfn
            break

    if fn is None:
        LOG.info("Found no available files to process")
        sys.exit()
    return fn


def sanity_check(val, lower, upper):
    """Simple bounds check"""
    if lower < val < upper:
        return float(val)
    return None


def provider2network(provider, name):
    """ Convert a MADIS network ID to one that I use, here in IEM land"""
    if not provider.endswith("DOT") and provider not in MY_PROVIDERS:
        return None
    if provider == "KYMN":
        return provider
    if provider == "MesoWest":
        # get the network from the last portion of the name
        network = name.split()[-1]
        if network == "VTWAC":
            return network
        if network.endswith("DOT") and len(network) == 5:
            return f"{network[:2]}_RWIS"
        return None

    if len(provider) == 5 or provider in ["KYTC-RWIS", "NEDOR"]:
        if provider[:2] == "IA":
            return None
        return f"{provider[:2]}_RWIS"
    LOG.info("Unsure how to convert %s into a network", provider)
    return None


def build_roadstate_xref(ncvar):
    """Figure out how values map."""
    xref = {}
    for myattr in [x for x in ncvar.ncattrs() if x.startswith("value")]:
        xref[int(myattr.replace("value", ""))] = ncvar.getncattr(myattr)
    return xref


def main():
    """Do Something"""
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    fn = find_file()
    nc = ncopen(fn, timeout=300)

    stations = chartostring(nc.variables["stationId"][:])
    providers = chartostring(nc.variables["dataProvider"][:])
    names = chartostring(nc.variables["stationName"][:])

    tmpk = nc.variables["temperature"][:]
    dwpk = nc.variables["dewpoint"][:]
    relh = nc.variables["relHumidity"][:]

    # Set some data bounds to keep mcalc from complaining
    tmpk = np.where(
        np.ma.logical_or(np.ma.less(tmpk, 200), np.ma.greater(tmpk, 320)),
        np.nan,
        tmpk,
    )
    dwpk = np.where(
        np.ma.logical_or(np.ma.less(dwpk, 200), np.ma.greater(dwpk, 320)),
        np.nan,
        dwpk,
    )
    relh = np.where(
        np.ma.logical_and(np.ma.less(relh, 100.1), np.ma.greater(relh, 0)),
        relh,
        np.nan,
    )
    obtime = nc.variables["observationTime"][:]
    pressure = nc.variables["stationPressure"][:]
    # altimeter = nc.variables["altimeter"][:]
    # slp = nc.variables["seaLevelPressure"][:]
    drct = nc.variables["windDir"][:]
    smps = nc.variables["windSpeed"][:]
    gmps = nc.variables["windGust"][:]
    # gmps_drct = nc.variables["windDirMax"][:]
    pcpn = nc.variables["precipAccum"][:]
    rtk1 = nc.variables["roadTemperature1"][:]
    rtk2 = nc.variables["roadTemperature2"][:]
    rtk3 = nc.variables["roadTemperature3"][:]
    rtk4 = nc.variables["roadTemperature4"][:]
    subk1 = nc.variables["roadSubsurfaceTemp1"][:]
    rstate1 = nc.variables["roadState1"][:]
    road_state_xref = build_roadstate_xref(nc.variables["roadState1"])
    rstate2 = nc.variables["roadState2"][:]
    rstate3 = nc.variables["roadState3"][:]
    rstate4 = nc.variables["roadState4"][:]
    nc.close()

    db = {}

    for recnum, provider in enumerate(providers):
        name = names[recnum]
        network = provider2network(provider, name)
        if network is None:
            continue
        LOG.debug("provider: %s name: %s network: %s", provider, name, network)
        this_station = stations[recnum]
        db[this_station] = {}
        ticks = obtime[recnum]
        ts = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=ticks)
        db[this_station]["ts"] = ts.replace(tzinfo=pytz.utc)
        db[this_station]["network"] = network
        db[this_station]["pres"] = sanity_check(pressure[recnum], 0, 1000000)
        db[this_station]["tmpk"] = sanity_check(tmpk[recnum], 200, 330)
        db[this_station]["dwpk"] = sanity_check(dwpk[recnum], 200, 330)
        db[this_station]["relh"] = sanity_check(relh[recnum], 0, 100.1)
        db[this_station]["drct"] = sanity_check(drct[recnum], -1, 361)
        db[this_station]["smps"] = sanity_check(smps[recnum], -1, 200)
        db[this_station]["gmps"] = sanity_check(gmps[recnum], -1, 200)
        db[this_station]["rtk1"] = sanity_check(rtk1[recnum], 0, 500)
        db[this_station]["rtk2"] = sanity_check(rtk2[recnum], 0, 500)
        db[this_station]["rtk3"] = sanity_check(rtk3[recnum], 0, 500)
        db[this_station]["rtk4"] = sanity_check(rtk4[recnum], 0, 500)
        db[this_station]["subk"] = sanity_check(subk1[recnum], 0, 500)
        db[this_station]["pday"] = sanity_check(pcpn[recnum], -1, 5000)
        if rstate1[recnum] is not np.ma.masked:
            db[this_station]["scond0"] = road_state_xref.get(rstate1[recnum])
        if rstate2[recnum] is not np.ma.masked:
            db[this_station]["scond1"] = road_state_xref.get(rstate2[recnum])
        if rstate3[recnum] is not np.ma.masked:
            db[this_station]["scond2"] = road_state_xref.get(rstate3[recnum])
        if rstate4[recnum] is not np.ma.masked:
            db[this_station]["scond3"] = road_state_xref.get(rstate4[recnum])

    for sid in db:
        iem = Observation(sid, db[sid]["network"], db[sid]["ts"])
        for colname in ["scond0", "scond1", "scond2", "scond3"]:
            iem.data[colname] = db[sid].get(colname)
        if db[sid]["tmpk"] is not None:
            iem.data["tmpf"] = convert_value(db[sid]["tmpk"], "degK", "degF")
        if db[sid]["dwpk"] is not None:
            iem.data["dwpf"] = convert_value(db[sid]["dwpk"], "degK", "degF")
        if db[sid]["relh"] is not None and db[sid]["relh"] is not np.ma.masked:
            iem.data["relh"] = float(db[sid]["relh"])
        if db[sid]["drct"] is not None:
            iem.data["drct"] = db[sid]["drct"]
        if db[sid]["smps"] is not None:
            iem.data["sknt"] = convert_value(
                db[sid]["smps"], "meter / second", "knot"
            )
        if db[sid]["gmps"] is not None:
            iem.data["gust"] = convert_value(
                db[sid]["gmps"], "meter / second", "knot"
            )
        if db[sid]["pres"] is not None:
            iem.data["pres"] = (float(db[sid]["pres"]) / 100.00) * 0.02952
        if db[sid]["rtk1"] is not None:
            iem.data["tsf0"] = convert_value(db[sid]["rtk1"], "degK", "degF")
        if db[sid]["rtk2"] is not None:
            iem.data["tsf1"] = convert_value(db[sid]["rtk2"], "degK", "degF")
        if db[sid]["rtk3"] is not None:
            iem.data["tsf2"] = convert_value(db[sid]["rtk3"], "degK", "degF")
        if db[sid]["rtk4"] is not None:
            iem.data["tsf3"] = convert_value(db[sid]["rtk4"], "degK", "degF")
        if db[sid]["subk"] is not None:
            iem.data["rwis_subf"] = convert_value(
                db[sid]["subk"], "degK", "degF"
            )
        if db[sid]["pday"] is not None:
            iem.data["pday"] = round(mm2inch(db[sid]["pday"]), 2)
        if not iem.save(icursor):
            LOG.info(
                "MADIS Extract: %s found new station: %s network: %s" "",
                fn.split("/")[-1],
                sid,
                db[sid]["network"],
            )
            subprocess.call("python sync_stations.py %s" % (fn,), shell=True)
            os.chdir("../../dbutil")
            subprocess.call("sh SYNC_STATIONS.sh", shell=True)
            os.chdir("../ingestors/madis")
            LOG.info("...done with sync.")
        del iem
    icursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
