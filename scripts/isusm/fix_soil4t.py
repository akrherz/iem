"""Quality control our 4 inch soil temperature data.

Called from soilm_ingest.py
"""

import json
from datetime import date, datetime

import click
import httpx
import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.util import convert_value, logger
from sqlalchemy.engine import Connection

LOG = logger()


def setval(conn: Connection, station, col: str, ob, dt: date, newval):
    """We have something to set."""
    LOG.warning(
        "%s %s %s %.1f -> %.1f (%.1f) [E]",
        station,
        dt,
        col,
        ob,
        newval,
        newval - ob,
    )
    conn.execute(
        sql_helper(
            """
        UPDATE sm_daily SET {col}_qc = :newval, {col}_f = 'E' WHERE
        station = :station and valid = :valid
        """,
            col=col,
        ),
        {
            "station": station,
            "valid": dt,
            "newval": newval,
        },
    )


def do_checks(qcdf: pd.DataFrame, conn: Connection, dt: date, col: str):
    # We'll take any value
    obcol = f"ob_{col}"
    for station, row in qcdf[qcdf["useme"]].iterrows():
        # If Ob is None, we have no choice
        if row[obcol] is None:
            setval(conn, station, col, row[obcol], dt, row[col])
            continue
        # Passes if value within 2 C of IEMRE
        if abs(row[obcol] - row[col]) <= 2:
            LOG.info(
                "%s passes2c %s ob:%.2f iemre:%.2f",
                station,
                obcol,
                row[obcol],
                row[col],
            )
            continue
        # Passes if within bounds of Iowa values
        if qcdf[col].min() <= row[obcol] <= qcdf[col].max():
            LOG.info(
                "%s passesbnd %s ob:%.2f iemre:%.2f",
                station,
                col,
                row[obcol],
                row[col],
            )
            continue
        # We fail
        setval(conn, station, col, row[obcol], dt, row[col])


@with_sqlalchemy_conn("isuag")
def check_date(dt: date, conn: Connection = None):
    """Look this date over and compare with IEMRE."""

    nt = NetworkTable("ISUSM")
    res = conn.execute(
        sql_helper("""
    SELECT station, t4_c_avg, t4_c_min, t4_c_max from sm_daily where
    valid = :valid ORDER by station ASC"""),
        {"valid": dt},
    )
    qcrows = []
    for row in res.mappings():
        station = row["station"]
        # Go fetch me the IEMRE value!
        uri = (
            f"https://mesonet.agron.iastate.edu/iemre/daily/{dt:%Y-%m-%d}/"
            f"{nt.sts[station]['lat']:.2f}/"
            f"{nt.sts[station]['lon']:.2f}/json"
        )
        res = httpx.get(uri, timeout=60)
        j = json.loads(res.content)
        iemre = j["data"][0]
        iemre_low = convert_value(iemre["soil4t_low_f"], "degF", "degC")
        iemre_high = convert_value(iemre["soil4t_high_f"], "degF", "degC")
        if iemre_high is None or iemre_low is None:
            LOG.warning("%s %s IEMRE is missing", station, dt)
            continue
        iemre_avg = (iemre_high + iemre_low) / 2.0
        useme = True
        if nt.sts[station]["attributes"].get("NO_4INCH") == "1":
            LOG.info("Skipping %s as NO_4INCH", station)
            useme = False
        qcrows.append(
            {
                "station": station,
                "ob_t4_c_avg": row["t4_c_avg"],
                "ob_t4_c_min": row["t4_c_min"],
                "ob_t4_c_max": row["t4_c_max"],
                "useme": useme,
                "t4_c_avg": iemre_avg,
                "t4_c_min": iemre_low,
                "t4_c_max": iemre_high,
            }
        )
    qcdf = pd.DataFrame(qcrows).set_index("station")
    for col in ["t4_c_avg", "t4_c_min", "t4_c_max"]:
        do_checks(qcdf, conn, dt, col)
    conn.commit()


@click.command()
@click.option("--date", "dt", type=click.DateTime(), required=True)
def main(dt: datetime):
    """Go Main Go."""
    check_date(dt.date())


if __name__ == "__main__":
    main()
