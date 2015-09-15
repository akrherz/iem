"""Create the RR5 SHEF product that the Weather Bureau Desires

Run from RUN_20_AFTER.sh

"""
from pyiem.tracker import loadqc
import subprocess
import datetime
import os
import psycopg2
import numpy as np
import unittest
import tempfile


def mt(prefix, tmpf, depth, q):
    """Properly encode a value at depth into SHEF"""
    if tmpf is None or 'soil4' in q or np.isnan(tmpf):
        return ""
    val = float(depth)
    val += abs(tmpf) / 1000.0
    if tmpf < 0:
        val = 0 - val

    return "/%s %.3f" % (prefix, val)


def generate_rr5():
    """Create the RR5 Data"""
    qcdict = loadqc()
    data = ("\n\n\n"
            ": Iowa State University Soil Moisture Network\n"
            ": Data contact Daryl Herzmann akrherz@iastate.edu\n"
            ": File generated %s UTC\n"
            ) % (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"),)

    pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
    cursor = pgconn.cursor()
    cursor.execute("""SELECT id, valid, tmpf, c1tmpf, c2tmpf, c3tmpf, c4tmpf,
    c2smv, c3smv, c4smv, phour
    from current c JOIN stations t
    on (t.iemid = c.iemid) WHERE t.network = 'ISUSM' and
    valid > (now() - '90 minutes'::interval)""")
    for row in cursor:
        q = qcdict.get(row[0], dict())
        if 'tmpf' in q or row[2] is None:
            tmpf = "M"
        else:
            tmpf = "%.1f" % (row[2], )
        if 'precip' in q or row[10] is None:
            precip = "M"
        else:
            precip = "%.2f" % (row[10], )
        data += (".A %s %s C DH%s/TA %s%s%s%s%s\n"
                 ".A1 %s%s%s/PPH %s\n"
                 ) % (row[0], row[1].strftime("%Y%m%d"),
                      row[1].strftime("%H%M"), tmpf,
                      mt('TV', row[3], '4', q), mt('TV', row[4], '12', q),
                      mt('TV', row[5], '24', q), mt('TV', row[6], '50', q),
                      mt('MW', max([0, row[7]]), '12', q),
                      mt('MW', max([0, row[8]]), '24', q),
                      mt('MW', max([0, row[9]]), '50', q),
                      precip
                      )
    return data


def main():
    """Go Main Go"""
    rr5data = generate_rr5()
    print rr5data
    (tmpfd, tmpfn) = tempfile.mkstemp()
    os.write(tmpfd, rr5data)
    os.close(tmpfd)
    subprocess.call(("/home/ldm/bin/pqinsert -p 'SUADSMRR5DMX.dat' %s"
                     ) % (tmpfn,), shell=True)
    os.unlink(tmpfn)

if __name__ == '__main__':
    main()


# Test out our functions
class MyTest(unittest.TestCase):

    def test_mt(self):
        """Conversion of values to SHEF encoded values"""
        self.assertEquals(mt(4, 40, {}), "/TV 40.004")
        self.assertEquals(mt(-4, 40, {}), "/TV -40.004")
        self.assertEquals(mt(104, 40, {}), "/TV 40.104")
