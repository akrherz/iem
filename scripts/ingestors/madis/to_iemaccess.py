"""Suck in MADIS data into the iemdb.

Run from RUN_20MIN.sh
RUN_20_AFTER for previous hour
RUN_40_AFTER for 2 hours ago.
"""

import os
import subprocess
import tempfile
import warnings
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import click
import httpx
import numpy as np
from netCDF4 import chartostring
from pyiem.database import get_dbconnc
from pyiem.observation import Observation
from pyiem.util import convert_value, logger, mm2inch, ncopen, utc

LOG = logger()
MYDIR = "/mesonet/data/madis"
MY_PROVIDERS = ["KYTC-RWIS", "NEDOR", "MesoWest", "ITD"]
WEBROOT = "https://madis-data.cprk.ncep.noaa.gov/madisPublic1/data/"
warnings.filterwarnings("ignore", category=DeprecationWarning)


def find_file(variant, valid: datetime):
    """Find the most recent file"""
    fn = None
    if valid < utc().replace(hour=0, minute=0):
        if (utc() - valid).days > 5:
            uri = (
                f"{WEBROOT}archive/{valid:%Y/%m/%d}/LDAD/{variant[:-1]}/netCDF/"
                f"{valid:%Y%m%d_%H}00.gz"
            )
        else:
            uri = f"{WEBROOT}LDAD/{variant[:-1]}/netCDF/{valid:%Y%m%d_%H}00.gz"
        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".gz"
            ) as tmp:
                resp = httpx.get(uri)
                resp.raise_for_status()
                tmp.write(resp.content)
                fn = tmp.name
            # gunzip the file
            subprocess.call(["gunzip", "-f", fn])
            fn = fn[:-3]
            return fn
        except Exception as exp:
            LOG.info("Failed to fetch %s %s", uri, exp)
            return None

    for j in range(300, -1, -1):
        testfn = valid.strftime(f"{MYDIR}/{variant}/%Y%m%d_%H00_{j}.nc")
        if os.path.isfile(testfn):
            LOG.info("processing %s", testfn)
            return testfn
    LOG.warning("Found no %s files to process for %s", variant, valid)
    return None


def sanity_check(val, lower, upper):
    """Simple bounds check"""
    if lower < val < upper:
        return float(val)
    return None


def provider2network(provider, name):
    """Convert a MADIS network ID to one that I use, here in IEM land"""
    if not provider.endswith("DOT") and provider not in MY_PROVIDERS:
        return None
    if provider == "MesoWest":
        # get the network from the last portion of the name
        tokens = name.split()
        if not tokens:
            return None
        network = tokens[-1]
        if network == "NEDOR":
            return "NE_RWIS"
        if network == "VTWAC":
            return network
        # Le Sigh
        if network == "CDOT":
            return "CO_RWIS"
        if network == "ODOT":
            return "OR_RWIS"
        if network.endswith("DOT"):
            if len(network) == 5:
                return f"{network[:2]}_RWIS"
            if tokens[-2] == "UTAH" or len(tokens[-2]) == 2:
                return f"{tokens[-2][:2]}_RWIS"
            LOG.warning("How to convert %s into a network?", repr(tokens))
            return None
        return None
    if provider == "ITD":
        return "ID_RWIS"
    if len(provider) == 5 or provider in ["KYTC-RWIS", "NEDOR"]:
        if provider[:2] == "IA":
            return None
        return f"{provider[:2]}_RWIS"
    LOG.warning("Unsure how to convert %s into a network", provider)
    return None


def build_roadstate_xref(ncvar):
    """Figure out how values map."""
    xref = {}
    for myattr in [x for x in ncvar.ncattrs() if x.startswith("value")]:
        xref[int(myattr.replace("value", ""))] = ncvar.getncattr(myattr)
    return xref


def process(fn: str):
    """Process the MADIS file"""
    pgconn, icursor = get_dbconnc("iem")
    with ncopen(fn, timeout=300) as nc:
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
        drct = nc.variables["windDir"][:]
        smps = nc.variables["windSpeed"][:]
        gmps = nc.variables["windGust"][:]
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
        vsby = convert_value(nc.variables["visibility"][:], "meter", "mile")

    updates = 0
    dirty = False
    for recnum, provider in enumerate(providers):
        name = names[recnum]
        network = provider2network(provider, name)
        sid = stations[recnum]
        if network is None:
            continue
        ticks = obtime[recnum]
        ts = datetime(1970, 1, 1) + timedelta(seconds=ticks)
        ts = ts.replace(tzinfo=ZoneInfo("UTC"))
        iem = Observation(sid, network, ts)

        if rstate1[recnum] is not np.ma.masked:
            iem.data["scond0"] = road_state_xref.get(rstate1[recnum])
        if rstate2[recnum] is not np.ma.masked:
            iem.data["scond1"] = road_state_xref.get(rstate2[recnum])
        if rstate3[recnum] is not np.ma.masked:
            iem.data["scond2"] = road_state_xref.get(rstate3[recnum])
        if rstate4[recnum] is not np.ma.masked:
            iem.data["scond3"] = road_state_xref.get(rstate4[recnum])

        val = sanity_check(tmpk[recnum], 200, 330)
        if val is not None:
            iem.data["tmpf"] = convert_value(val, "degK", "degF")

        val = sanity_check(dwpk[recnum], 200, 330)
        if val is not None:
            iem.data["dwpf"] = convert_value(val, "degK", "degF")

        val = sanity_check(relh[recnum], 0, 100.1)
        if val is not None and val is not np.ma.masked:
            iem.data["relh"] = float(val)

        val = sanity_check(drct[recnum], -1, 361)
        if val is not None:
            iem.data["drct"] = val

        val = sanity_check(smps[recnum], -1, 200)
        if val is not None:
            iem.data["sknt"] = convert_value(val, "meter / second", "knot")

        val = sanity_check(gmps[recnum], -1, 200)
        if val is not None:
            iem.data["gust"] = convert_value(val, "meter / second", "knot")
        pres = sanity_check(pressure[recnum], 0, 1000000)
        if pres is not None:
            iem.data["pres"] = (float(pres) / 100.00) * 0.02952

        val = sanity_check(rtk1[recnum], 0, 500)
        if val is not None:
            iem.data["tsf0"] = convert_value(val, "degK", "degF")

        val = sanity_check(rtk2[recnum], 0, 500)
        if val is not None:
            iem.data["tsf1"] = convert_value(val, "degK", "degF")

        val = sanity_check(rtk3[recnum], 0, 500)
        if val is not None:
            iem.data["tsf2"] = convert_value(val, "degK", "degF")

        val = sanity_check(rtk4[recnum], 0, 500)
        if val is not None:
            iem.data["tsf3"] = convert_value(val, "degK", "degF")

        val = sanity_check(vsby[recnum], 0, 30)
        if val is not None:
            iem.data["vsby"] = val

        subk = sanity_check(subk1[recnum], 0, 500)
        if subk is not None:
            iem.data["rwis_subf"] = convert_value(subk, "degK", "degF")

        pday = sanity_check(pcpn[recnum], -1, 5000)
        if pday is not None:
            iem.data["pday"] = round(mm2inch(pday), 2)
        updates += 1
        # Could be processing previous hour or out-of-order data
        if not iem.save(icursor, force_current_log=True):
            LOG.warning(
                "MADIS Extract: %s found new station: %s network: %s",
                fn.split("/")[-1],
                sid,
                network,
            )
            dirty = True
    if dirty:
        subprocess.call(["python", "sync_stations.py", f"--filename={fn}"])
        os.chdir("../../dbutil")
        subprocess.call(["sh", "SYNC_STATIONS.sh"])

    LOG.info("Found %s/%s updates in %s", updates, len(providers), fn)
    icursor.close()
    pgconn.commit()
    pgconn.close()


@click.command()
@click.option(
    "--valid", required=True, type=click.DateTime(), help="Specific valid time"
)
def main(valid: datetime):
    """Do Something"""
    valid = valid.replace(tzinfo=timezone.utc)
    for variant in ["rwis1", "mesonet1"]:
        fn = find_file(variant, valid)
        if fn is None:
            continue
        process(fn)
        if fn.startswith("/tmp/"):
            os.unlink(fn)


if __name__ == "__main__":
    main()
