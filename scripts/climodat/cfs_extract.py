"""Extract data from CFS for climodat and later usage of yieldfx

Run from RUN_NOON.sh
"""

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
from metpy.units import units
from netCDF4 import Dataset
from pyiem.database import get_dbconn
from pyiem.iemre import find_ij
from pyiem.network import Table as NetworkTable
from pyiem.util import logger, ncopen

LOG = logger()


def process(nc: Dataset) -> pd.DataFrame:
    """Do Work."""
    date0 = datetime.strptime(
        nc.variables["time"].units[:21],
        "Days since %Y-%m-%d",
    ).date()
    taxis = [date0 + timedelta(days=t) for t in nc.variables["time"][:]]
    rows = []
    nt = NetworkTable("IACLIMATE")
    for sid, entry in nt.sts.items():
        # Skip virtual stations
        if sid[2:] == "0000" or sid[2] in ["C", "D"]:
            continue

        i, j = find_ij(entry["lon"], entry["lat"], domain="conus")

        highs = (
            (units("degK") * nc.variables["high_tmpk"][:, j, i])
            .to(units("degF"))
            .m
        )
        lows = (
            (units("degK") * nc.variables["low_tmpk"][:, j, i])
            .to(units("degF"))
            .m
        )
        precip = (
            (units("mm") * nc.variables["p01d"][:, j, i]).to(units("inch")).m
        )
        srad = nc.variables["srad"][:, j, i] * 86400.0 / 1e6  # W/m^2 -> MJ/m^2

        for idx, valid in enumerate(taxis):
            high = bnds(highs[idx], -70, 140)
            low = bnds(lows[idx], -90, 120)
            thisprecip = bnds(precip[idx], 0, 30)
            thissrad = bnds(srad[idx], 0, 50)
            if (
                high is None
                or low is None
                or thisprecip is None
                or thissrad is None
            ):
                continue
            rows.append(
                {
                    "sid": sid,
                    "valid": valid,
                    "high": round(high, 0),
                    "low": round(low, 0),
                    "precip": round(float(thisprecip), 2),
                    "srad": round(float(thissrad), 2),
                }
            )

    return pd.DataFrame(rows)


def bnds(val, lower, upper):
    """Make sure a value is between the bounds, or else it is None"""
    if pd.isna(val) or np.ma.is_masked(val):
        return None
    if val < lower or val > upper:
        return None
    return val


def dbsave(model_init: datetime, df: pd.DataFrame):
    """Save the data!"""

    pgconn = get_dbconn("coop", rw=True)
    cursor = pgconn.cursor()
    # Check to see if we already have data for this date
    cursor.execute(
        "SELECT id from forecast_inventory "
        "WHERE model = 'CFS' and modelts = %s",
        (model_init,),
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
            (model_init,),
        )
        modelid = cursor.fetchone()[0]

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT into alldata_forecast(modelid,
            station, day, high, low, precip, srad)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
            (
                modelid,
                row["sid"],
                row["valid"],
                int(row["high"]),
                int(row["low"]),
                row["precip"],
                row["srad"],
            ),
        )
    LOG.info("Inserted %s rows for modelid %s", len(df.index), modelid)
    cursor.close()
    pgconn.commit()


def main():
    """Go!"""
    with ncopen("/mesonet/data/iemre/cfs_current.nc") as nc:
        ts = datetime.strptime(
            nc.getncattr("model_init"), "%Y-%m-%d %H:%M UTC"
        ).replace(tzinfo=timezone.utc)
        df = process(nc)
    if not df.empty:
        dbsave(ts, df)


if __name__ == "__main__":
    main()
