"""Compute daily summaries of observed data.

NOTE: We don't want to compute things provided by ASOS DSM/CF6/CLI data.

Called from RUN_12Z.sh with no args and 2 days ago
Called from RUN_MIDNIGHT.sh with no args
"""

import warnings
from datetime import date, datetime, timedelta

import click
import metpy.calc as mcalc
import numpy as np
import pandas as pd
from metpy.units import units as munits
from pyiem.database import get_dbconn, get_sqlalchemy_conn, sql_helper
from pyiem.util import logger

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


def compute_wind_gusts_asos(gdf, currentrow, newdata):
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


def get_rwis_obs(dt: date) -> pd.DataFrame:
    """Get RWIS observations for a given date."""
    with get_sqlalchemy_conn("rwis") as conn:
        obsdf = pd.read_sql(
            sql_helper("""
        select t.id as station, network, d.iemid, drct, sknt, gust, dwpf,
        valid at time zone tzname as localvalid, valid, relh, feel from
        alldata d JOIN stations t on (t.iemid = d.iemid)
        where network ~* 'RWIS'
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
    return obsdf


def get_asos_obs(dt: date) -> pd.DataFrame:
    """Get ASOS observations for a given date."""
    with get_sqlalchemy_conn("asos") as conn:
        obsdf = pd.read_sql(
            sql_helper("""
        select station, network, iemid, drct, sknt, gust, dwpf,
        valid at time zone tzname as localvalid, valid, relh, feel,
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
    return obsdf


def compute_things(df):
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


def do(dt: date, netclass: str, meta: dict):
    """Process this date timestamp"""
    iemaccess = get_dbconn("iem")
    icursor = iemaccess.cursor()
    table = f"summary_{dt.year}"
    # Get what we currently know, just grab everything
    with get_sqlalchemy_conn("iem") as conn:
        current = pd.read_sql(
            sql_helper(
                """
    SELECT s.* from {table} s JOIN stations t on (s.iemid = t.iemid)
    WHERE day = :dt and network ~* :netclass
            """,
                table=table,
            ),
            conn,
            params={"dt": dt, "netclass": netclass},
            index_col="iemid",
        )
    LOG.info("Found %s summary entries for %s", len(current.index), netclass)
    obsdf = meta["getobs"](dt)
    if obsdf.empty:
        LOG.info("no %s database entries for %s", netclass, dt)
        return
    compute_things(obsdf)

    updates = 0
    for iemid, gdf in obsdf.groupby("iemid"):
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
            # Commit this immediately attempting to avoid a deadlock that
            # has been difficult to track down
            icursor.close()
            iemaccess.commit()
            icursor = iemaccess.cursor()
            current.loc[iemid] = None
        newdata = {}
        currentrow = current.loc[iemid]
        if netclass == "ASOS":
            compute_wind_gusts_asos(gdf, currentrow, newdata)
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

        is_new(
            "max_dwpf",
            clean(ldf["dwpf"].max(), -150, 100),
            currentrow,
            newdata,
        )
        is_new(
            "min_dwpf",
            clean(ldf["dwpf"].min(), -150, 100),
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

    LOG.info("Updated %s/%s summary rows", updates, len(current.index))
    icursor.close()
    iemaccess.commit()
    iemaccess.close()


@click.command()
@click.option(
    "--date", "dt", type=click.DateTime(), required=True, help="Date"
)
def main(dt: datetime):
    """Go Main Go"""
    dt = dt.date()
    settings = {
        "ASOS": {"database": "asos", "getobs": get_asos_obs},
        "RWIS": {"database": "rwis", "getobs": get_rwis_obs},
    }
    for netclass, meta in settings.items():
        try:
            do(dt, netclass, meta)
        except Exception as exp:
            LOG.warning("compute_daily %s %s failed", netclass, dt)
            LOG.exception(exp)


if __name__ == "__main__":
    main()
