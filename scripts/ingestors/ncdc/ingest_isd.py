"""HMMMM
"""
from __future__ import print_function
import sys
import subprocess
import os
import datetime

import pytz
from pyiem.ncei import ds3505
import psycopg2
import tqdm


def main(argv):
    """Go"""
    pgconn = psycopg2.connect(database='asos', host='iemdb')
    airforce = int(argv[1])
    wban = int(argv[2])
    faa = argv[3]
    year = int(argv[4])
    year2 = int(argv[5])
    failedyears = []
    msgs = []
    for year in tqdm.tqdm(range(year, year2)):
        sts = datetime.datetime(year, 1, 1).replace(tzinfo=pytz.utc)
        ets = sts.replace(year=year+1)
        cursor = pgconn.cursor()
        lfn = "%06i-%05i-%s" % (airforce, wban, year)
        if not os.path.isfile(lfn):
            fn = "ftp://ftp.ncdc.noaa.gov/pub/data/noaa/%s/%s.gz" % (year, lfn)
            subprocess.call("wget -q -O %s.gz %s" % (lfn, fn),
                            shell=True)
            if (not os.path.isfile(lfn+".gz") or
                    os.path.getsize(lfn+".gz") == 0):
                failedyears.append(year)
                continue
            subprocess.call("gunzip %s.gz" % (lfn, ), shell=True,
                            stderr=subprocess.PIPE)
        added = 0
        bad = 0
        removed = 0
        skipped = 0
        for line in open(lfn):
            data = ds3505.parser(line.strip(), faa, add_metar=True)
            if data is None:
                bad += 1
                continue
            if added == 0:
                cursor.execute("""
                    DELETE from alldata where station = %s
                    and valid >= %s and valid < %s
                """, (faa, sts, ets))
                removed = cursor.rowcount
            res = ds3505.sql(cursor, faa, data)
            if res is None:
                skipped += 1
            else:
                added += 1
        msgs.append(("  %s: %s added: %s removed: %s bad: %s"
                     " skipped: %s") % (year, faa, added, removed, bad,
                                        skipped))
        cursor.close()
        pgconn.commit()
        year += 1
    print(" failed years: %s" % (failedyears, ))
    print("\n".join(msgs))


if __name__ == '__main__':
    os.chdir("/mesonet/tmp")
    main(sys.argv)
