import psycopg2

PGCONN = psycopg2.connect(database='mec', host='127.0.0.1', port='5555')
cursor = PGCONN.cursor()
cursor2 = PGCONN.cursor()

cursor.execute("""SELECT id, unitnumber, ST_x(geom), ST_y(geom) 
    from turbines""")

o = open('turbines.csv', 'w')
o.write("TID,LON,LAT\n")

p = open('turbine_data.csv', 'w')
p.write("TID,VALID_UTC,POWER,YAW,WINDSPEED\n")

for row in cursor:
    o.write("%s,%.6f,%.6f\n" % (row[0], row[2], row[3]))
    
    cursor2.execute("""SELECT valid at time zone 'UTC', power, yaw, 
    windspeed from turbine_data_%s where power is not null and 
    yaw is not null and windspeed is not null""" % (row[1],))
    
    for row2 in cursor2:
        p.write("%s,%s,%s,%s,%s\n" % (row[0], 
                    row2[0].strftime("%Y-%m-%d %H:%M:%S"), row2[1],
                    row2[2], row2[3]))
    print row[0], cursor2.rowcount
    
p.close()
o.close()