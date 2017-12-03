"""
  Return the maximum xmin in the database, having too large of a value leads to
  bad things and eventual database not accepting new writes.  I had to lower
  the default postgresql setting from 200 mil to 180 mil as the database does
  lots of writes and autovac sometimes can not keep up.
"""
import sys
from pyiem.util import get_dbconn

IEM = get_dbconn('iem', user='nobody')
icursor = IEM.cursor()


def check():
    icursor.execute("""
    SELECT datname, age(datfrozenxid) FROM pg_database
    ORDER by age DESC LIMIT 1
    """)
    row = icursor.fetchone()

    return row


if __name__ == '__main__':
    dbname, count = check()
    if count < 191000000:
        print 'OK - %s %s |count=%s;191000000;195000000;220000000' % (count,
                                                                      dbname,
                                                                      count)
        sys.exit(0)
    elif count < 195000000:
        print(('WARNING - %s %s |count=%s;191000000;195000000;220000000'
               ) % (count, dbname, count))
        sys.exit(1)
    else:
        print(('CRITICAL - %s %s |count=%s;191000000;195000000;220000000'
               ) % (count, dbname, count))
        sys.exit(2)
