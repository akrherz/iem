"""
Need to do some custom 1 minute data aggregation to fill out hourly table.
"""
import datetime

import numpy as np
import pandas as pd
from pyiem.util import get_dbconn, get_sqlalchemy_conn, utc, logger

LOG = logger()
TIME_FORMAT = "%Y-%m-%d %H:%M-06"


def hourly_process(cursor, station, hour, mdf, hdf):
    """Merge this row information into the database."""
    # The totals for this hour are stored for the next hour
    row = pd.Series(
        {"station": station, "valid": hour + datetime.timedelta(hours=1)}
    )
    if row["valid"] not in hdf.index:
        return
    lastob = mdf.iloc[-1]
    sumdf = mdf.sum(numeric_only=True)
    row["obs_count"] = len(mdf.index)
    current = hdf.loc[row["valid"]]
    if current["obs_count"] == row["obs_count"]:
        return
    row["slrkj_tot"] = sumdf["slrkj_tot"]
    # Take last ob
    for colname in (
        "t4_c_avg t12_c_avg t24_c_avg t50_c_avg calcvwc12_avg "
        "calcvwc24_avg calcvwc50_avg rh_avg"
    ).split():
        row[colname] = float(lastob[f"{colname}_qc"])
    # Soil Vue Madness
    for depth in [2, 4, 8, 12, 14, 16, 20, 24, 28, 30, 32, 36, 40, 42, 52]:
        for col in ["t", "vwc", "ec"]:
            row[f"sv_{col}{depth}"] = float(lastob[f"sv_{col}{depth}_qc"])
    tokens = []
    sigh = {
        "calcvwc12_avg": "calc_vwc_12_avg",
        "calcvwc24_avg": "calc_vwc_24_avg",
        "calcvwc50_avg": "calc_vwc_50_avg",
    }
    for colname in row.index:
        if colname in ["station", "valid"]:
            continue
        if colname == "obs_count":
            tokens.append(f"{colname} = {row[colname]}")
            continue
        cname = sigh.get(colname, colname)
        tokens.append(f"{cname} = coalesce({cname}, %({colname})s)")
        tokens.append(f"{cname}_qc = coalesce({cname}_qc, %({colname})s)")
    LOG.info("updating sm_hourly %s %s", station, row["valid"])
    cursor.execute(
        f"UPDATE sm_hourly SET {','.join(tokens)} "
        "WHERE station = %(station)s and valid = %(valid)s",
        row,
    )


def daily_process(cursor, station, date, df, ddf):
    """Process this date's dataframe."""
    mindf = df.min(numeric_only=True)
    maxdf = df.max(numeric_only=True)
    avgdf = df.mean(numeric_only=True)
    row = pd.Series({"station": station, "date": date})
    row["obs_count"] = df["tair_c_avg_qc"].size
    row["tair_c_max"] = maxdf["tair_c_avg_qc"]
    row["tair_c_min"] = mindf["tair_c_avg_qc"]
    # For daily, we want the average for some of these columns
    for colname in (
        "t4_c_avg t12_c_avg t24_c_avg t50_c_avg calcvwc12_avg "
        "calcvwc24_avg calcvwc50_avg rh_avg"
    ).split():
        row[colname] = float(avgdf[f"{colname}_qc"])
    # Soil Vue Madness
    for depth in [2, 4, 8, 12, 14, 16, 20, 24, 28, 30, 32, 36, 40, 42, 52]:
        for col in ["t", "vwc", "ec"]:
            row[f"sv_{col}{depth}"] = float(avgdf[f"sv_{col}{depth}_qc"])
    current = ddf.loc[(station, date)]
    if current["obs_count"] == row["obs_count"]:
        LOG.info("%s %s obs_count %s matches", date, station, row["obs_count"])
        return
    # Ensure database gets nulls and not nan
    row = row.replace({np.nan: None})
    # build up SQL statement
    tokens = []
    sigh = {
        "calcvwc12_avg": "calc_vwc_12_avg",
        "calcvwc24_avg": "calc_vwc_24_avg",
        "calcvwc50_avg": "calc_vwc_50_avg",
    }
    for colname in row.index:
        if colname in ["station", "date"]:
            continue
        if colname == "obs_count":
            tokens.append(f"{colname} = {row[colname]}")
            continue
        cname = sigh.get(colname, colname)
        tokens.append(f"{cname} = coalesce({cname}, %({colname})s)")
        tokens.append(f"{cname}_qc = coalesce({cname}_qc, %({colname})s)")
    LOG.info("updating sm_daily %s %s", station, date)
    cursor.execute(
        f"UPDATE sm_daily SET {','.join(tokens)} "
        "WHERE station = %(station)s and valid = %(date)s",
        row,
    )


def do_date_ops(df):
    """Common things."""
    df["utc_valid"] = df["utc_valid"].dt.tz_localize("UTC")
    df = df.drop(columns="valid")
    # Compute a LST date via UTC-6
    df["date"] = (df["utc_valid"] - datetime.timedelta(hours=6)).dt.date
    return df


def main():
    """Do things."""
    pgconn = get_dbconn("isuag")
    # We need to collect up data for periods representing CST dates, this
    # is tricky business
    date = datetime.date.today() - datetime.timedelta(days=7)
    # 6z is the start of such a date
    sts = utc(date.year, date.month, date.day, 6)
    with get_sqlalchemy_conn("isuag") as conn:
        # Get the minute data
        mdf = pd.read_sql(
            "SELECT *, valid at time zone 'UTC' as utc_valid from sm_minute "
            "where valid >= %s ORDER by valid ASC",
            conn,
            params=(sts,),
            index_col=None,
        ).fillna(np.nan)
        # Get the hourly data
        hdf = pd.read_sql(
            "SELECT *, valid at time zone 'UTC' as utc_valid from sm_hourly "
            "where valid >= %s ORDER by valid ASC",
            conn,
            params=(sts,),
            index_col=None,
        )
        # Get the daily data
        ddf = pd.read_sql(
            "SELECT * from sm_daily where valid >= %s ORDER by valid ASC",
            conn,
            params=(sts.date(),),
            index_col=["station", "valid"],
        )

    # Do date operations
    mdf = do_date_ops(mdf)
    hdf = do_date_ops(hdf).set_index(["station", "utc_valid"])

    # Daily work
    cursor = pgconn.cursor()
    for (station, date), gdf in mdf.groupby(["station", "date"]):
        if (station, date) not in ddf.index:
            LOG.info("%s %s not in daily, skipping", station, date)
            continue
        daily_process(cursor, station, date, gdf, ddf)
    cursor.close()
    pgconn.commit()

    # Hourly work
    cursor = pgconn.cursor()
    for station, gdf in mdf.groupby("station"):
        for hour, hgdf in mdf.set_index("utc_valid").resample("H"):
            hourly_process(cursor, station, hour, hgdf, hdf.loc[station, :])
    cursor.close()
    pgconn.commit()

    # Special case of PET
    cursor = pgconn.cursor()
    cursor.execute(
        """WITH data as (
        SELECT station, date(valid),
        sum(etalfalfa_qc) as dailyet from sm_hourly WHERE
        valid >= %s and etalfalfa_qc is not null GROUP by station, date)
        UPDATE sm_daily s SET dailyet_qc = d.dailyet, dailyet = d.dailyet
        FROM data d WHERE s.station = d.station and s.valid = d.date""",
        (sts,),
    )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
