from pyiem.datatypes import temperature
import psycopg2
import datetime
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

ccursor.execute("""SELECT day, high from alldata_ia where station = 'IA2203'
  and high >= 100 and day > '1950-01-01' ORDER by day ASC""")

print 'DAY,DSM_HIGH,500T,700T,850T,925T'
for row in ccursor:
    day = row[0]
    data = {'high': row[1]}
    pcursor.execute("""
    SELECT tmpc, pressure from raob_profile_"""+ str(day.year)+""" p  JOIN
    raob_flights f on (f.fid = p.fid) WHERE f.station in ('KOAX','KOMA','KOVN') and 
    valid between '%s 03:00' and '%s 12:00' and pressure in (500,700,850,925)
    """ % (day.strftime("%Y-%m-%d"),day.strftime("%Y-%m-%d")))
    for row2 in pcursor:
        data[row2[1]] = row2[0]
        
    print '%s,%s,%s,%s,%s,%s' % (day, data['high'], data.get(500, 'M'),
                                 data.get(700, 'M'), data.get(850, 'M'),
                                 data.get(925, 'M')
                                 )