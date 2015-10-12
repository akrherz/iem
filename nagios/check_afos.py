"""
 Check how much AFOS data we are ingesting
"""
import sys
import psycopg2
IEM = psycopg2.connect(database='afos', host='iemdb', user='nobody')
icursor = IEM.cursor()


def check():
    icursor.execute("""SELECT count(*) from products
    WHERE entered > now() - '1 hour'::interval""")
    row = icursor.fetchone()

    return row[0]

if __name__ == '__main__':
    count = check()
    if count > 1000:
        print 'OK - %s count |count=%s;100;500;1000' % (count, count)
        sys.exit(0)
    elif count > 500:
        print 'WARNING - %s count |count=%s;100;500;1000' % (count, count)
        sys.exit(1)
    else:
        print 'CRITICAL - %s count |count=%s;100;500;1000' % (count, count)
        sys.exit(2)
