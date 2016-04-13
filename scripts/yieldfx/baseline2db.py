"""Copy the provided baseline data to the database"""
import psycopg2
import glob
import os
import datetime

pgconn = psycopg2.connect(database='coop', host='iemdb')
cursor = pgconn.cursor()

os.chdir('baseline')
for fn in glob.glob("*.txt"):
    location = fn[:-4]
    cursor.execute("""
        DELETE from yieldfx_baseline where station = %s
    """, (location, ))
    print("Removed %s rows for station: %s" % (cursor.rowcount, location))
    for line in open(fn):
        line = line.strip()
        if not line.startswith('19') and not line.startswith('20'):
            continue
        tokens = line.split()
        valid = (datetime.date(int(tokens[0]), 1, 1) +
                 datetime.timedelta(days=int(tokens[1])-1))
        cursor.execute("""INSERT into yieldfx_baseline (station, valid,
        radn, maxt, mint, rain) VALUES (%s, %s, %s, %s, %s, %s)
        """, (location, valid, float(tokens[2]), float(tokens[3]),
              float(tokens[4]), float(tokens[5])))

cursor.close()
pgconn.commit()
pgconn.close()
