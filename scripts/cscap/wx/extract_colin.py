""" Extract some data for Colin 

1951-2010 Annual GDDs by climate district  Apr 1 - Oct 31
1951-2010 Frost-free days ...

"""
import psycopg2
import pandas as pd
pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = pgconn.cursor()
from pyiem.network import Table as NetworkTable

nt = NetworkTable(['IACLIMATE', 'MNCLIMATE', 'NDCLIMATE', 'OHCLIMATE',
                   'INCLIMATE', 'ILCLIMATE', 'MICLIMATE', 'WICLIMATE',
                   'SDCLIMATE', 'NECLIMATE', 'KSCLIMATE', 'MOCLIMATE'])


res = []
for sid in nt.sts.keys():
    if sid[2] != 'C':
        continue
    TABLE = "alldata_%s" % (sid[:2],)
    cursor.execute("""
    WITH gdd as (
        SELECT year, sum(gdd50(high,low)) from """+TABLE+""" WHERE
        station = %s and sday between '0401' and '1031' and year >= 1951
        and year < 2011 GROUP by year),
    ff as (
        SELECT year, 
        max(case when month < 7 and low < 32 then extract(doy from day) else 0 end),
        min(case when month > 7 and low < 32 then extract(doy from day) else 366 end)
        from """+TABLE+""" WHERE station = %s and year >= 1951 and year < 2011
        GROUP by year)
        
    SELECT g.year, g.sum, f.min - f.max from ff f JOIN gdd g on (g.year = f.year)
    ORDER by g.year ASC
    """, (sid, sid))
    for row in cursor:
        res.append(dict(station=sid, year=row[0], gdd50=row[1], 
                        frostfree=int(row[2])))

df = pd.DataFrame(res)
df.to_csv('output.csv', index=False, columns=['station', 'year', 'gdd50', 
                                              'frostfree'])
