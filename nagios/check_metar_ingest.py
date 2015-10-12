"""
 Check how much METAR data we have
"""
import sys
import psycopg2
IEM = psycopg2.connect(database='iem', host=sys.argv[1], user='nobody')
icursor = IEM.cursor()


def check():
    icursor.execute("""SELECT count(*) from current c JOIN stations s on
    (s.iemid = c.iemid)
    WHERE valid > now() - '75 minutes'::interval and network ~* 'ASOS'""")
    row = icursor.fetchone()

    return row[0]

if __name__ == '__main__':
    count = check()
    if count > 3000:
        print 'OK - %s count |count=%s;1000;5000;10000' % (count, count)
        sys.exit(0)
    elif count > 2000:
        print 'WARNING - %s count |count=%s;1000;5000;10000' % (count, count)
        sys.exit(1)
    else:
        print 'CRITICAL - %s count |count=%s;1000;5000;10000' % (count, count)
        sys.exit(2)
