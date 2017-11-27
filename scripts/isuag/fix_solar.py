"""
 Some of our solar radiation data is not good!
"""
from __future__ import print_function
import datetime
import json

import requests
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def main():
    """ Go main go """
    pgconn = get_dbconn('isuag')
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()

    nt = NetworkTable("ISUSM")
    cursor.execute("""
     SELECT station, valid from sm_daily where (slrmj_tot_qc is null or
     slrmj_tot_qc = 0) and valid > '2015-04-14' ORDER by valid ASC
    """)
    for row in cursor:
        station = row[0]
        v1 = datetime.datetime(row[1].year, row[1].month, row[1].day)
        v2 = v1.replace(hour=23, minute=59)
        cursor2.execute("""
        SELECT sum(slrmj_tot_qc), count(*) from sm_hourly WHERE
        station = %s and valid >= %s and valid < %s
        """, (station, v1, v2))
        row2 = cursor2.fetchone()
        if row2[0] is None or row2[0] < 0.01:
            print('Double Failure %s %s' % (station, v1.strftime("%d %b %Y")))
            # Go fetch me the IEMRE value!
            uri = ("http://iem.local/iemre/daily/%s/%.2f/%.2f/json"
                   ) % (v1.strftime("%Y-%m-%d"), nt.sts[station]['lat'],
                        nt.sts[station]['lon'])
            res = requests.get(uri)
            j = json.loads(res.content)
            row2 = [j['data'][0]['srad_mj'], -1]
        if row2[0] is None or row2[0] < 0.01:
            print('Triple! Failure %s %s' % (station, v1.strftime("%d %b %Y")))
            continue
        print('%s %s -> %.2f (%s obs)' % (station, v1.strftime("%d %b %Y"),
                                          row2[0], row2[1]))
        cursor2.execute("""UPDATE sm_daily SET slrmj_tot_qc = %s
        WHERE station = %s and valid = %s""", (row2[0], station, row[1]))

    cursor2.close()
    pgconn.commit()


if __name__ == '__main__':
    main()
