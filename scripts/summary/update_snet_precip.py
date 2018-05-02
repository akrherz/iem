"""
Populate the hourly precip table with snet data
"""
import datetime

from pyiem.util import get_dbconn


def compute(ts):
    """Do what we need to do"""
    pgconn = get_dbconn('iem')
    icursor = pgconn.cursor()
    icursor2 = pgconn.cursor()
    tsm2 = ts - datetime.timedelta(hours=2)
    tsm1 = ts - datetime.timedelta(hours=1)
    sql = """select f2.id, f2.network, n, x from
   (SELECT id, network, min(pday) as n from
   current_log c, stations t
   WHERE t.network IN ('KELO','KIMT','KCCI') and valid IN ('%s',
   '%s','%s','%s') and pday >= 0
   and t.iemid = c.iemid GROUP by id, network) as f1,
   (SELECT id, network, max(pday) as x from
   current_log c, stations t
   WHERE t.network IN ('KELO','KIMT','KCCI') and valid IN ('%s',
   '%s','%s','%s') and pday >= 0
   and t.iemid = c.iemid GROUP by id, network) as f2
   WHERE f1.id = f2.id and f1.network = f2.network
    """ % (
       tsm2.replace(minute=56),
       tsm2.replace(minute=57),
       tsm2.replace(minute=58),
       tsm2.replace(minute=59),
       tsm1.replace(minute=56),
       tsm1.replace(minute=57),
       tsm1.replace(minute=58),
       tsm1.replace(minute=59))
    icursor.execute(sql)
    for row in icursor:
        x = row[3]
        n = row[2]
        station = row[0]

        phour = x - n
        if phour < 0:
            phour = x
        sql = """
        INSERT into hourly_%s values ('%s','%s','%s','%s')
        """ % (ts.year, station, row[1], ts.strftime("%Y-%m-%d %H:%M"), phour)
        icursor2.execute(sql)
    icursor.close()
    icursor2.close()
    pgconn.commit()


def main():
    """Go Main Go"""
    compute(datetime.datetime.now().replace(minute=0, second=0))


if __name__ == '__main__':
    main()
