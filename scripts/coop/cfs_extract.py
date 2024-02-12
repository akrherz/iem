"""Extract data from CFS

Total precipitation
Maximum temperature
Minimum temperature

Run at 5 AM local from RUN_10_AFTER.sh
"""
import datetime

import numpy as np
import pygrib
from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.util import archive_fetch, convert_value, logger, utc

LOG = logger()


def do_agg(dkey, fname, ts, data):
    """Do aggregate"""
    ppath = ts.strftime(
        f"%Y/%m/%d/model/cfs/%H/{fname}.01.%Y%m%d%H.daily.grib2"
    )
    with archive_fetch(ppath) as fn:
        if fn is None:
            LOG.info("missing %s", ppath)
            return
        # Precip
        gribs = pygrib.open(fn)
        for grib in gribs:
            if data["x"] is None:
                lat, lon = grib.latlons()
                data["y"] = lat[:, 0]
                data["x"] = lon[0, :]
            ftime = ts + datetime.timedelta(hours=grib.forecastTime)
            cst = ftime - datetime.timedelta(hours=7)
            key = cst.strftime("%Y-%m-%d")
            d = data["fx"].setdefault(
                key, dict(precip=None, high=None, low=None, srad=None)
            )
            LOG.info("Writting %s %s from ftime: %s", dkey, key, ftime)
            if d[dkey] is None:
                d[dkey] = grib.values * 6 * 3600.0
            else:
                d[dkey] += grib.values * 6 * 3600.0


def do_temp(dkey, fname, func, ts, data):
    """Do Temperatures"""
    ppath = ts.strftime(
        f"%Y/%m/%d/model/cfs/%H/{fname}.01.%Y%m%d%H.daily.grib2"
    )
    with archive_fetch(ppath) as fn:
        if fn is None:
            LOG.info("missing %s", ppath)
            return
        gribs = pygrib.open(fn)
        for grib in gribs:
            ftime = ts + datetime.timedelta(hours=grib.forecastTime)
            cst = ftime - datetime.timedelta(hours=7)
            key = cst.strftime("%Y-%m-%d")
            if key not in data["fx"]:
                continue
            d = data["fx"][key]
            LOG.info("Writting %s %s from ftime: %s", dkey, key, ftime)
            if d[dkey] is None:
                d[dkey] = grib.values
            else:
                d[dkey] = func(d[dkey], grib.values)


def process(ts):
    """Do Work"""
    data = {"x": None, "y": None, "proj": None, "fx": {}}
    do_agg("precip", "prate", ts, data)
    do_temp("high", "tmax", np.maximum, ts, data)
    do_temp("low", "tmin", np.minimum, ts, data)
    do_agg("srad", "dswsfc", ts, data)

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
    if data["x"] is None:
        LOG.warning("No longitude info found, aborting")
        return

    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    # Check to see if we already have data for this date
    cursor.execute(
        "SELECT id from forecast_inventory "
        "WHERE model = 'CFS' and modelts = %s",
        (ts,),
    )
    if cursor.rowcount > 0:
        modelid = cursor.fetchone()[0]
        cursor.execute(
            "DELETE from alldata_forecast where modelid = %s", (modelid,)
        )
        if cursor.rowcount > 0:
            LOG.warning("Removed %s previous entries", cursor.rowcount)
    else:
        cursor.execute(
            "INSERT into forecast_inventory(model, modelts) "
            "VALUES ('CFS', %s) RETURNING id",
            (ts,),
        )
        modelid = cursor.fetchone()[0]

    for date in list(data["fx"].keys()):
        d = data["fx"][date]
        if (
            d["high"] is None
            or d["low"] is None
            or d["precip"] is None
            or d["srad"] is None
        ):
            LOG.warning("Missing data for date: %s", date)
            del data["fx"][date]

    nt = NetworkTable("IACLIMATE")
    for sid, entry in nt.sts.items():
        # Skip virtual stations
        if sid[2:] == "0000" or sid[2] in ["C", "D"]:
            continue
        # Careful here, lon is 0-360 for this file
        i = np.digitize([entry["lon"] + 360], data["x"])[0]
        j = np.digitize([entry["lat"]], data["y"])[0]
        for date in data["fx"]:
            d = data["fx"][date]
            high = bnds(
                convert_value(d["high"][j, i], "degK", "degF"), -70, 140
            )
            low = bnds(convert_value(d["low"][j, i], "degK", "degF"), -90, 120)
            precip = bnds(round(float(d["precip"][j, i] / 25.4), 2), 0, 30)
            srad = bnds(d["srad"][j, i] / 1000000.0, 0, 50)
            if high is None or low is None or precip is None or srad is None:
                continue
            cursor.execute(
                """
                INSERT into alldata_forecast(modelid,
                station, day, high, low, precip, srad)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (modelid, sid, date, int(high), int(low), precip, srad),
            )
    cursor.close()
    pgconn.commit()


def main():
    """Go!"""
    # Extract 12 UTC Data
    ts = utc() - datetime.timedelta(days=4)
    ts = ts.replace(hour=12, minute=0, second=0, microsecond=0)
    data = process(ts)
    dbsave(ts, data)


if __name__ == "__main__":
    main()
