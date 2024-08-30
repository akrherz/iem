"""Compute daily summaries of ASOS/METAR data.

Called from RUN_12Z.sh with no args and 2 days ago
Called from RUN_MIDNIGHT.sh with no args
"""

import time
import warnings
from datetime import date, datetime, timedelta
from typing import Optional

import click
import metpy.calc as mcalc
import numpy as np
import pandas as pd
from metpy.units import units as munits
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.util import logger
from sqlalchemy import text

LOG = logger()
# bad values into mcalc
warnings.simplefilter("ignore", RuntimeWarning)


def clean(val, floor, ceiling):
    """Make sure RH values are always sane"""
    if val > ceiling or val < floor or pd.isna(val):
        return None
    if isinstance(val, munits.Quantity):
        return float(val.magnitude)
    return float(val)


def compute_wind_gusts(gdf, currentrow, newdata):
    """Do wind gust logic."""
    dfmax = max([gdf["gust"].max(), gdf["peak_wind_gust"].max()])
    if pd.isnull(dfmax) or (
        currentrow["max_gust"] is not None and currentrow["max_gust"] >= dfmax
    ):
        return
    newdata["max_gust"] = dfmax
    # need to figure out timestamp
    peakrows = gdf[gdf["peak_wind_gust"] == dfmax]
    if peakrows.empty:
        peakrows = gdf[gdf["gust"] == dfmax]
        if peakrows.empty:
            return
        newdata["max_gust_ts"] = peakrows.iloc[0]["valid"]
        is_new("max_drct", peakrows.iloc[0]["drct"], currentrow, newdata)
    else:
        newdata["max_gust_ts"] = peakrows.iloc[0]["peak_wind_time"]
        is_new(
            "max_drct", peakrows.iloc[0]["peak_wind_drct"], currentrow, newdata
        )


def is_new(colname, newval, currentrow, newdata):
    """Comp and set."""
    if pd.isnull(newval):
        return
    if (
        pd.isnull(currentrow[colname])
        or abs(newval - currentrow[colname]) > 0.01
    ):
        newdata[colname] = newval


def do(dt: date):
    """Process this date timestamp"""
    iemaccess = get_dbconn("iem")
    icursor = iemaccess.cursor()
    table = f"summary_{dt.year}"
    # Get what we currently know, just grab everything
    with get_sqlalchemy_conn("iem") as conn:
        current = pd.read_sql(
            text(f"SELECT * from {table} WHERE day = :dt"),
            conn,
            params={"dt": dt},
            index_col="iemid",
        )
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text("""
        select station, network, iemid, drct, sknt, gust,
        valid at time zone tzname as localvalid, valid,
        tmpf, dwpf, relh, feel,
        peak_wind_gust, peak_wind_drct, peak_wind_time,
        peak_wind_time at time zone tzname as local_peak_wind_time from
        alldata d JOIN stations t on (t.id = d.station)
        where network ~* 'ASOS'
        and valid between :sts and :ets and t.tzname is not null
        and date(valid at time zone tzname) = :dt
        ORDER by valid ASC
        """),
            conn,
            params={
                "sts": dt - timedelta(days=2),
                "ets": dt + timedelta(days=2),
                "dt": dt,
            },
            index_col=None,
        )
    if df.empty:
        LOG.info("no ASOS database entries for %s", dt)
        return
    # derive some parameters
    df["u"], df["v"] = mcalc.wind_components(
        df["sknt"].values * munits.knots, df["drct"].values * munits.deg
    )
    df["localvalid_lag"] = df.groupby("iemid")["localvalid"].shift(1)
    df["timedelta"] = df["localvalid"] - df["localvalid_lag"]
    ndf = df[pd.isna(df["timedelta"])]
    df.loc[ndf.index.values, "timedelta"] = pd.to_timedelta(
        ndf["localvalid"].dt.hour * 3600.0
        + ndf["localvalid"].dt.minute * 60.0,
        unit="s",
    )
    df["timedelta"] = df["timedelta"] / np.timedelta64(1, "s")

    updates = 0
    for iemid, gdf in df.groupby("iemid"):
        if len(gdf.index) < 6:
            continue
        if iemid not in current.index:
            LOG.info(
                "Adding %s for %s %s %s",
                table,
                gdf.iloc[0]["station"],
                gdf.iloc[0]["network"],
                dt,
            )
            icursor.execute(
                f"INSERT into {table} (iemid, day) values (%s, %s)",
                (iemid, dt),
            )
            current.loc[iemid] = None
        newdata = {}
        currentrow = current.loc[iemid]
        compute_wind_gusts(gdf, currentrow, newdata)
        # take the nearest value
        ldf = gdf.copy().bfill().ffill()
        totsecs = ldf["timedelta"].sum()
        is_new(
            "avg_rh",
            clean((ldf["relh"] * ldf["timedelta"]).sum() / totsecs, 1, 100),
            currentrow,
            newdata,
        )
        is_new("min_rh", clean(ldf["relh"].min(), 1, 100), currentrow, newdata)
        is_new("max_rh", clean(ldf["relh"].max(), 1, 100), currentrow, newdata)

        uavg = (ldf["u"] * ldf["timedelta"]).sum() / totsecs
        vavg = (ldf["v"] * ldf["timedelta"]).sum() / totsecs
        is_new(
            "vector_avg_drct",
            clean(
                mcalc.wind_direction(uavg * munits.knots, vavg * munits.knots),
                0,
                360,
            ),
            currentrow,
            newdata,
        )
        is_new(
            "avg_sknt",
            clean((ldf["sknt"] * ldf["timedelta"]).sum() / totsecs, 0, 150),
            currentrow,
            newdata,
        )
        is_new(
            "max_sknt",
            clean(ldf["sknt"].max(), 0, 150),
            currentrow,
            newdata,
        )
        is_new(
            "max_feel",
            clean(ldf["feel"].max(), -150, 200),
            currentrow,
            newdata,
        )
        is_new(
            "avg_feel",
            clean((ldf["feel"] * ldf["timedelta"]).sum() / totsecs, -150, 200),
            currentrow,
            newdata,
        )
        is_new(
            "min_feel",
            clean(ldf["feel"].min(), -150, 200),
            currentrow,
            newdata,
        )
        if not newdata:
            continue
        cols = []
        args = []
        for key, val in newdata.items():
            cols.append(f"{key} = %s")
            args.append(val)
        args.extend([iemid, dt])

        sql = ", ".join(cols)

        icursor.execute(
            f"UPDATE {table} SET {sql} WHERE iemid = %s and day = %s", args
        )
        updates += 1
        if icursor.rowcount == 0:
            LOG.info(
                " update of %s[%s] was 0",
                gdf.iloc[0]["station"],
                gdf.iloc[0]["network"],
            )
        if updates % 100 == 0:
            icursor.close()
            iemaccess.commit()
            icursor = iemaccess.cursor()

    icursor.close()
    iemaccess.commit()
    iemaccess.close()


@click.command()
@click.option(
    "--date", "dt", type=click.DateTime(), required=False, help="Date"
)
def main(dt: Optional[datetime]):
    """Go Main Go"""
    if dt is None:
        dt = date.today() - timedelta(days=1)
    else:
        dt = dt.date()
    try:
        do(dt)
    except Exception as exp:
        LOG.info("first pass yield an exception")
        LOG.exception(exp)
        LOG.info("sleeping two minutes before trying once more")
        time.sleep(120)
        do(dt)


if __name__ == "__main__":
    main()
