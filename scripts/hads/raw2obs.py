"""Convert the raw table data into something faster for website to use"""
import datetime
import sys
from io import StringIO
from zoneinfo import ZoneInfo

import pandas as pd
from pyiem.util import convert_value, get_dbconn, get_sqlalchemy_conn, logger

LOG = logger()


def v(val):
    """lame"""
    if pd.isnull(val):
        return "null"
    return val


def do(ts):
    """Do a UTC date's worth of data"""
    pgconn = get_dbconn("hads")
    table = ts.strftime("raw%Y_%m")
    sts = datetime.datetime(ts.year, ts.month, ts.day).replace(
        tzinfo=ZoneInfo("UTC")
    )
    ets = sts + datetime.timedelta(hours=24)
    with get_sqlalchemy_conn("hads") as conn:
        df = pd.read_sql(
            f"""
            SELECT station, valid, substr(key, 1, 3) as vname, value
            from {table} WHERE valid >= %s and valid < %s and
            substr(key, 1, 3) in ('USI', 'UDI', 'TAI', 'TDI')
            and value > -999
        """,
            conn,
            params=(sts, ets),
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
    cursor.copy_from(
        data,
        table,
        columns=("station", "valid", "tmpf", "dwpf", "drct", "sknt"),
        null="null",
    )
    cursor.close()
    pgconn.commit()


def main(argv):
    """Go Main Go"""
    ts = datetime.date.today() - datetime.timedelta(days=1)
    if len(argv) == 4:
        ts = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    do(ts)


if __name__ == "__main__":
    main(sys.argv)
