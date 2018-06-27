"""
 Send the current_log history of SNET observations to its long term home

 The database partitioning is based on monthly tables based on UTC Time, so
 this runs at 0z and takes the previous GMT day...

"""
from __future__ import print_function
import datetime
import os
import subprocess

import pytz
import psycopg2.extras
from pyiem.util import get_dbconn


def formatter(val, precision):
    if val is None or isinstance(val, str):
        return 'None'
    fmt = '%%.%sf' % (precision,)
    return fmt % val


def main():
    """Go Main"""
    pgconn = get_dbconn('iem')
    icursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    utc = datetime.datetime.utcnow()
    utc = utc.replace(tzinfo=pytz.utc)
    # We want 0z today
    ets = utc.replace(hour=0, minute=0, second=0, microsecond=0)
    # 0z yesterday
    sts = ets - datetime.timedelta(days=1)

    # Collect obs from iemaccess
    sql = """SELECT c.*, t.id from current_log c JOIN stations t
        ON (t.iemid = c.iemid) WHERE valid >= %s and valid < %s and
        t.network IN ('KELO','KCCI','KIMT')"""
    args = (sts, ets)
    icursor.execute(sql, args)

    out = open('/tmp/snet_dbinsert.sql', 'w')
    out.write("DELETE from t%s WHERE valid >= '%s' and valid < '%s';\n" % (
        sts.strftime("%Y_%m"), sts, ets))
    out.write(("COPY t%s FROM stdin WITH NULL 'None';\n"
               ) % (sts.strftime("%Y_%m"), ))
    i = 0
    for row in icursor:
        if row['pmonth'] is None:
            row['pmonth'] = 0
        try:
            s = ("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n"
                 ) % (row.get('id'), row.get('valid'),
                      formatter(row.get('tmpf'), 0),
                      formatter(row.get('dwpf'), 0),
                      formatter(row.get('drct'), 0), row.get('sknt'),
                      row.get('pday'),
                      row.get('pmonth'), row.get('srad'), row.get('relh'),
                      row.get('pres'), formatter(row.get('gust'), 0))
        except Exception as exp:
            print(exp)
            print('Fail %s' % (row, ))
        out.write(s)
        if i > 0 and i % 1000 == 0:
            out.write(("\.\nCOPY t%s FROM stdin WITH NULL 'None';\n"
                       ) % (sts.strftime("%Y_%m"), ))
        i += 1
    out.write("\.\n")
    out.close()

    proc = subprocess.Popen("psql -h iemdb -f /tmp/snet_dbinsert.sql snet",
                            shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output = proc.stderr.read().decode('utf-8').replace("DELETE 0\n", "")
    if len(output) > 0:
        print('Error encountered with dbinsert...')
        print(output)
    # Clean up after ourself
    os.unlink('/tmp/snet_dbinsert.sql')


if __name__ == '__main__':
    main()
