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
    select extract(year from valid) as yr, max(dwpf) from alldata where
    station = %s and extract(month from valid) < 4 
    and dwpf is not null GROUP by yr 
    ORDER by max ASC
    """, (sid,))
    
    maxval = None
    thisyear = None
    years = []
    for i, row in enumerate(cursor):
        val = round(row[1])
        if i == 0:
            maxval = val
        if row[0] == 2015:
            thisyear = val
        if val == maxval:
            years.append("%.0f" % (row[0],))
        
    print '%s,%s,%s,%.0f,%.0f,%s' % (sid, nt.sts[sid]['name'], 
          nt.sts[sid]['archive_begin'].year, thisyear,
                                  maxval, "-".join(years))   
print "</table>"
