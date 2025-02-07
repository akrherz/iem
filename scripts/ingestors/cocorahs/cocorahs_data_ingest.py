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
from pyiem.database import get_sqlalchemy_conn, sql_helper
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


def main(conn, dt: Optional[date]) -> None:
    """Go Main Go"""
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
        if local_valid.year < 2000:
            LOG.info("Skipping %s %s as <2000", sid, local_valid)
            continue
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
        params = {
            "iemid": iemid,
            "d": local_valid.date(),
            "valid": valid,
            "pday": pday,
            "snow": snow,
            "snow_swe": snow_swe,
            "snowd": snowd,
            "snowd_swe": snowd_swe,
            "updated": updated,
        }
        res = conn.execute(
            sql_helper(
                "select iemid from {table} where iemid = :iemid and day = :d",
                table=table,
            ),
            params,
        )
        if res.rowcount == 0:
            conn.execute(
                sql_helper(
                    "INSERT into {table}(iemid, day) VALUES (:iemid, :d)",
                    table=table,
                ),
                params,
            )
        conn.execute(
            sql_helper(
                """
            UPDATE {table} SET obvalid = :valid,
            precip = :pday, snow = :snow, snow_swe = :snow_swe,
            snowd = :snowd, snowd_swe = :snowd_swe, updated = :updated
            WHERE iemid = :iemid and day = :d
        """,
                table=table,
            ),
            params,
        )


@click.command()
@click.option("--date", "dt", type=click.DateTime())
def frontend(dt: Optional[datetime]):
    """Do Logic."""
    if dt is not None:
        dt = dt.date()
    with get_sqlalchemy_conn("coop") as conn:
        main(conn, dt)
        conn.commit()


if __name__ == "__main__":
    frontend()
