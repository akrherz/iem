"""QC high/low temperature against IEMRE.

Called from RUN_2AM.sh for yesterday and ten days ago.
"""

import click
import httpx
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.util import convert_value, logger
from sqlalchemy import text

LOG = logger()


def setaccess(cursor, iemid, col, dt, newval):
    """We have something to set."""
    tmpf = convert_value(newval, "degC", "degF")
    cursor.execute(
        f"""
        UPDATE summary_{dt.year} SET {col}_tmpf = %s WHERE
        iemid = %s and day = %s
        """,
        (tmpf, int(iemid), dt),
    )


def setval(cursor, station, col, ob, dt, newval):
    """We have something to set."""
    LOG.warning("%s[%s] %s %s -> %s [E]", station, dt, col, ob, newval)
    cursor.execute(
        f"""
        UPDATE sm_daily SET tair_c_{col}_qc = %s, tair_c_{col}_f = 'E' WHERE
        station = %s and valid = %s
        """,
        (newval, station, dt),
    )


def check_date(dt):
    """Look this date over and compare with IEMRE."""
    nt = NetworkTable("ISUSM", only_online=False)
    with get_sqlalchemy_conn("isuag") as conn:
        obs = pd.read_sql(
            text(
                """
                select station, tair_c_avg_qc, tair_c_max_qc,
                tair_c_min_qc from sm_daily where valid = :date
                """
            ),
            conn,
            params={"date": dt},
            index_col="station",
        )
    # Merge in IEMRE
    for station in obs.index:
        # Go fetch me the IEMRE value!
        uri = (
            f"http://mesonet.agron.iastate.edu/iemre/daily/{dt:%Y-%m-%d}/"
            f"{nt.sts[station]['lat']:.2f}/"
            f"{nt.sts[station]['lon']:.2f}/json"
        )
        j = httpx.get(uri, timeout=60).json()
        iemre = j["data"][0]
        obs.at[station, "iemid"] = nt.sts[station]["iemid"]
        obs.at[station, "iemre_min"] = convert_value(
            iemre["daily_low_f"], "degF", "degC"
        )
        obs.at[station, "iemre_max"] = convert_value(
            iemre["daily_high_f"], "degF", "degC"
        )

    obs["iemre_avg"] = (obs["iemre_min"] + obs["iemre_max"]) / 2.0

    pgconn, cursor = get_dbconnc("isuag")
    ipgconn, icursor = get_dbconnc("iem")
    for col in ["min", "max", "avg"]:
        suspect = obs[
            ((obs[f"iemre_{col}"] - obs[f"tair_c_{col}_qc"]).abs() > 2)
            | obs[f"tair_c_{col}_qc"].isnull()
        ]
        for station, row in suspect.iterrows():
            setval(
                cursor,
                station,
                col,
                row[f"tair_c_{col}_qc"],
                dt,
                row[f"iemre_{col}"],
            )
            if col != "avg":
                setaccess(icursor, row["iemid"], col, dt, row[f"iemre_{col}"])
    cursor.close()
    pgconn.commit()
    icursor.close()
    ipgconn.commit()


@click.command()
@click.option("--date", "dt", type=click.DateTime(), help="Date to process")
def main(dt):
    """Go Main Go."""
    dt = dt.date()
    check_date(dt)


if __name__ == "__main__":
    main()
