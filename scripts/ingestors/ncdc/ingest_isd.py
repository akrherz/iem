"""HMMMM
"""
from __future__ import print_function
import sys
import subprocess
import os

import tqdm
from pyiem.ncei import ds3505
from pyiem.util import get_dbconn, utc

ADD_ONLY = True


def main(argv):
    """Go"""
    pgconn = get_dbconn('asos')
    airforce = int(argv[1])
    wban = int(argv[2])
    faa = argv[3]
    year = int(argv[4])
    year2 = int(argv[5])
    failedyears = []
    msgs = []
    dbid = faa if len(faa) == 4 and faa[0] != 'K' else faa[1:]
    for year in tqdm.tqdm(range(year, year2)):
        sts = utc(year, 1, 1)
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
        # ignore any bad bytes, sigh
        for line in open(lfn, errors='ignore'):
            data = ds3505.parser(line.strip(), faa, add_metar=True)
            if data is None:
                bad += 1
                continue
            if added == 0 and not ADD_ONLY:
                cursor.execute("""
                    DELETE from alldata where station = %s
                    and valid >= %s and valid < %s
                """, (dbid, sts, ets))
                if cursor.rowcount > 0:
                    print("deleted %s rows for %s" % (cursor.rowcount, dbid))
                removed = cursor.rowcount
            if ADD_ONLY:
                # check for existing ob
                cursor.execute("""
                    SELECT valid from alldata where station = %s and valid = %s
                """, (dbid, data['valid']))
                if cursor.rowcount > 0:
                    skipped += 1
                    continue
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
