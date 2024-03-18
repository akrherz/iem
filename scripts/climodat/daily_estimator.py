"""Climodat Daily Data Estimator.

This script has been a source of pain for many years.  The present idea is that
this script should not cleanup database problems that could be cleanly
rectified by ``use_acis.py``.  The purpose of this script is to:

1. Create database entries for stations that should be active.
2. Copy observations based on the TRACKS_STATION metadata.
3. Estimate high, low, precip (when necessary) based on IEMRE gridded data.

RUN_NOON.sh - processes the current date, this skips any calendar day sites
RUN_NOON.sh - processes yesterday, running all sites
RUN_0Z.sh - processes the current date and gets the prelim calday sites data.
RUN_2AM.sh - processes yesterday, which should run all sites
"""

import datetime

import click
import numpy as np
import pandas as pd
import xarray as xr
from metpy.units import units
from pyiem import iemre
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.reference import TRACE_VALUE, state_names
from pyiem.util import logger, mm2inch
from sqlalchemy import text

pd.set_option("future.no_silent_downcasting", True)
LOG = logger()
NON_CONUS = ["AK", "HI", "PR", "VI", "GU", "AS"]


def init_df(state, date):
    """Build up a dataframe for further processing."""
    # NB: we need to load all stations and then later cull those that are
    # not relevent for this given date
    nt = NetworkTable(f"{state}CLIMATE", only_online=False)
    rows = []
    # Logic to determine if we can generate data for today's date or not
    skip_calday_sites = (
        date == datetime.date.today() and datetime.datetime.now().hour < 18
    )
    threaded = {}
    for sid, entry in nt.sts.items():
        # handled by compute4regions
        if sid[2:] == "0000" or sid[2] in ["C", "D"]:
            continue
        # clicken/egg status
        ab = date if entry["archive_begin"] is None else entry["archive_begin"]
        ae = date if entry["archive_end"] is None else entry["archive_end"]
        # out of bounds
        if date < ab or date > ae:
            continue
        if skip_calday_sites and entry["temp24_hour"] not in range(3, 12):
            continue
        if entry["threading"]:
            threaded[sid] = nt.get_threading_id(sid, date)
        i, j = iemre.find_ij(entry["lon"], entry["lat"])
        rows.append(
            {
                "day": date,
                "sday": f"{date:%m%d}",
                "year": date.year,
                "month": date.month,
                "station": sid,
                "gridi": i,
                "gridj": j,
                "state": nt.sts[sid]["state"],
                "temp_hour_default": nt.sts[sid]["temp24_hour"],
                "precip_hour_default": nt.sts[sid]["precip24_hour"],
                "dbhas": np.nan,  # so that combine_first works
                "tracks": (nt.sts[sid]["attributes"].get("TRACKS_STATION")),
                "high": np.nan,
                "low": np.nan,
                "precip": np.nan,
                "snow": np.nan,
                "snowd": np.nan,
                "temp_hour": np.nan,
                "precip_hour": np.nan,
                "temp_estimated": True,
                "precip_estimated": True,
            }
        )
    if not rows:
        LOG.info("No applicable stations found for state: %s", state)
        return None, threaded
    return pd.DataFrame(rows).set_index("station"), threaded


def load_current(df: pd.DataFrame, state: str, date):
    """load what our database currently has."""
    # Load up any available observations
    with get_sqlalchemy_conn("coop") as conn:
        obs = pd.read_sql(
            text(
                f"""
                SELECT station, high, low, precip, snow, snowd, temp_hour,
                precip_hour, temp_estimated, precip_estimated,
                true as dbhas from alldata_{state} WHERE day = :date
                and station = ANY(:stations)
                """
            ),
            conn,
            params={"date": date, "stations": df.index.values.tolist()},
            index_col="station",
        )
    # combine this back into the main table
    df = df.combine_first(obs)
    # Update dbhas for those rows without entries
    df["dbhas"] = df["dbhas"].fillna(False).astype(bool)
    # Set the default on the estimated columns to True
    for col in ["temp_estimated", "precip_estimated"]:
        df[col] = df[col].fillna(True)
    # Anything estimated needs to reset the hour to the default as the
    # database may be wrong
    df.loc[df["temp_estimated"], "temp_hour"] = df["temp_hour_default"]
    df.loc[df["precip_estimated"], "precip_hour"] = df["precip_hour_default"]
    # Fix any nulls
    df.loc[pd.isna(df["temp_hour"]), "temp_hour"] = df["temp_hour_default"]
    df.loc[pd.isna(df["precip_hour"]), "precip_hour"] = df[
        "precip_hour_default"
    ]
    return df


def estimate_precip(df, ds: xr.Dataset):
    """Estimate precipitation based on IEMRE"""
    if ds["p01d_12z"].isnull().all():
        LOG.info("p01d_12z is all null, skipping")
        return df
    grid12 = mm2inch(ds["p01d_12z"].values)
    grid00 = mm2inch(ds["p01d"].values)

    # We want the estimator to run anywhere that precip is estimated as
    # estimates may improve with time.
    idx = df["precip_estimated"] | pd.isnull(df["precip"])
    for sid, row in df[idx].iterrows():
        # ensure precip_etimated is set
        df.at[sid, "precip_estimated"] = True
        if row["precip_hour"] in [0, 22, 23, 24]:
            precip = grid00[row["gridj"], row["gridi"]]
            precip_hour = 24
        else:
            precip = grid12[row["gridj"], row["gridi"]]
            precip_hour = 7  # not precise
        df.at[sid, "precip_hour"] = precip_hour
        # denote trace
        if 0 < precip < 0.01:
            df.at[sid, "precip"] = TRACE_VALUE
        elif precip < 0:
            df.at[sid, "precip"] = 0
        elif np.isnan(precip) or np.ma.is_masked(precip):
            df.at[sid, "precip"] = 0
        else:
            df.at[sid, "precip"] = precip
    return df


def k2f(val):
    """Converter."""
    return (val * units.degK).to(units.degF).m


def estimate_hilo(df, ds: xr.Dataset):
    """Estimate the High and Low Temperature based on gridded data"""
    # Ensure that the grid is not all nan or masked
    if ds["high_tmpk_12z"].isnull().all():
        LOG.info("high_tmpk_12z is all null, skipping")
        return df
    highgrid12 = k2f(ds["high_tmpk_12z"].values)
    lowgrid12 = k2f(ds["low_tmpk_12z"].values)
    highgrid00 = k2f(ds["high_tmpk"].values)
    lowgrid00 = k2f(ds["low_tmpk"].values)

    # We want this to rerun for anything already estimated
    idx = df["temp_estimated"] | pd.isnull(df["high"]) | pd.isnull(df["low"])
    for sid, row in df[idx].iterrows():
        # ensure temp_etimated is set
        df.at[sid, "temp_estimated"] = True
        if row["temp_hour"] in [0, 22, 23, 24]:
            val = highgrid00[row["gridj"], row["gridi"]]
            temp_hour = 24
        else:
            val = highgrid12[row["gridj"], row["gridi"]]
            temp_hour = 7  # Not precise
        if not np.ma.is_masked(val):
            df.at[sid, "temp_hour"] = temp_hour
            df.at[sid, "high"] = int(round(val, 0))
        if row["temp_hour"] in [0, 22, 23, 24]:
            val = lowgrid00[row["gridj"], row["gridi"]]
        else:
            val = lowgrid12[row["gridj"], row["gridi"]]
        if not np.ma.is_masked(val):
            df.at[sid, "low"] = int(round(val, 0))
    return df


def update_database(cursor, table: str, df: pd.DataFrame):
    """Inject into the database!"""
    # Datatypes are important to the database update
    df["high"] = df["high"].astype("Int64")
    df["low"] = df["low"].astype("Int64")
    df.loc[df["precip"] > 0.009, "precip"] = df["precip"].round(2)
    df["precip_hour"] = df["precip_hour"].astype("Int64")
    df["temp_hour"] = df["temp_hour"].astype("Int64")

    # Debug print a nice table of the data that gets inserted below
    for row in df.itertuples(index=True):
        LOG.info(
            "%s Hi[%s,%2s]=%3s Lo=%3s Pcp[%s,%2s]=%6s Snow=%6s Snowd=%6s",
            row.Index,
            "T" if row.temp_estimated else "F",
            row.temp_hour,
            row.high,
            row.low,
            "T" if row.precip_estimated else "F",
            row.precip_hour,
            row.precip,
            row.snow,
            row.snowd,
        )

    # initialize any entries we need
    cursor.executemany(
        f"INSERT INTO {table} (station, day, sday, year, month) "
        "VALUES (%(station)s, %(day)s, %(sday)s, %(year)s, %(month)s)",
        df[~df["dbhas"]].reset_index().to_dict("records"),
    )
    # we can update now
    cursor.executemany(
        f"""
        UPDATE {table} SET high = %(high)s, low = %(low)s, precip = %(precip)s,
        snow = %(snow)s, snowd = %(snowd)s,
        precip_estimated = %(precip_estimated)s, precip_hour = %(precip_hour)s,
        temp_estimated = %(temp_estimated)s, temp_hour = %(temp_hour)s
        WHERE station = %(station)s and day = %(day)s
        """,
        df.replace({np.nan: None}).reset_index().to_dict("records"),
    )


def merge_obs(df: pd.DataFrame, state, ts):
    """Merge data from observations."""
    networks = [f"{state}_COOP", f"{state}_ASOS", f"{state}_DCP"]
    with get_sqlalchemy_conn("iem") as conn:
        obs = pd.read_sql(
            text(
                """
            SELECT t.id || '|' || t.network as tracks,
            round(max_tmpf::numeric, 0) as high,
            round(min_tmpf::numeric, 0) as low,
            pday as precip, snow, snowd,
            extract(hour from (coop_valid + '1 minute'::interval)
            at time zone tzname)::int as temp_hour,
            extract(hour from (coop_valid + '1 minute'::interval)
            at time zone tzname)::int as precip_hour
            from summary s JOIN stations t
            on (t.iemid = s.iemid) WHERE t.network = ANY(:networks)
            and s.day = :dt
            """
            ),
            conn,
            params={"networks": networks, "dt": ts},
            index_col="tracks",
        )
    if obs.empty:
        LOG.warning("loading obs for state %s yielded no data", state)
        return df
    # Fill out obs with nan
    obs = obs.fillna(np.nan).infer_objects()
    # If a site has either a null high or low, we need to estimate both to
    # avoid troubles with having only one estimated flag column :/
    obs.loc[obs[["high", "low"]].isna().any(axis=1), ("high", "low")] = np.nan
    obs.loc[obs["high"] <= obs["low"], ("high", "low")] = np.nan
    # Join the obs back onto the main dataframe
    df = df.join(obs, how="left", on="tracks", rsuffix="_obs")
    # We do not estimate snow or snowd, so we can just copy over
    for col in ["snow", "snowd"]:
        take = df[f"{col}_obs"].notna() & (df[f"{col}_obs"] != df[col])
        df.loc[take, col] = df.loc[take, f"{col}_obs"]

    # Variables we can estimate
    for col in ["high", "low", "precip"]:
        estcol = "precip_estimated" if col == "precip" else "temp_estimated"
        hourcol = "precip_hour" if col == "precip" else "temp_hour"
        # I did the maths and there is only one contigency where we can
        # do anything here, that's when we have obs data
        take_obs = df[f"{col}_obs"].notna()
        df.loc[take_obs, col] = df.loc[take_obs, f"{col}_obs"]
        df.loc[take_obs, estcol] = False
        df.loc[take_obs, hourcol] = df.loc[take_obs, f"{hourcol}_obs"]

    for col in ["precip_hour", "temp_hour"]:
        # Account for observations that have no hour set, use default
        df[col] = df[col].fillna(df[f"{col}_default"])
        # replace any 0s with 24
        df[col] = df[col].replace(0, 24)

    return df


def merge_threaded(df, threaded):
    """Duplicate some data for the threaded stations."""
    for sid in threaded:
        copysid = threaded[sid]
        if copysid in df.index:
            # This gets tricky, but we need to retain the dbhas flag
            dbhas = sid in df.index and df.at[sid, "dbhas"]
            df.loc[sid] = df.loc[copysid]
            df.at[sid, "dbhas"] = dbhas
    return df


@click.command()
@click.option("--date", required=True, type=click.DateTime())
@click.option("--state", "st", default=None, help="Single state to process")
def main(date, st):
    """Go Main Go."""
    date = date.date()
    ds = iemre.get_grids(
        date,
        varnames=[
            "high_tmpk",
            "low_tmpk",
            "p01d",
            "p01d_12z",
            "high_tmpk_12z",
            "low_tmpk_12z",
        ],
    )
    pgconn = get_dbconn("coop")
    states = state_names.keys() if st is None else [st]
    for state in states:
        # initialize our dataframe based on station table metadata
        df, threaded = init_df(state, date)
        if df is None:
            LOG.info("skipping state %s as load_table empty", state)
            continue
        # Load what our database has for current obs
        df = load_current(df, state, date)
        df = merge_obs(df, state, date)
        # IEMRE does not exist for these states, so we skip this
        if state not in NON_CONUS:
            df = estimate_hilo(df, ds)
            df = estimate_precip(df, ds)
            # Everything should be filled out.
            missing = df[["high", "low", "precip"]].isna().any(axis=1).sum()
            if missing > 0:
                LOG.info(
                    "state: %s date: %s missing: %s, skipping...",
                    state,
                    date.strftime("%Y-%m-%d"),
                    missing,
                )
                continue
        if threaded:
            df = merge_threaded(df, threaded)
        cursor = pgconn.cursor()
        update_database(cursor, f"alldata_{state}", df)
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
