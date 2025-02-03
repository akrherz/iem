"""Convert the raw table data into something faster for website to use.

called from RUN_MIDNIGHT.sh
"""

from datetime import date, datetime, timedelta, timezone
from io import StringIO

import click
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn, sql_helper
from pyiem.util import convert_value, logger

LOG = logger()


def v(val):
    """lame"""
    if pd.isnull(val):
        return "null"
    return val


def do(ts: date):
    """Do a UTC date's worth of data"""
    pgconn = get_dbconn("hads")
    table = ts.strftime("raw%Y_%m")
    sts = datetime(ts.year, ts.month, ts.day, tzinfo=timezone.utc)
    ets = sts + timedelta(hours=24)
    with get_sqlalchemy_conn("hads") as conn:
        df = pd.read_sql(
            sql_helper(
                f"""
            SELECT station, valid, substr(key, 1, 3) as vname, value
            from {table} WHERE valid >= :sts and valid < :ets and
            substr(key, 1, 3) in ('USI', 'UDI', 'TAI', 'TDI')
            and value > -999
        """,
                table=table,
            ),
            conn,
            params={"sts": sts, "ets": ets},
            index_col=None,
        )
    if df.empty:
        LOG.info("No data found for date: %s", ts)
        return

    pdf = pd.pivot_table(
        df, values="value", index=["station", "valid"], columns="vname"
    )
    if "USI" in pdf.columns:
        pdf["sknt"] = convert_value(pdf["USI"].values, "mile / hour", "knot")

    table = ts.strftime("t%Y")
    data = StringIO()
    for (station, valid), row in pdf.iterrows():
        data.write(
            ("%s\t%s\t%s\t%s\t%s\t%s\n")
            % (
                station,
                valid.strftime("%Y-%m-%d %H:%M:%S+00"),
                v(row.get("TAI")),
                v(row.get("TDI")),
                v(row.get("UDI")),
                v(row.get("sknt")),
            )
        )
    cursor = pgconn.cursor()
    cursor.execute(
        f"DELETE from {table} WHERE valid between %s and %s", (sts, ets)
    )
    data.seek(0)
    sql = (
        f"copy {table}(station, valid, tmpf, dwpf, drct, sknt) from stdin "
        "with (delimiter E'\\t', null 'null')"
    )
    with cursor.copy(sql) as copy:
        copy.write(data.read())
    cursor.close()
    pgconn.commit()


@click.command()
@click.option("--date", "dt", required=True, type=click.DateTime())
def main(dt: datetime):
    """Go Main Go"""
    do(dt.date())


if __name__ == "__main__":
    main()
