from pyiem.network import Table as NetworkTable
import psycopg2
from pyiem.datatypes import pressure
pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = pgconn.cursor()

nt = NetworkTable("IA_ASOS")
ids = nt.sts.keys()
ids.sort()

print """
<table class="table table-condensed table-striped">
<thead>
<tr><th>ID</th><th>Station Name</th><th>Data Since</th>
<th>Altimeter [inch]</th><th>Sea Level Pressure [mb]</th></tr>
</thead>
"""


for sid in ids:
    if nt.sts[sid]['archive_begin'].year > 1972:
        continue
    cursor.execute("""
    select valid, alti, mslp from alldata where station = %s and alti > 30.6 
    and alti < 32 ORDER by alti DESC, valid ASC
    """, (sid,))
    
    maxval = None
    for i, row in enumerate(cursor):
        if i == 0:
            maxval = row[1]
        if row[1] != maxval:
            break
        
        slp = row[2] if row[2] is not None else pressure(row[1], 'IN').value('MB')
        
        print """<tr><td>%s</td><td>%s</td><td>%s</td>
        <td>%s</td><td>%.2f</td><td>%.1f</td></tr>""" % (sid, nt.sts[sid]['name'],
            nt.sts[sid]['archive_begin'].year,
                                        row[0].strftime("%d %b %Y %H:%M %p"), row[1], slp)
    print
print "</table>"