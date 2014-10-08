import psycopg2
import pytz
import datetime

PGCONN = psycopg2.connect(database='mec', host='127.0.0.1', port='5555')
cursor = PGCONN.cursor()
cursor2 = PGCONN.cursor()

xref = {'131':'227',
'119': '233',
'113': '243',
'114': '244',
'115': '245',
}

cursor.execute("""SELECT id, unitnumber, ST_x(geom), ST_y(geom) 
    from turbines WHERE unitnumber in ('131', '119', '113', '114', '115')""")

o = open('turbines.csv', 'w')
o.write("TID,LON,LAT\n")

p = open('turbine_data.csv', 'w')
p.write("TID,VALID_LST,VALID_LOCAL,POWER,YAW,WINDSPEED,PITCH\n")

for row in cursor:
    o.write("%s,%.6f,%.6f\n" % (row[0], row[2], row[3]))
    
    cursor2.execute("""SELECT valid, power, yaw, 
    windspeed, pitch from sampled_data_%s WHERE
    valid between '2008-08-26 10:00' and '2008-08-26 19:00'
    and extract(minute from valid)::numeric %% 10 = 0
    ORDER by valid ASC """ % (row[1],))
    
    for row2 in cursor2:
        ts = row2[0] - datetime.timedelta(hours=1)
        p.write("%s,%s,%s,%s,%s,%s,%s\n" % (xref[row[1]], 
                    ts.strftime("%Y-%m-%d %H:%M:%S"), 
                    row2[0].strftime("%Y-%m-%d %H:%M:%S"),                     
                    row2[1], row2[2], row2[3], row2[4]))
    print row[0], cursor2.rowcount
    
p.close()
o.close()