""" See akrherz/iem#85 """
import psycopg2
import datetime
pgconn = psycopg2.connect(database='asos', host='localhost', port=5555,
                          user='mesonet')
cursor = pgconn.cursor()
cursor2 = pgconn.cursor()

cursor.execute("""
  SELECT valid, metar, station from t2016 where report_type = 1 and p01i < 0.02
  and p01i > 0.005
""")
fixed = 0
processed = 0
for row in cursor:
    nextts = (row[0] + datetime.timedelta(minutes=60)).replace(minute=0)
    cursor2.execute("""
    SELECT valid, p01i from t2016 where station = %s and
    valid > %s and valid < %s and report_type = 2 and p01i >= 0.01
    """, (row[2], row[0], nextts))
    processed += 1
    if cursor2.rowcount == 0:
        newmetar = row[1].replace("P0001", "P0000")
        cursor2.execute("""UPDATE t2016 SET metar = %s, p01i = 0.0001
        WHERE station = %s and valid = %s and report_type = 1
        """, (newmetar, row[2], row[0]))
        if cursor2.rowcount != 1:
            print("BIG ERROR? %s" % (str(row),))
        else:
            fixed += 1
        if fixed % 100 == 0:
            print("Flush %s/%s/%s" % (fixed, processed, cursor.rowcount))
            cursor2.close()
            pgconn.commit()
            cursor2 = pgconn.cursor()

print("Fixed %s/%s entries" % (fixed, cursor.rowcount))
cursor2.close()
pgconn.commit()
