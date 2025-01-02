"""Hey, we are going to QC precipitation, somehow!

Implementation Thoughts:

1. We are really only caring about the situation of having too low of precip
2. We'll take the stage IV product as gospel
3. We won't update the 'raw' precip tables
4. This uses the flag 'E' for estimated
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import click
import httpx
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.reference import ISO8601
from pyiem.util import logger, utc

LOG = logger()


def print_debugging(station):
    """Add some more details to the output messages to help with ticket res"""
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT valid, rain_in_tot, rain_in_tot_qc, "
        "rain_in_tot_f from sm_daily WHERE station = %s and "
        "(rain_in_tot > 0 or rain_in_tot_qc > 0) ORDER by valid DESC LIMIT 10",
        (station,),
    )
    print("     Date           Obs     QC  Flag")
    for row in cursor:
        print(f"     {row[0]}   {row[1]:5.2f}  {row[2]:5.2f} {row[3]}")


def get_hdf(nt, dt):
    """Fetch the hourly dataframe for this network"""
    # Get our stage IV hourly totals
    rows = []
    for station in nt.sts:
        # service provides UTC dates, so we need to request two days
        for ldate in [dt, dt + timedelta(days=1)]:
            uri = (
                "http://iem.local/json/stage4/"
                f"{nt.sts[station]['lon']:.2f}/"
                f"{nt.sts[station]['lat']:.2f}/{ldate:%Y-%m-%d}"
            )
            try:
                resp = httpx.get(uri, timeout=30)
                resp.raise_for_status()
                jdata = resp.json()
            except Exception as exp:
                LOG.warning("JSON stage4 service failed\n%s\n%s", uri, exp)
                continue
            for entry in jdata["data"]:
                rows.append(  # noqa
                    {
                        "station": station,
                        "valid": datetime.strptime(
                            entry["end_valid"], ISO8601
                        ).replace(tzinfo=ZoneInfo("UTC")),
                        "precip_in": entry["precip_in"],
                    }
                )
    df = pd.DataFrame(rows)
    df = df.fillna(0)
    return df


def set_iemacces(station, dt, precip_inch):
    """Set the precip value for IEMAccess."""
    # update iemaccess
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()
    LOG.info("Update iemaccess %s %s %.4f", station, dt, precip_inch)
    cursor.execute(
        "UPDATE summary s SET pday = %s FROM stations t WHERE "
        "t.iemid = s.iemid and s.day = %s and t.id = %s and "
        "t.network = 'ISUSM'",
        (precip_inch, dt, station),
    )
    cursor.close()
    pgconn.commit()


def update_precip(dt, station, hdf):
    """Do the update work"""
    sts = utc(dt.year, dt.month, dt.day, 7)
    ets = sts + timedelta(hours=24)
    ldf = hdf[
        (hdf["station"] == station)
        & (hdf["valid"] >= sts)
        & (hdf["valid"] < ets)
    ]

    newpday = ldf["precip_in"].sum()
    set_iemacces(station, dt, newpday)
    # update isusm
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor()
    # daily
    cursor.execute(
        "UPDATE sm_daily SET rain_in_tot_qc = %s, rain_in_tot_f = 'E' "
        "WHERE valid = %s and station = %s",
        (newpday, dt, station),
    )
    for _, row in ldf.iterrows():
        # hourly
        LOG.info(
            "set hourly %s %s %s", station, row["valid"], row["precip_in"]
        )
        cursor.execute(
            "UPDATE sm_hourly SET rain_in_tot_qc = %s, rain_in_tot_f = 'E' "
            "WHERE valid = %s and station = %s",
            (row["precip_in"], row["valid"], station),
        )
        # For minute data, we just apply a linear offset
        cursor.execute(
            "SELECT sum(rain_in_tot) from sm_minute WHERE station = %s and "
            "valid > %s and valid <= %s",
            (
                station,
                row["valid"],
                row["valid"] + timedelta(minutes=60),
            ),
        )
        if cursor.rowcount == 0:
            LOG.warning("Can't adjust %s %s, no data", station, row["valid"])
            continue
        current_in = cursor.fetchone()[0]
        multi = 0
        value = None
        if current_in == 0:
            value = row["precip_in"] / 60.0
        elif row["precip_in"] > 0:
            multi = row["precip_in"] / current_in
        cursor.execute(
            "UPDATE sm_minute "
            "SET rain_in_tot_qc = coalesce(%s, rain_in_tot_qc * %s), "
            "rain_in_tot_f = 'E' WHERE valid > %s and valid <= %s "
            "and station = %s",
            (
                value,
                multi,
                row["valid"],
                row["valid"] + timedelta(minutes=60),
                station,
            ),
        )
        LOG.info(
            "minute %s multi %.4f value %.4f rows updated %s",
            row["valid"],
            multi,
            value,
            cursor.rowcount,
        )
    cursor.close()
    pgconn.commit()


@click.command()
@click.option(
    "--date",
    "dt",
    type=click.DateTime(),
    required=True,
    help="Date to process",
)
def main(dt: datetime):
    """Go main go"""
    dt = dt.date()
    LOG.info("Processing date: %s", dt)
    nt = NetworkTable("ISUSM")

    # Get our obs
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            "SELECT station, rain_in_tot from sm_daily where "
            "valid = %s ORDER by station ASC",
            conn,
            params=(dt,),
            index_col="station",
        )
    if df.empty:
        LOG.warning("no observations found for %s, aborting", dt)
        return
    df["obs"] = df["rain_in_tot"]
    hdf = get_hdf(nt, dt)
    if hdf.empty:
        LOG.warning("hdf is empty, abort for %s", dt)
        return

    # lets try some QC
    for station in df.index.values:
        # the daily total is 12 CST to 12 CST, so that is always 6z
        # so we want the 7z total
        sts = utc(dt.year, dt.month, dt.day, 7)
        ets = sts + timedelta(hours=24)
        # OK, get our data
        ldf = hdf[
            (hdf["station"] == station)
            & (hdf["valid"] >= sts)
            & (hdf["valid"] < ets)
        ]
        df.at[station, "stage4"] = ldf["precip_in"].sum()

    df["diff"] = df["obs"] - df["stage4"]
    for station, row in df.iterrows():
        LOG.info("%s stage4: %s ob: %s", station, row["stage4"], row["obs"])
        # We want to QC the case of having too low of precip.
        # How low is too low?
        # if stageIV > 0.1 and obs < 0.05
        # Or if obs is 1 inch over stage4
        if (row["stage4"] > 0.1 and row["obs"] < 0.05) or (
            (row["obs"] - row["stage4"]) > 1
        ):
            # print to keep email log more pretty
            print(
                f"ISUSM fix_precip {dt} {station} "
                f"stageIV: {row['stage4']:.2f} obs: {row['obs']:.2f}"
            )
            print_debugging(station)
            if station == "MCSI4":
                LOG.warning("Not updating Marcus")
                set_iemacces(station, dt, row["obs"])
                continue
            update_precip(dt, station, hdf)
        else:
            set_iemacces(station, dt, row["obs"])


if __name__ == "__main__":
    main()
