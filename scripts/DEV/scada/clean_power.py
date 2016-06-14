import psycopg2
pgconn = psycopg2.connect(database='scada')
cursor = pgconn.cursor()
cursor2 = pgconn.cursor()

cursor.execute("""DELETE from cleanpower""")
cursor2.execute("""SELECT distinct valid from data ORDER by valid""")


def unshadowed(azimuth):
    distance = 3000
    radius = 5  # half of the fan opening
    a0 = azimuth - radius
    a1 = azimuth + radius
    if a0 < 0:
        a = "(azimuth > %s or azimuth < %s)" % (360 + a0, a1)
    elif a1 >= 360:
        a = "(azimuth > %s or azimuth < %s)" % (a0, a1 - 360)
    else:
        a = "azimuth between %s and %s" % (a0, a1)

    cursor.execute("""
        SELECT id from turbines where id not in (
        SELECT distinct aid from shadow where """ + a + """
        and distance < %s)
    """, (distance,))
    t = []
    for row in cursor:
        t.append(row[0])
    return t

for row in cursor2:
    valid = row[0]
    # find the average yaw
    cursor.execute("""SELECT avg(yawangle), stddev(yawangle)
    from data where valid = %s and yawangle >= 0
    """, (valid,))
    (yaw, std_yaw) = cursor.fetchone()
    if yaw is None:
        print "skipping", valid
        continue
    # find unshadowed turbines at this yaw
    turbines = unshadowed(yaw)
    # get the averages for these turbines
    cursor.execute("""SELECT avg(power), avg(windspeed) from data
    where valid = %s and turbine_id in %s and alpha1 < 1 and windspeed >= 0
    and power >= 0""", (valid, tuple(turbines)))
    row2 = cursor.fetchone()
    if row2[0] is None:
        print "skipping", valid
        continue
    cursor.execute("""INSERT into cleanpower(valid, power, yawangle, windspeed)
    values (%s, %s, %s, %s)""", (valid, row2[0], yaw, row2[1]))
    print "%s %5.2f %6.2f %6.2f" % (valid, row2[0], yaw, row2[1])


cursor.close()
pgconn.commit()
