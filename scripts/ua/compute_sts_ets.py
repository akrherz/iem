import psycopg2
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
mcursor = MESOSITE.cursor()
POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

pcursor.execute("""SELECT station, min(valid), max(valid), count(*) from
    raob_flights GROUP by station ORDER by count DESC""")
for row in pcursor:
    station = row[0]
    sts = row[1]
    ets = row[2]
    online = False
    if ets.year == 2013:
        ets = None
        online = True
    mcursor.execute("""UPDATE stations SET online = %s, archive_begin = %s,
    archive_end = %s WHERE network = 'RAOB' and id = %s""", (online,
                                                sts, ets, station))
    if mcursor.rowcount != 1:
        print station, sts, ets, row[3]
    
mcursor.close()
MESOSITE.commit()
MESOSITE.close()