"""Hey, we are going to QC precipitation, somehow!

Implementation Thoughts:

1. We are really only caring about the situation of having too low of precip
2. We'll take the stage IV product as gospel
3. We won't update the 'raw' precip tables
4. This uses the flag 'E' for estimated

"""
import datetime
import sys

import pytz
import requests
import pandas as pd
from metpy.units import units
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger, utc

LOG = logger()


def print_debugging(station):
    """Add some more details to the output messages to help with ticket res"""
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT valid, rain_mm_tot / 25.4, rain_mm_tot_qc / 25.4, "
        "rain_mm_tot_f from sm_daily WHERE station = %s and "
        "(rain_mm_tot > 0 or rain_mm_tot_qc > 0) ORDER by valid DESC LIMIT 10",
        (station,),
    )
    LOG.info("     Date           Obs     QC  Flag")
    for row in cursor:
        LOG.info("     %s   %5.2f  %5.2f %5s", *row)


def get_hdf(nt, date):
    """Fetch the hourly dataframe for this network"""
    # Get our stage IV hourly totals
    rows = []
    for station in nt.sts:
        # service provides UTC dates, so we need to request two days
        for ldate in [date, date + datetime.timedelta(days=1)]:
            uri = ("http://iem.local/json/stage4/%.2f/%.2f/%s") % (
                nt.sts[station]["lon"],
                nt.sts[station]["lat"],
                ldate.strftime("%Y-%m-%d"),
            )
            try:
                j = requests.get(uri).json()
            except Exception as exp:
                LOG.info("JSON stage4 service failed\n%s\n%s", uri, exp)
                continue
            for entry in j["data"]:
                rows.append(
                    dict(
                        station=station,
                        valid=datetime.datetime.strptime(
                            entry["end_valid"], "%Y-%m-%dT%H:%M:%SZ"
                        ).replace(tzinfo=pytz.UTC),
                        precip_in=entry["precip_in"],
                    )
                )
    df = pd.DataFrame(rows)
    df.fillna(0, inplace=True)
    return df


def set_iemacces(station, date, precip_inch):
    """Set the precip value for IEMAccess."""
    # update iemaccess
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()
    LOG.debug("Update iemaccess %s %s %.4f", station, date, precip_inch)
    cursor.execute(
        "UPDATE summary s SET pday = %s FROM stations t WHERE "
        "t.iemid = s.iemid and s.day = %s and t.id = %s and "
        "t.network = 'ISUSM'",
        (precip_inch, date, station),
    )
    cursor.close()
    pgconn.commit()


def update_precip(date, station, hdf):
    """Do the update work"""
    sts = utc(date.year, date.month, date.day, 7)
    ets = sts + datetime.timedelta(hours=24)
    ldf = hdf[
        (hdf["station"] == station)
        & (hdf["valid"] >= sts)
        & (hdf["valid"] < ets)
    ]

    newpday = ldf["precip_in"].sum()
    newpday_mm = (units("inch") * newpday).to(units("mm")).m
    set_iemacces(station, date, newpday)
    # update isusm
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor()
    # daily
    cursor.execute(
        "UPDATE sm_daily SET rain_mm_tot_qc = %s, rain_mm_tot_f = 'E' "
        "WHERE valid = %s and station = %s",
        (newpday_mm, date, station),
    )
    for _, row in ldf.iterrows():
        # hourly
        LOG.debug(
            "set hourly %s %s %s", station, row["valid"], row["precip_in"]
        )
        total = (units("mm") * row["precip_in"]).to(units("inch")).m
        cursor.execute(
            "UPDATE sm_hourly SET rain_mm_tot_qc = %s, rain_mm_tot_f = 'E' "
            "WHERE valid = %s and station = %s",
            (total, row["valid"], station),
        )
        # For minute data, we just apply a linear offset
        cursor.execute(
            "SELECT sum(rain_in_tot) from sm_minute WHERE station = %s and "
            "valid > %s and valid <= %s",
            (
                station,
                row["valid"],
                row["valid"] + datetime.timedelta(minutes=60),
            ),
        )
        if cursor.rowcount == 0:
            LOG.info("Can't adjust %s %s, no data", station, row["valid"])
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
                row["valid"] + datetime.timedelta(minutes=60),
                station,
            ),
        )
        LOG.debug(
            "minute %s multi %.4f value %.4f rows updated %s",
            row["valid"],
            multi,
            value,
            cursor.rowcount,
        )
    cursor.close()
    pgconn.commit()


def main(argv):
    """ Go main go """
    date = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    LOG.debug("Processing date: %s", date)
    pgconn = get_dbconn("isuag")
    nt = NetworkTable("ISUSM")

    # Get our obs
    df = read_sql(
        "SELECT station, rain_mm_tot from sm_daily where "
        "valid = %s ORDER by station ASC",
        pgconn,
        params=(date,),
        index_col="station",
    )
    if df.empty:
        LOG.info("no observations found for %s, aborting", date)
        return
    # Covert to inches
    df["obs"] = (units("mm") * df["rain_mm_tot"].values).to(units("inch")).m
    hdf = get_hdf(nt, date)
    if hdf.empty:
        LOG.info("hdf is empty, abort fix_precip for %s", date)
        return

    # lets try some QC
    for station in df.index.values:
        # the daily total is 12 CST to 12 CST, so that is always 6z
        # so we want the 7z total
        sts = utc(date.year, date.month, date.day, 7)
        ets = sts + datetime.timedelta(hours=24)
        # OK, get our data
        ldf = hdf[
            (hdf["station"] == station)
            & (hdf["valid"] >= sts)
            & (hdf["valid"] < ets)
        ]
        df.at[station, "stage4"] = ldf["precip_in"].sum()

    df["diff"] = df["obs"] - df["stage4"]
    for station, row in df.iterrows():
        LOG.debug("%s stage4: %s ob: %s", station, row["stage4"], row["obs"])
        # We want to QC the case of having too low of precip.
        # How low is too low?
        # if stageIV > 0.1 and obs < 0.05
        if row["stage4"] > 0.1 and row["obs"] < 0.05:
            LOG.info(
                "ISUSM fix_precip %s %s stageIV: %.2f obs: %.2f",
                date,
                station,
                row["stage4"],
                row["obs"],
            )
            print_debugging(station)
            if station == "MCSI4":
                LOG.info("Not updating Marcus")
                continue
            update_precip(date, station, hdf)
        else:
            set_iemacces(station, date, row["obs"])


if __name__ == "__main__":
    main(sys.argv)
