"""Bring the summary table entries to my laptop, please!"""
import psycopg2.extras
import sys
import datetime
IEM = psycopg2.connect(database="iem")
icursor = IEM.cursor()

REMOTE = psycopg2.connect(database='iem',
                          host='129.186.185.33',
                          user='nobody')
cur = REMOTE.cursor(cursor_factory=psycopg2.extras.DictCursor)

date = datetime.date(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))

cur.execute("""SELECT * from summary where day = %s""", (date, ))

table = "summary_%s" % (date.year, )
for row in cur:
    icursor.execute("""INSERT into """ + table + """ (iemid, day, max_tmpf,
    min_tmpf, pday, snow, snowd) values (%(iemid)s, %(day)s, %(max_tmpf)s,
    %(min_tmpf)s, %(pday)s, %(snow)s, %(snowd)s)
    """, row)

icursor.close()
IEM.commit()
IEM.close()
