from pyiem.network import Table as NetworkTable
import psycopg2
from pyiem.datatypes import pressure, temperature
from pyiem.meteorology import heatindex
pgconn = psycopg2.connect(database='asos', host='localhost', port=5555,
                          user='nobody')
cursor = pgconn.cursor()

nt = NetworkTable(["IA_ASOS", "AWOS"])
ids = nt.sts.keys()
ids.sort()

print """
<table class="table table-condensed table-striped">
<thead>
<tr><th>ID</th><th>Station Name</th><th>3 Sep Peak Heat Index</th>
<th>Last Highest</th><th>Date</th></tr>
</thead>
"""

bah = nt.sts.keys()

for sid in ids:
    cursor.execute("""
    select valid, tmpf, dwpf from alldata where
    station = %s and extract(month from valid) = 9
    and dwpf is not null and tmpf > 84 and valid > '1990-01-01'
    ORDER by valid DESC
    """, (sid,))

    thisdate = [0, None, None, None]
    for i, row in enumerate(cursor):
        hdx = heatindex(temperature(row[1], 'F'),
                        temperature(row[2], 'F')).value('F')
        if row[0].strftime("%Y%m%d") == '20150903':
            if hdx > thisdate[0]:
                thisdate = [hdx, row[0], row[1], row[2]]
            continue
        if thisdate[1] is None:
            break
        if hdx >= thisdate[0]:
            bah.remove(sid)
            print(('%s,%s,%.0f,(%.0f/%.0f),%.0f,(%.0f/%.0f),%s'
                   ) % (sid, nt.sts[sid]['name'],
                        thisdate[0], thisdate[2], thisdate[3],
                        hdx, row[1], row[2],
                        row[0].strftime("%d %b %Y %I:%M %p")))
            break
print 'missed', bah
print "</table>"
