"""
Harry Hillaker kindly provides a monthly file of his QC'd COOP observations
This script processes them into something we can insert into the IEM database
"""
from __future__ import print_function
import sys
import re
import datetime
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn
from pyiem.reference import TRACE_VALUE

# This is not good, but necessary.  We translate some sites into others, so to
# maintain a long term record.
STCONV = {
    "IA6199": "IA6200",  # Oelwein
    "IA3288": "IA3290",  # Glenwood
    "IA4963": "IA8266",  # Lowden becomes Tipton
    "IA7892": "IA4049",  # Stanley becomes Independence
    "IA0214": "IA0213",  # Anamosa
    "IA2041": "IA3980",  # Dakota City becomes Humboldt
}
FIELDS = ["high", "low", "precip", "snow", "snowd"]
PGCONN = get_dbconn("coop")


def get_current(year, month):
    """Get our current data"""
    # pandas does not use datetime.date objects for indices
    return read_sql(
        """
    SELECT *, high as new_high, low as new_low, precip as new_precip,
    snow as new_snow, snowd as new_snowd,
    extract(day from day)::int as dom
    from alldata_ia where year = %s and month = %s
    ORDER by day ASC, station ASC
    """,
        PGCONN,
        params=(year, month),
        index_col=["station", "dom"],
    )


def safef(val):
    """Safe float"""
    val = val.strip()
    if val in ["M", "C", "*", "?", ""]:
        return None
    if val == "T":
        return TRACE_VALUE
    return float(val)


def safef2(val):
    """hack"""
    if pd.isnull(val):
        return None
    return val


def add_rows(cursor, df, dbid, ts):
    """Create entries"""
    print("Adding month of database entries for station: %s" % (dbid,))
    now = ts.replace(day=1)
    ets = (now + datetime.timedelta(days=35)).replace(day=1)
    interval = datetime.timedelta(days=1)
    while now < ets:
        df.loc[(dbid, now.day), :] = None
        if (dbid, now.day) not in df.index:
            sys.exit()
        cursor.execute(
            """INSERT INTO alldata_ia
                (station, day, sday, year, month)
                VALUES (%s, %s, %s, %s, %s)
                """,
            (dbid, now, now.strftime("%m%d"), now.year, now.month),
        )
        now += interval


def print_diags(df):
    """Print out some diagnostics on how well we did!"""
    # Create a difference column for each var
    # df.reset_index(inplace=True)

    print("==== bulk stats to report for website news item ====")
    for field, threshold in zip(FIELDS, [2, 2, 0.2, 2, 2]):
        df["diff_" + field] = df["new_" + field] - df[field]
        df["diff_" + field + "_abs"] = df["diff_" + field].abs()
        df2 = df[df["diff_" + field].abs() >= threshold]
        print(
            (
                "var: %6s bias: %6.2f std: %6.2f found: "
                "%4s entries out of bnds %s"
            )
            % (
                field,
                df2["diff_" + field].mean(),
                df2["diff_" + field].std(),
                len(df2.index),
                threshold,
            )
        )

    print("==== worst offenders ====")
    for field in FIELDS:
        sdf = df.sort_values("diff_" + field + "_abs", ascending=False)
        print(" ---> %s" % (field,))
        print(
            df.loc[sdf.head().index][["diff_" + field, field, "new_" + field]]
        )


def main(argv):
    """Go Main!"""
    year = int(argv[1])
    month = int(argv[2])
    df = get_current(year, month)
    print("Found %s previous database entries" % (len(df.index),))

    fn = "/mesonet/data/harry/%s/SCIA%s%02i.txt" % (year, str(year)[2:], month)
    print("Processing File: %s" % (fn,))

    cursor = PGCONN.cursor()
    lines = open(fn, "r").readlines()

    hits = 0
    misses = 0
    for linenum, line in enumerate(lines):
        tokens = re.split(",", line.replace('"', ""))
        if len(tokens) < 15 or len(tokens[2]) != 4:
            misses += 1
            continue
        if not tokens[0] or tokens[2] == "YR" or tokens[0] == "YR":
            continue
        stid = tokens[0]
        dbid = "%s%04.0f" % ("IA", int(stid))
        dbid = STCONV.get(dbid, dbid)
        try:
            day = int(tokens[4])
            ts = datetime.date(int(tokens[2]), int(tokens[3]), day)
            if ts.month != month or ts.year != year:
                raise ValueError("bad!")
        except ValueError:
            print(
                ("ABORT! timefail yr:%s mo:%s dy:%s linenum:%s")
                % (tokens[2], tokens[3], tokens[4], linenum)
            )
            return
        if (dbid, day) not in df.index:
            add_rows(cursor, df, dbid, ts)
        df.at[(dbid, day), "new_high"] = safef(tokens[6])
        df.at[(dbid, day), "new_low"] = safef(tokens[8])
        df.at[(dbid, day), "new_precip"] = safef(tokens[12])
        df.at[(dbid, day), "new_snow"] = safef(tokens[14])
        df.at[(dbid, day), "new_snowd"] = safef(tokens[16])

        cursor.execute(
            """
            UPDATE alldata_ia SET high = %s, low= %s,
            precip = %s, snow = %s,
            snowd = %s
            WHERE station = %s and day = %s
            """,
            (
                safef2(df.at[(dbid, day), "new_high"]),
                safef2(df.at[(dbid, day), "new_low"]),
                safef2(df.at[(dbid, day), "new_precip"]),
                safef2(df.at[(dbid, day), "new_snow"]),
                safef2(df.at[(dbid, day), "new_snowd"]),
                dbid,
                ts,
            ),
        )
        if cursor.rowcount != 1:
            print(
                "ABORT: update not==1, %s %s cnt:%s"
                % (dbid, ts, cursor.rowcount)
            )
            return
        hits += 1

    print("    got %s good lines %s bad lines" % (hits, misses))
    print_diags(df)
    cursor.close()
    if len(argv) > 3:
        print("Skipping database commit as we are in regression mode")
        return
    PGCONN.commit()


if __name__ == "__main__":
    main(sys.argv)
