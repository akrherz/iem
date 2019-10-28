"""
Dump iem database of OT data to archive
Runs at 00 and 12 UTC
"""
from __future__ import print_function
import datetime
import sys
import psycopg2.extras
from pyiem.util import get_dbconn, utc

OTHER = get_dbconn("other")
IEM = get_dbconn("iem")


def dowork(ts, ts2):
    """Process between these two timestamps please"""
    # Delete any obs from yesterday
    ocursor = OTHER.cursor(cursor_factory=psycopg2.extras.DictCursor)
    icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = "DELETE from t%s WHERE valid >= '%s' and valid < '%s'" % (
        ts.year,
        ts,
        ts2,
    )
    ocursor.execute(sql)

    # Get obs from Access
    sql = """SELECT c.*, t.id from current_log c JOIN stations t on
        (t.iemid = c.iemid) WHERE valid >= '%s' and valid < '%s'
        and t.network = 'OT'""" % (
        ts,
        ts2,
    )
    icursor.execute(sql)
    if icursor.rowcount == 0:
        print("ot2archive found no results for ts: %s ts2: %s" % (ts, ts2))

    for row in icursor:
        pday = 0
        if row["pday"] is not None and float(row["pday"]) > 0:
            pday = row["pday"]
        alti = row["alti"]
        if alti is None and row["mslp"] is not None:
            alti = row["mslp"] * 0.03
        sql = """INSERT into t%s (station, valid, tmpf, dwpf, drct, sknt, alti,
             pday, gust, c1tmpf, srad) values
             ('%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """ % (
            ts.year,
            row["id"],
            row["valid"],
            (row["tmpf"] or "Null"),
            (row["dwpf"] or "Null"),
            (row["drct"] or "Null"),
            (row["sknt"] or "Null"),
            (alti or "Null"),
            pday,
            (row["gust"] or "Null"),
            (row["c1tmpf"] or "Null"),
            (row["srad"] or "Null"),
        )
        ocursor.execute(sql)

    ocursor.close()
    OTHER.commit()


def main(argv):
    """Run for a given UTC date"""
    ts = utc(int(argv[1]), int(argv[2]), int(argv[3]))
    ts2 = ts + datetime.timedelta(hours=24)
    dowork(ts, ts2)


if __name__ == "__main__":
    main(sys.argv)
