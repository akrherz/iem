import psycopg2
from tqdm import tqdm

POSTGIS = psycopg2.connect(database='postgis', host='localhost',
                           port=5555, user='nobody')
cursor = POSTGIS.cursor()
cursor2 = POSTGIS.cursor()

cursor.execute("""
 SELECT ugc, issue, expire, wfo from warnings_temp where phenomena = 'SV' and
 significance = 'W' and issue > '2005-10-01' and ugc is not null
""")
total = cursor.rowcount
print 'Events is ', total

hits = {}
misses = 0
for row in tqdm(cursor, total=total):
    cursor2.execute("""
    SELECT distinct phenomena, significance from warnings_temp
    where ugc = %s and expire > %s and issue < %s and significance = 'A'
    """, (row[0], row[1], row[2]))
    for row2 in cursor2:
        key = "%s.%s" % (row2[0], row2[1])
        if key not in hits:
            hits[key] = 0
        hits[key] += 1
    if cursor2.rowcount == 0:
        misses += 1

print 'Misses %s %.1f%%' % (misses, misses / float(total) * 100.0)
for key in hits.keys():
    print '%s %s %.1f%%' % (key, hits[key], hits[key] / float(total) * 100.0)
