"""Look into our archive and make sure we have what we need!"""

import datetime
import subprocess
import os
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("mesosite", user="nobody")
    mcursor = pgconn.cursor()

    mcursor.execute(
        """SELECT sts, template, interval from archive_products
        WHERE id = 44"""
    )
    row = mcursor.fetchone()

    tpl = (
        row[1]
        .replace(
            "https://mesonet.agron.iastate.edu/archive/data/",
            "/mesonet/ARCHIVE/data/",
        )
        .replace("%i", "%M")
    )
    now = row[0]
    interval = datetime.timedelta(minutes=row[2])
    ets = datetime.datetime.now().replace(tzinfo=now.tzinfo)

    while now < ets:
        fp = now.strftime(tpl)
        if not os.path.isfile(fp):
            cmd = "python q2_5min_rate.py %s" % (
                now.strftime("%Y %m %d %H %M"),
            )
            subprocess.call(cmd, shell=True)
        now += interval


if __name__ == "__main__":
    main()
