"""Extract data from gridded NDFD, seven days of data

Total precipitation
Maximum temperature
Minimum temperature

Attempt to derive climodat data from the NDFD database, we will use the 00 UTC
files.

Run from RUN_10_AFTER.sh at 1z
"""

import datetime

import click
import numpy as np
import pygrib
import pyproj
from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.util import archive_fetch, convert_value, logger, utc

LOG = logger()
nt = NetworkTable("IACLIMATE")


def do_precip(gribs, ftime, data):
    """Precip"""
    try:
        sel = gribs.select(parameterName="Total precipitation")
    except Exception:
        LOG.info("No precip found at %s", ftime)
        return
    if data["x"] is None:
        data["proj"] = pyproj.Proj(sel[0].projparams)
        llcrnrx, llcrnry = data["proj"](
            sel[0]["longitudeOfFirstGridPointInDegrees"],
            sel[0]["latitudeOfFirstGridPointInDegrees"],
        )
        nx = sel[0]["Nx"]
        ny = sel[0]["Ny"]
        dx = sel[0]["DxInMetres"]
        dy = sel[0]["DyInMetres"]
        data["x"] = llcrnrx + dx * np.arange(nx)
        data["y"] = llcrnry + dy * np.arange(ny)
    cst = ftime - datetime.timedelta(hours=6)
    key = cst.strftime("%Y-%m-%d")
    d = data["fx"].setdefault(key, dict(precip=None, high=None, low=None))
    LOG.info("Writting precip %s from ftime: %s", key, ftime)
    if d["precip"] is None:
        d["precip"] = sel[0].values
    else:
        d["precip"] += sel[0].values


def do_temp(name, dkey, gribs, ftime, data):
    """Temp"""
    try:
        sel = gribs.select(parameterName=name)
    except Exception:
        return
    cst = ftime - datetime.timedelta(hours=6)
    key = cst.strftime("%Y-%m-%d")
    d = data["fx"].setdefault(key, dict(precip=None, high=None, low=None))
    LOG.info("Writting %s %s from ftime: %s", name, key, ftime)
    d[dkey] = convert_value(sel[0].values, "degK", "degF")


def process(ts):
    """Do Work"""
    data = {"x": None, "y": None, "proj": None, "fx": {}}
    # Only have data out 168 hours
    for fhour in range(1, 169):
        # Hourly data only goes out 36 hours
        if (36 < fhour < 72) and fhour % 3 != 0:
            continue
        if fhour > 72 and fhour % 6 != 0:
            continue
        ftime = ts + datetime.timedelta(hours=fhour)
        ppath = (
            f"{ts:%Y/%m/%d}/model/ndfd/{ts:%H}/"
            f"ndfd.t{ts:%H}z.awp2p5f{fhour:03.0f}.grib2"
        )
        with archive_fetch(ppath) as fn:
            if fn is None:
                LOG.warning("missing: %s", ppath)
                continue
            LOG.info("-> %s", fn)
            gribs = pygrib.open(fn)
            do_precip(gribs, ftime, data)
            do_temp("Maximum temperature", "high", gribs, ftime, data)
            do_temp("Minimum temperature", "low", gribs, ftime, data)

    return data


def bnds(val, lower, upper):
    """Make sure a value is between the bounds, or else it is None"""
    if val is None:
        return None
    if val < lower or val > upper:
        return None
    return val


def dbsave(ts, data):
    """Save the data!"""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    # Check to see if we already have data for this date
    cursor.execute(
        "SELECT id from forecast_inventory WHERE model = 'NDFD' and "
        "modelts = %s",
        (ts,),
    )
    if cursor.rowcount > 0:
        modelid = cursor.fetchone()[0]
        cursor.execute(
            "DELETE from alldata_forecast where modelid = %s",
            (modelid,),
        )
        if cursor.rowcount > 0:
            LOG.warning("Removed %s previous entries", cursor.rowcount)
    else:
        cursor.execute(
            "INSERT into forecast_inventory(model, modelts) VALUES "
            "('NDFD', %s) RETURNING id",
            (ts,),
        )
        modelid = cursor.fetchone()[0]

    for date in list(data["fx"].keys()):
        d = data["fx"][date]
        if d["high"] is None or d["low"] is None or d["precip"] is None:
            del data["fx"][date]

    found_data = False
    for sid, entry in nt.sts.items():
        # Skip virtual stations
        if sid[2:] == "0000" or sid[2] == "C":
            continue
        x, y = data["proj"](entry["lon"], entry["lat"])
        i = np.digitize([x], data["x"])[0]
        j = np.digitize([y], data["y"])[0]
        for date in data["fx"]:
            d = data["fx"][date]
            high = bnds(float(d["high"][j, i]), -70, 140)
            low = bnds(float(d["low"][j, i]), -90, 100)
            precip = bnds(float(d["precip"][j, i] / 25.4), 0, 30)
            if high is None or low is None or precip is None:
                continue
            cursor.execute(
                "INSERT into alldata_forecast(modelid, station, day, high, "
                "low, precip) VALUES (%s, %s, %s, %s, %s, %s)",
                (modelid, sid, date, int(high), int(low), round(precip, 2)),
            )
            found_data = True
    cursor.close()
    # Don't commit the cursor when there is no good data found!
    if found_data:
        pgconn.commit()


@click.command()
@click.option("--date", "ts", help="Date to process")
def main(ts):
    """Go!"""
    # Extract 00 UTC Data
    if ts is not None:
        ts = ts.replace(tzinfo=datetime.timezone.utc)
    else:
        ts = utc().replace(hour=0, minute=0, second=0, microsecond=0)
    data = process(ts)
    if data["proj"] is None:
        LOG.warning("ERROR: found no data!")
    else:
        dbsave(ts, data)


if __name__ == "__main__":
    main()
