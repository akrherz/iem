from pyiem.datatypes import temperature
import psycopg2
import datetime
ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

acursor.execute("""select valid, tmpf from alldata where station = 'DSM' 
  and tmpf >= 97.9 and
  extract(hour from valid + '10 minutes'::interval) = 13 ORDER by valid ASC""")

for row in acursor:
    ccursor.execute("""SELECT high from alldata_ia where station = 'IA2203'
    and day = date(%s)""", (row[0],))
    row2 = ccursor.fetchone()
    print row[0], row[1], row2[0]