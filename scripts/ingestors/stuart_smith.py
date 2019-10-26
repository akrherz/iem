"""
 My belief is that the data is always in standard time
"""
from __future__ import print_function
import subprocess
import datetime
import os
import sys

from pyiem.util import get_dbconn


def main():
    """Go main go"""
    pgconn = get_dbconn("other")
    mcursor = pgconn.cursor()

    # Do the bubbler file
    mcursor.execute("""SELECT max(valid) from ss_bubbler""")
    row = mcursor.fetchone()
    maxts = (
        None
        if row[0] is None
        else datetime.datetime.strptime(
            row[0].strftime("%m/%d/%y %H:%M:%S"), "%m/%d/%y %H:%M:%S"
        )
    )

    if not os.path.isfile("/mnt/rootdocs/Bubbler.csv"):
        sys.exit()

    for line in open("/mnt/rootdocs/Bubbler.csv"):
        tokens = line.strip().split(",")
        if len(tokens) < 2 or line[0] in ["S", "G"] or len(line) > 300:
            continue
        # Sometimes the data is corrupted :(
        if len(tokens[0]) > 12:
            continue
        try:
            ts = datetime.datetime.strptime(
                "%s %s" % (tokens[0], tokens[1]), "%m/%d/%Y %H:%M:%S"
            )
        except Exception:
            continue
        if maxts and ts <= maxts:
            continue
        if len(tokens) == 3:
            tokens.append(None)
        if len(tokens) == 4:
            tokens.append(None)
        mcursor.execute(
            """
            INSERT into ss_bubbler values (%s, %s, %s, %s)
        """,
            (ts, tokens[2], tokens[3], tokens[4]),
        )

    # Do the STS_GOLD file
    maxts = {}
    mcursor.execute(
        """SELECT max(valid at time zone 'UTC'), site_serial
                    from ss_logger_data GROUP by site_serial"""
    )
    for row in mcursor:
        # Max standard time value
        maxts[row[1]] = row[0] - datetime.timedelta(hours=6)
    # Don't accept data from the future, well, within some reason
    ceiling = datetime.datetime.utcnow() - datetime.timedelta(hours=3)

    for sid in [9100104, 9100135, 9100131, 9100156]:
        ts = maxts.get(sid, datetime.datetime(2000, 1, 1))
        ticks = int(ts.strftime("%s"))
        sql = (
            "SELECT * from logger_data WHERE site_serial = %s" " and Date_time > %s"
        ) % (sid, ticks)
        proc = subprocess.Popen(
            ("echo '%s' | mdb-sql -p " "/mnt/sts_gold/sts_gold.mdb") % (sql,),
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

        data = proc.stdout.read().decode("utf-8")
        for linenum, line in enumerate(data.split("\n")):
            tokens = line.split("\t")
            if len(tokens) < 13 or linenum < 2:
                continue
            # site_serial = int(tokens[1])
            ts = datetime.datetime.strptime(tokens[2], "%m/%d/%y %H:%M:%S")
            if ts >= ceiling:
                continue
            tokens[2] = ts.strftime("%Y-%m-%d %H:%M:%S-0600")
            mcursor.execute(
                """
                INSERT into ss_logger_data values (%s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                tokens,
            )

    mcursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
