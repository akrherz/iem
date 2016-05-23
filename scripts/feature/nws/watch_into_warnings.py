"""
-- Since our main db is too slow for this script to run practically
 create table warnings_temp as
 select ugc, phenomena, significance, issue, expire, wfo from warnings
 WHERE issue > '2005-10-01';

 create index warnings_temp_ugc_idx on warnings_temp(ugc);
 cluster warnings_temp using warnings_temp_ugc_idx;
 grant select on warnings_temp to nobody;

"""
import psycopg2
from tqdm import tqdm
from pyiem.plot import MapPlot

POSTGIS = psycopg2.connect(database='postgis', host='localhost',
                           port=5555, user='nobody')
cursor = POSTGIS.cursor()
cursor2 = POSTGIS.cursor()

phenomena = 'SV'

cursor.execute("""
 SELECT ugc, issue, init_expire, wfo from warnings where phenomena = %s and
 significance = 'A' and issue > '2005-10-01' ORDER by issue ASC
""", (phenomena, ))
total = cursor.rowcount
print 'Events is ', total

hits = {}
hits2 = {}
totals = {}
misses = 0
for row in tqdm(cursor, total=total):
    wfo = row[3]
    if wfo not in hits:
        hits[wfo] = {}
    if wfo not in totals:
        totals[wfo] = 0
    totals[wfo] += 1
    cursor2.execute("""
    SELECT distinct phenomena, significance from warnings_temp
    where ugc = %s and expire > %s and issue < %s and wfo = %s
    """, (row[0], row[1], row[2], wfo))
    for row2 in cursor2:
        key = "%s.%s" % (row2[0], row2[1])
        if key not in hits[wfo]:
            hits[wfo][key] = 0
        hits[wfo][key] += 1
        if key not in hits2:
            hits2[key] = 0
        hits2[key] += 1
    if cursor2.rowcount == 0:
        misses += 1

data = {}
for wfo in hits.keys():
    data[wfo] = hits[wfo].get(
                '%s.W' % (phenomena,), 0) / float(totals[wfo]) * 100.0

m = MapPlot(sector='nws', axisbg='white',
            title=("Conversion [%] of Severe T'Storm Watch Counties/Parishes into "
                   "SVR Warnings"), titlefontsize=14,
            subtitle='1 Oct 2005 - 19 May 2016')
m.fill_cwas(data, ilabel=True, lblformat='%.0f')
m.postprocess(filename='test.png')

print 'Misses %s %.1f%%' % (misses, misses / float(total) * 100.0)
for key in hits2.keys():
    print '%s %s %.1f%%' % (key, hits2[key], hits2[key] / float(total) * 100.0)
