import psycopg2
import pandas as pd
from pyiem.network import Table as NetworkTable
nt = NetworkTable("IA_COOP")

pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = pgconn.cursor()
pgconn2 = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor2 = pgconn2.cursor()

cursor.execute("""
    SELECT id, day, pday from summary_2015 s JOIN stations t on (t.iemid = s.iemid)
    WHERE s.day = '2015-06-25' and t.network = 'IA_COOP'
    ORDER by pday DESC LIMIT 10
    """)

for row in cursor:
    cursor2.execute("""SELECT day, precip from alldata_ia where
    station = %s and precip > 3 and day < '2015-06-25'
    """, (nt.sts[row[0]]['climate_site'],))
    rows = []
    for row2 in cursor2:
        rows.append(dict(pday=row2[0], precip=row2[1]))
    df = pd.DataFrame(rows)

    psort = df.sort('precip', ascending=False)
    pday = df.sort('pday', ascending=False)
    print(("%s %-20s %5.2f %5.2f %12s %5.2f %12s"
           ) % (row[0], nt.sts[row[0]]['name'],
                row[2], psort['precip'].iloc[0],
                psort['pday'].iloc[0].strftime("%b %-d, %Y"),
                pday['precip'].iloc[0],
                pday['pday'].iloc[0].strftime("%b %-d, %Y")))
