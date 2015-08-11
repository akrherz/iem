import urllib2
import psycopg2
import datetime
mesosite = psycopg2.connect(database='coop', host='iemdb')
mcursor = mesosite.cursor()

# Get max date
current = {}
mcursor.execute("SELECT monthdate, anom_34, soi_3m from elnino")
for row in mcursor:
    current[row[0]] = dict(anom_34=row[1], soi_3m=row[2])

url = "http://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices"
req = urllib2.Request(url)
data = urllib2.urlopen(req).readlines()

for line in data[1:]:
    tokens = line.split()
    anom34 = float(tokens[-1])
    date = datetime.date(int(tokens[0]), int(tokens[1]), 1)
    val = current.get(date, {}).get('anom_34', None)
    if val is None or anom34 != val:
        print 'Found ElNino3.4! %s %s' % (date, anom34)
        if current.get(date) is None:
            mcursor.execute("""INSERT into elnino(monthdate) values (%s)
            """, (date, ))
            current[date] = dict(anom_34=anom34)
        mcursor.execute("""
            UPDATE elnino SET anom_34 = %s
            WHERE monthdate = %s
        """, (anom34, date))

url = "http://www.cpc.ncep.noaa.gov/data/indices/soi.3m.txt"
req = urllib2.Request(url)
data = urllib2.urlopen(req).readlines()

for line in data[1:]:
    year = int(line[:4])
    pos = 4
    for month in range(1, 13):
        soi = float(line[pos:pos+6])
        pos += 6
        date = datetime.date(year, month, 1)
        if soi < -999:
            continue
        val = current.get(date, {}).get('soi_3m', None)
        if val is None or soi != val:
            print 'Found SOI 3M! %s %s' % (date, soi)
            if current.get(date) is None:
                mcursor.execute("""INSERT into elnino(monthdate) values (%s)
                """, (date, ))
            mcursor.execute("""
                UPDATE elnino SET soi_3m = %s
                WHERE monthdate = %s
            """, (soi, date))

mesosite.commit()
mesosite.close()
