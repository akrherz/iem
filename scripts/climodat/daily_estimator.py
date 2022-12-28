"""Climodat Daily Data Estimator.

   python daily_estimator.py YYYY MM DD

RUN_NOON.sh - processes the current date, this skips any calendar day sites
RUN_NOON.sh - processes yesterday, running all sites
RUN_0Z.sh - processes the current date and gets the prelim calday sites data.
RUN_2AM.sh - processes yesterday, which should run all sites
"""
import datetime

# pylint: disable=invalid-unary-operand-type
import sys

import numpy as np
import pandas as pd
from metpy.units import units
from pyiem import iemre
from pyiem.network import Table as NetworkTable
from pyiem.reference import TRACE_VALUE, state_names
from pyiem.util import get_dbconn, get_dbconnstr, logger
from sqlalchemy import text

LOG = logger()
NON_CONUS = ["AK", "HI", "PR", "VI", "GU"]


def load_table(state, date):
    """Update the station table"""
    # IMPORTANT: Only consider sites that are in an online state, so to
    # not run the estimator for `offline` sites
    nt = NetworkTable(f"{state}CLIMATE", only_online=True)
    rows = []
    # Logic to determine if we can generate data for today's date or not
    skip_calday_sites = (
        date == datetime.date.today() and datetime.datetime.now().hour < 18
    )
    threaded = {}
    for sid in nt.sts:
        # handled by compute_0000
        if sid[2:] == "0000" or sid[2] == "C":
            continue
        entry = nt.sts[sid]
        if skip_calday_sites and not entry["temp24_hour"] in range(3, 12):
            continue
        if entry["threading"]:
            threaded[sid] = nt.get_threading_id(sid, date)
            continue
        i, j = iemre.find_ij(entry["lon"], entry["lat"])
        rows.append(
            {
                "station": sid,
                "gridi": i,
                "gridj": j,
                "state": nt.sts[sid]["state"],
                "temp24_hour": nt.sts[sid]["temp24_hour"],
                "precip24_hour": nt.sts[sid]["precip24_hour"],
                "dirty": False,
                "tracks": (
                    nt.sts[sid]["attributes"]
                    .get("TRACKS_STATION", "|")
                    .split("|")[0]
                ),
            }
        )
    if not rows:
        LOG.info("No applicable stations found for state: %s", state)
        return None, threaded
    df = pd.DataFrame(rows)
    df = df.set_index("station")
    # Load up any available observations
    obs = pd.read_sql(
        text(
            "SELECT station, high, low, precip, snow, snowd, temp_hour, "
            "precip_hour, coalesce(temp_estimated, true) as temp_estimated, "
            "coalesce(precip_estimated, true) as precip_estimated "
            f"from alldata_{state} WHERE day = :date and station in :states"
        ),
        get_dbconnstr("coop"),
        params={"date": date, "states": tuple(df.index.values)},
        index_col="station",
    )
    # combine this back into the main table
    df = df.combine_first(obs)
    # Set the default on the estimated columns to True
    for col in ["temp_estimated", "precip_estimated"]:
        df[col] = df[col].fillna(True)
    return df, threaded


def estimate_precip(df, ds):
    """Estimate precipitation based on IEMRE"""
    grid12 = mm2in(ds["p01d_12z"].values)
    grid00 = mm2in(ds["p01d"].values)

    for sid, row in df[pd.isna(df["precip"])].iterrows():
        if row["precip24_hour"] in [0, 22, 23, 24]:
            precip = grid00[row["gridj"], row["gridi"]]
            precip_hour = 0
        else:
            precip = grid12[row["gridj"], row["gridi"]]
            precip_hour = 7  # not precise
        df.at[sid, "precip_estimated"] = True
        df.at[sid, "precip_hour"] = precip_hour
        df.at[sid, "dirty"] = True
        # denote trace
        if 0 < precip < 0.01:
            df.at[sid, "precip"] = TRACE_VALUE
        elif precip < 0:
            df.at[sid, "precip"] = 0
        elif np.isnan(precip) or np.ma.is_masked(precip):
            df.at[sid, "precip"] = 0
        else:
            df.at[sid, "precip"] = precip


def snowval(val):
    """Make sure our snow value makes database sense."""
    if pd.isna(val):
        return None
    return round(float(val), 1)


def mm2in(val):
    """More special logic."""
    return (val * units.mm).to(units.inch).m


def k2f(val):
    """Converter."""
    return (val * units.degK).to(units.degF).m


def estimate_hilo(df, ds):
    """Estimate the High and Low Temperature based on gridded data"""

    highgrid12 = k2f(ds["high_tmpk_12z"].values)
    lowgrid12 = k2f(ds["low_tmpk_12z"].values)
    highgrid00 = k2f(ds["high_tmpk"].values)
    lowgrid00 = k2f(ds["low_tmpk"].values)

    for sid, row in df[pd.isna(df["high"])].iterrows():
        if row["temp24_hour"] in [0, 22, 23]:
            val = highgrid00[row["gridj"], row["gridi"]]
            temp_hour = 0
        else:
            val = highgrid12[row["gridj"], row["gridi"]]
            temp_hour = 7  # Not precise
        if not np.ma.is_masked(val):
            df.at[sid, "temp_hour"] = temp_hour
            df.at[sid, "temp_estimated"] = True
            df.at[sid, "high"] = val
            df.at[sid, "dirty"] = True
    for sid, row in df[pd.isna(df["low"])].iterrows():
        if row["temp24_hour"] in [0, 22, 23]:
            val = lowgrid00[row["gridj"], row["gridi"]]
            temp_hour = 0
        else:
            val = lowgrid12[row["gridj"], row["gridi"]]
            temp_hour = 7  # Not precise
        if not np.ma.is_masked(val):
            df.at[sid, "temp_hour"] = temp_hour
            df.at[sid, "temp_estimated"] = True
            df.at[sid, "low"] = val
            df.at[sid, "dirty"] = True


def nonan(val, precision=0):
    """Can't have NaN."""
    if pd.isna(val):
        return None
    if precision == 0:
        return int(np.round(val, 0))
    return np.round(val, precision)


def commit(cursor, table, df, ts):
    """Inject into the database!"""
    # Inject!
    allowed_failures = 10
    for sid, row in df[df["dirty"]].iterrows():
        LOG.info(
            "sid: %s high: %s low: %s precip: %s snow: %s snowd: %s",
            sid,
            row["high"],
            row["low"],
            row["precip"],
            row["snow"],
            row["snowd"],
        )
        if any(pd.isnull(x) for x in [row["high"], row["low"], row["precip"]]):
            if allowed_failures < 0:
                LOG.warning("aborting commit due too many failures")
                return False
            # These sites could have false positives due to timezone issues
            if row["state"] not in NON_CONUS:
                LOG.info("cowardly refusing %s %s\n%s", sid, ts, row)
                allowed_failures -= 1
            continue

        def do_update(_sid, _row):
            """inline."""
            sql = (
                f"UPDATE {table} SET high = %s, low = %s, precip = %s, "
                "snow = %s, snowd = %s, temp_estimated = %s, "
                "precip_estimated = %s, temp_hour = %s, precip_hour = %s "
                "WHERE day = %s and station = %s"
            )
            args = (
                nonan(_row["high"]),
                nonan(_row["low"]),
                nonan(_row["precip"], 2),
                nonan(_row["snow"], 1),
                nonan(_row["snowd"], 1),
                _row["temp_estimated"],
                _row["precip_estimated"],
                nonan(_row["temp_hour"]),
                nonan(_row["precip_hour"]),
                ts,
                _sid,
            )
            cursor.execute(sql, args)

        do_update(sid, row)
        if cursor.rowcount == 0:
            cursor.execute(
                f"INSERT INTO {table} (station, day, sday, year, month) "
                "VALUES (%s, %s, %s, %s, %s)",
                (sid, ts, ts.strftime("%m%d"), ts.year, ts.month),
            )
            do_update(sid, row)
    return True


def merge_network_obs(df, network, ts):
    """Merge data from observations."""
    obs = pd.read_sql(
        "SELECT t.id as station, max_tmpf as high, min_tmpf as low, "
        "pday as precip, snow, snowd, "
        "coalesce(extract(hour from (coop_valid + '1 minute'::interval) "
        "  at time zone tzname), 24) as temp_hour "
        "from summary s JOIN stations t "
        "on (t.iemid = s.iemid) WHERE t.network = %s and s.day = %s",
        get_dbconnstr("iem"),
        params=(network, ts),
        index_col="station",
    )
    if obs.empty:
        if network not in ["DC_ASOS"]:
            LOG.warning("loading obs for network %s yielded no data", network)
        return df
    obs["precip_hour"] = obs["temp_hour"]
    # If a site has either a null high or low, we need to estimate both to
    # avoid troubles with having only one estimated flag column :/
    for col in ["high", "low"]:
        obs.loc[pd.isnull(obs[col]), ("high", "low")] = np.nan
    obs.loc[obs["high"] <= obs["low"], ("high", "low")] = np.nan
    # Tricky part here, if our present data table has data and is not
    # estimated, we don't want to over-write it!
    df = df.join(obs, how="left", on="tracks", rsuffix="b")
    # HACK the `high` and `precip` columns end up modifying the estimated
    # column, which fouls up subsequent logic
    for col in "low temp_hour high snow snowd precip_hour precip".split():
        estcol = (
            "precip_estimated"
            if col in ["precip", "snow", "snowd", "precip_hour"]
            else "temp_estimated"
        )
        # Use obs if the current entry is null or is estimated and new
        # col is not null
        useidx = pd.isna(df[col]) | (~pd.isna(df[f"{col}b"]) & df[estcol])
        hits = useidx.sum()
        if hits == 0:
            continue
        LOG.info(
            "Found %s/%s rows needing data for %s",
            hits,
            len(df.index),
            col,
        )
        # Workaround pandas-dev/pandas/issues/48673
        if hits == len(df.index):
            df[col] = df[f"{col}b"]
            df["dirty"] = True
            # suboptimal
            if col in ["high", "precip"]:
                df[estcol] = False
        else:
            df.loc[useidx, col] = df[f"{col}b"]
            df.loc[useidx, "dirty"] = True
            # suboptimal
            if col in ["high", "precip"]:
                df.loc[useidx, estcol] = False
        df = df.drop(f"{col}b", axis=1)
    return df


def merge_threaded(df, threaded):
    """Duplicate some data for the threaded stations."""
    for sid in threaded:
        copysid = threaded[sid]
        if copysid in df.index:
            # Ensure that we force a database write for a new entry
            if sid not in df.index:
                df.at[copysid, "dirty"] = True
            df.loc[sid] = df.loc[copysid]


def main(argv):
    """Go Main Go."""
    date = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    ds = iemre.get_grids(date)
    pgconn = get_dbconn("coop")
    states = (
        state_names.keys()
        if len(argv) < 5
        else [
            argv[4],
        ]
    )
    for state in states:
        cursor = pgconn.cursor()
        df, threaded = load_table(state, date)
        if df is None:
            LOG.info("skipping state %s as load_table empty", state)
            continue
        df = merge_network_obs(df, f"{state}_COOP", date)
        df = merge_network_obs(df, f"{state}_ASOS", date)
        # IEMRE does not exist for these states, so we skip this
        if state not in NON_CONUS:
            estimate_hilo(df, ds)
            estimate_precip(df, ds)
            # We can not estimate snow at this time.
        if threaded:
            merge_threaded(df, threaded)
        if not commit(cursor, f"alldata_{state}", df, date):
            return
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    # See how we are called
    main(sys.argv)
