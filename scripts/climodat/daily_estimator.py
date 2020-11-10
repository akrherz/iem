"""Climodat Daily Data Estimator.

   python daily_estimator.py YYYY MM DD

RUN_NOON.sh - processes the current date, this skips any calendar day sites
RUN_NOON.sh - processes yesterday, running all sites
RUN_2AM.sh - processes yesterday, which should run all sites
"""
import sys
import datetime

import pandas as pd
from pandas.io.sql import read_sql
import numpy as np
from metpy.units import units
from pyiem import iemre
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger
from pyiem.reference import TRACE_VALUE, state_names

LOG = logger()


def load_table(state, date):
    """Update the station table"""
    nt = NetworkTable(f"{state}CLIMATE")
    rows = []
    istoday = date == datetime.date.today()
    for sid in nt.sts:
        # handled by compute_0000
        if sid[2:] == "0000" or sid[2] == "C":
            continue
        if istoday and not nt.sts[sid]["temp24_hour"] in range(3, 12):
            continue
        i, j = iemre.find_ij(nt.sts[sid]["lon"], nt.sts[sid]["lat"])
        rows.append(
            {
                "station": sid,
                "gridi": i,
                "gridj": j,
                "temp24_hour": nt.sts[sid]["temp24_hour"],
                "precip24_hour": nt.sts[sid]["precip24_hour"],
                "tracks": nt.sts[sid]["attributes"]
                .get("TRACKS_STATION", "|")
                .split("|")[0],
            }
        )
    df = pd.DataFrame(rows)
    df.set_index("station", inplace=True)
    for key in ["high", "low", "precip", "snow", "snowd"]:
        df[key] = None
    return df


def estimate_precip(df, ds):
    """Estimate precipitation based on IEMRE"""
    grid12 = mm2in(ds["p01d_12z"].values)
    grid00 = mm2in(ds["p01d"].values)

    for sid, row in df[pd.isna(df["precip"])].iterrows():
        if row["precip24_hour"] in [0, 22, 23]:
            precip = grid00[row["gridj"], row["gridi"]]
        else:
            precip = grid12[row["gridj"], row["gridi"]]
        # denote trace
        if precip > 0 and precip < 0.01:
            df.at[sid, "precip"] = TRACE_VALUE
        elif precip < 0:
            df.at[sid, "precip"] = 0
        elif np.isnan(precip) or np.ma.is_masked(precip):
            df.at[sid, "precip"] = 0
        else:
            df.at[sid, "precip"] = precip


def snowval(val):
    """Make sure our snow value makes database sense."""
    if val is None:
        return None
    return round(float(val), 1)


def mm2in(val):
    """More special logic."""
    return (val * units.mm).to(units.inch).m


def estimate_snow(df, ds):
    """Estimate the Snow based on COOP reports"""
    snowgrid12 = mm2in(ds["snow_12z"].values)
    snowdgrid12 = mm2in(ds["snowd_12z"].values)

    for sid, row in df.iterrows():
        if pd.isnull(row["snow"]):
            df.at[sid, "snow"] = snowgrid12[row["gridj"], row["gridi"]]
        if pd.isnull(row["snowd"]):
            df.at[sid, "snowd"] = snowdgrid12[row["gridj"], row["gridi"]]


def k2f(val):
    """Converter."""
    return (val * units.degK).to(units.degF).m


def estimate_hilo(df, ds):
    """Estimate the High and Low Temperature based on gridded data"""

    highgrid12 = k2f(ds["high_tmpk_12z"].values)
    lowgrid12 = k2f(ds["low_tmpk_12z"].values)
    highgrid00 = k2f(ds["high_tmpk"].values)
    lowgrid00 = k2f(ds["low_tmpk"].values)

    for sid, row in df.iterrows():
        if pd.isnull(row["high"]):
            if row["temp24_hour"] in [0, 22, 23]:
                val = highgrid00[row["gridj"], row["gridi"]]
            else:
                val = highgrid12[row["gridj"], row["gridi"]]
            if not np.ma.is_masked(val):
                df.at[sid, "high"] = val
        if pd.isnull(row["low"]):
            if row["temp24_hour"] in [0, 22, 23]:
                val = lowgrid00[row["gridj"], row["gridi"]]
            else:
                val = lowgrid12[row["gridj"], row["gridi"]]
            if not np.ma.is_masked(val):
                df.at[sid, "low"] = val


def nonan(val, precision):
    """Can't have NaN."""
    if np.isnan(val):
        return None
    return np.round(val, precision)


def commit(cursor, table, df, ts):
    """Inject into the database!"""
    # Inject!
    allowed_failures = 10
    for sid, row in df.iterrows():
        LOG.debug(
            "sid: %s high: %s low: %s precip: %s snow: %s snowd: %s",
            sid,
            row["high"],
            row["low"],
            row["precip"],
            row["snow"],
            row["snowd"],
        )
        if any(np.isnan(x) for x in [row["high"], row["low"], row["precip"]]):
            if allowed_failures < 0:
                LOG.warning("aborting commit due too many failures")
                return False
            LOG.info(
                "daily_estimator cowardly refusing %s %s\n%s", sid, ts, row
            )
            allowed_failures -= 1
            continue

        def do_update(_sid, _row):
            """inline."""
            sql = (
                f"UPDATE {table} SET high = %s, low = %s, precip = %s, "
                "snow = %s, snowd = %s, estimated = 't' WHERE day = %s "
                "and station = %s"
            )
            args = (
                nonan(_row["high"], 0),
                nonan(_row["low"], 0),
                nonan(_row["precip"], 2),
                nonan(_row["snow"], 1),
                nonan(_row["snowd"], 1),
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
    pgconn = get_dbconn("iem")
    obs = read_sql(
        "SELECT t.id as station, max_tmpf as high, min_tmpf as low, "
        "pday as precip, snow, snowd from summary s JOIN stations t "
        "on (t.iemid = s.iemid) WHERE t.network = %s and s.day = %s",
        pgconn,
        params=(network, ts),
        index_col="station",
    )
    # Some COOP sites may not report 'daily' high and low, so we cull those
    # out as nulls
    obs.at[obs["high"] <= obs["low"], ["high", "low"]] = None
    if obs.empty:
        LOG.warning("loading obs for network %s yielded no data", network)
        return df
    df = df.join(obs, how="left", on="tracks", rsuffix="b")
    for col in ["high", "low", "precip", "snow", "snowd"]:
        df[col].update(df[col + "b"])
        df = df.drop(col + "b", axis=1)
    return df


def main(argv):
    """Go Main Go."""
    date = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    ds = iemre.get_grids(date)
    pgconn = get_dbconn("coop")
    for state in state_names:
        if state in ["AK", "HI", "DC"]:
            continue
        table = f"alldata_{state}"
        cursor = pgconn.cursor()
        df = load_table(state, date)
        df = merge_network_obs(df, f"{state}_COOP", date)
        df = merge_network_obs(df, f"{state}_ASOS", date)
        estimate_hilo(df, ds)
        estimate_precip(df, ds)
        estimate_snow(df, ds)
        if not commit(cursor, table, df, date):
            return
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    # See how we are called
    main(sys.argv)
