import psycopg2
import pytz
import datetime
import sys

sts = datetime.datetime(2010, int(sys.argv[1]), 1)
ets = sts + datetime.timedelta(days=35)
ets = ets.replace(day=1)

PGCONN = psycopg2.connect(database='mec', host='127.0.0.1', port='5555')
cursor = PGCONN.cursor()
cursor2 = PGCONN.cursor()

cursor.execute("""SELECT id, unitnumber, ST_x(geom), ST_y(geom)
    from turbines""")

o = open('turbines.csv', 'w')
o.write("TID,LON,LAT\n")

p = open('turbine_data_%s.csv' % (sts.strftime("%Y%m"),), 'w')
p.write("TID,VALID_UTC,VALID_LOCAL,POWER,YAW,YAW2,WINDSPEED,PITCH\n")

for row in cursor:
    o.write("%s,%.6f,%.6f\n" % (row[0], row[2], row[3]))

    cursor2.execute("""SELECT valid at time zone 'UTC', power, yaw, yaw2,
    windspeed, pitch from sampled_data_%s WHERE
    valid between '%s' and '%s'
    ORDER by valid ASC """ % (row[1], sts.strftime("%Y-%m-%d"),
                              ets.strftime("%Y-%m-%d")))

    for row2 in cursor2:
        ts = row2[0]
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))
        p.write(("%s,%s,%s,%s,%s,%s,%s,%s\n"
                 ) % (row[0], ts.strftime("%Y-%m-%d %H:%M:%S"),
                      (ts.astimezone(pytz.timezone("America/Chicago"))
                       ).strftime("%Y-%m-%d %H:%M:%S"),
                      row2[1], row2[2], row2[3], row2[4], row2[5]))
    print row[0], cursor2.rowcount

p.close()
o.close()
