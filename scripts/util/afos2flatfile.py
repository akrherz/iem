"""Dump what I have stored in the AFOS database to flat files
"""
import datetime
import subprocess

from pyiem.util import get_dbconn, logger, noaaport_text, utc

LOG = logger()
pgconn = get_dbconn("afos", user="nobody")
cursor = pgconn.cursor()

pils = "DSW|SQW"


def workflow(date):
    """ Process a given UTC date """
    sts = utc(date.year, date.month, date.day)
    ets = sts + datetime.timedelta(hours=24)
    for pil in pils.split("|"):
        cursor.execute(
            """
            SELECT data from products WHERE
            entered >= %s and entered < %s and
            substr(pil,1,3) = %s ORDER by entered ASC
            """,
            (sts, ets, pil),
        )
        if cursor.rowcount == 0:
            continue
        LOG.info("%s %s %s", date, pil, cursor.rowcount)
        with open("/tmp/afos.tmp", "w") as fh:
            for row in cursor:
                fh.write(noaaport_text(row[0]))

        cmd = "data a %s0000 bogus text/noaaport/%s_%s.txt txt" % (
            date.strftime("%Y%m%d"),
            pil,
            date.strftime("%Y%m%d"),
        )
        cmd = "pqinsert -p '%s' /tmp/afos.tmp" % (cmd,)
        subprocess.call(cmd, shell=True)


def main():
    """Go Main"""
    sts = datetime.datetime(2018, 1, 1)
    ets = datetime.datetime(2020, 1, 28)
    interval = datetime.timedelta(days=1)
    now = sts
    while now < ets:
        workflow(now)
        now += interval


if __name__ == "__main__":
    # go
    main()
