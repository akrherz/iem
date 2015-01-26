"""
How many times does the soil thaw?
How many days do we have above freezing?
How much rain do we get?
How many days do we have with snow cover?
How much of our annual precipitation falls?

"""

import psycopg2
import datetime
import numpy as np
pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = pgconn.cursor()

starts = {}
ends = {}

cursor.execute("""SELECT year,
 max(case when low < 29 and month < 7 then extract(doy from day) else 0 end),
 min(case when low < 29 and month > 6 then extract(doy from day) else 366 end)
 from alldata_ia where station = 'IA0200' GROUP by year""")

for row in cursor:
    starts[row[0]] = row[1]
    ends[row[0]] = row[2]

daf = []
p = []
sd = []
for year in range(2010,2015):
    d0 = datetime.date(year,1,1) + datetime.timedelta(days=ends[year])
    d1 = datetime.date(year+1,1,1) + datetime.timedelta(days=starts[year+1])
    # Days above freezing
    cursor.execute("""SELECT count(*) from alldata_ia where high > 32
     and station = 'IA0200' and day between %s and %s""",
     (d0, d1))
    daf.append(cursor.fetchone()[0])

    # Sum precip
    cursor.execute("""SELECT sum(precip) from alldata_ia where 
     station = 'IA0200' and day between %s and %s""",
     (d0, d1))
    p.append(cursor.fetchone()[0])
    
    #Snow cover
    cursor.execute("""SELECT count(*) from alldata_ia where snowd > 0
     and station = 'IA0200' and day between %s and %s""",
     (d0, d1))
    sd.append(cursor.fetchone()[0])

print 'DAF', np.average(daf)
print 'P', np.average(p)
print 'SC', np.average(sd)