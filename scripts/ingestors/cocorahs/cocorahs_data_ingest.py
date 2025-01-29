"""Process CoCoRaHS Stations!

https://data.cocorahs.org/cocorahs/Export/ExportManager.aspx

Called from RUN_20MIN.sh
"""

from datetime import date, datetime, timedelta, timezone
from io import StringIO
from typing import Optional
from zoneinfo import ZoneInfo

import click
import httpx
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.reference import TRACE_VALUE
from pyiem.util import logger, utc
from sqlalchemy import text

LOG = logger()


def safeP(v):
    """hack"""
    if type(v) is str:
        if v == "T":
            return TRACE_VALUE
        if v == "NA":
            return None
    return float(v)


def main(dt: Optional[date]) -> None:
    """Go Main Go"""
    with get_sqlalchemy_conn("coop") as conn:
        stations = pd.read_sql(
            text(
                """
    select iemid, id, tzname from stations where network ~* '_COCORAHS'
                """
            ),
            conn,
            index_col="id",
        )
    LOG.info("Found %s station defined", len(stations.index))
    dbconn, cursor = get_dbconnc("coop")

    if dt is not None:
        # Export for a given date
        url = (
            "http://data.cocorahs.org/export/exportreports.aspx"
            f"?ReportType=Daily&dtf=1&Format=CSV&"
            f"ReportDateType=date&Date={dt:%m/%d/%Y}&TimesInGMT=True"
        )
    else:
        # realtime, request the past six(?) hours
        since = utc() - timedelta(hours=2)
        url = (
            "https://data.cocorahs.org/export/exportreports.aspx"
            "?ReportType=Daily&dtf=1&Format=CSV&ReportDateType=timestamp"
            f"&Date={since:%-m/%d/%Y%%20%I:%m%%20%p}&"
            "TimesInGMT=True"
        )
    with StringIO() as sio:
        try:
            resp = httpx.get(url, timeout=30)
            resp.raise_for_status()
            sio.write(resp.text.replace(", ", ","))
        except Exception as exp:
            LOG.exception(exp)
            return
        sio.seek(0)
        obs = pd.read_csv(sio).set_index("StationNumber")
    LOG.info("Found %s obs to process", len(obs.index))
    for sid, row in obs.iterrows():
        if sid not in stations.index:
            if sid.startswith("IA-"):
                print(sid)
            continue
        tzinfo = ZoneInfo(stations.at[sid, "tzname"])
        valid = datetime.strptime(
            f"{row['ObservationDate']} {row['ObservationTime']}",
            "%Y-%m-%d %I:%M %p",
        ).replace(tzinfo=timezone.utc)
        local_valid = valid.astimezone(tzinfo)
        updated = datetime.strptime(
            row["DateTimeStamp"], "%Y-%m-%d %I:%M %p"
        ).replace(tzinfo=timezone.utc)
        pday = safeP(row["TotalPrecipAmt"])
        snow = safeP(row["NewSnowDepth"])
        snow_swe = safeP(row["NewSnowSWE"])
        snowd = safeP(row["TotalSnowDepth"])
        snowd_swe = safeP(row["TotalSnowSWE"])
        iemid = stations.at[sid, "iemid"]
        table = f"cocorahs_{local_valid:%Y}"
        cursor.execute(
            f"select iemid from {table} where iemid = %s and day = %s",
            (iemid, local_valid.date()),
        )
        if cursor.rowcount == 0:
            cursor.execute(
                f"INSERT into {table}(iemid, day) VALUES (%s, %s)",
                (iemid, local_valid.date()),
            )
        cursor.execute(
            f"""
            UPDATE {table} SET obvalid = %s,
            precip = %s, snow = %s, snow_swe = %s,
            snowd = %s, snowd_swe = %s, updated = %s
            WHERE iemid = %s and day = %s
        """,
            (
                valid,
                pday,
                snow,
                snow_swe,
                snowd,
                snowd_swe,
                updated,
                iemid,
                local_valid.date(),
            ),
        )

    cursor.close()
    dbconn.commit()


@click.command()
@click.option("--date", "dt", type=click.DateTime())
def frontend(dt: Optional[datetime]):
    """Do Logic."""
    if dt is not None:
        dt = dt.date()
    main(dt)


if __name__ == "__main__":
    frontend()
