"""
 We need to look at the raw SNET datafiles and see what the daily precip should
 have been.  Due to complex issues with clocks, we should see the largest
 value in the raw data file and use that for the daily precip value stored in
 the summary database

 Runs from: RUN_MIDNIGHT.sh

"""
from __future__ import print_function
import datetime
import sys
import os

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def process(icursor, ts):
    """process this timestamp"""
    nt = NetworkTable(["KCCI", "KIMT", "KELO"])
    for nwsli in nt.sts.keys():
        nwnid = nt.sts[nwsli]["nwn_id"]
        #
        fp = "/mesonet/ARCHIVE/raw/snet/%s/%s.dat" % (
            ts.strftime("%Y_%m/%d"),
            nwnid,
        )
        if not os.path.isfile(fp):
            # print 'Missing: %s' % (fp,)
            continue

        maxPrecip = -99
        lines = open(fp).readlines()
        for line in lines[-100:]:
            tokens = line.split(",")
            pDay = float(tokens[9][:-2])
            if pDay > maxPrecip:
                maxPrecip = pDay

        if maxPrecip < 0:
            continue

        sql = """UPDATE summary_%s s SET pday = %s FROM stations t
            WHERE t.id = '%s' and t.iemid = s.iemid
            and day = '%s' """ % (
            ts.year,
            maxPrecip,
            nwsli,
            ts.strftime("%Y-%m-%d"),
        )
        icursor.execute(sql)


def main(argv):
    """Go Main Go"""
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()
    ts = datetime.datetime.now() - datetime.timedelta(days=1)
    if len(argv) == 4:
        ts = datetime.datetime(
            int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
        )
    process(icursor, ts)
    icursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
