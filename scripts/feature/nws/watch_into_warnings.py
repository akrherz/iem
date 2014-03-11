import psycopg2

POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = POSTGIS.cursor()
cursor2 = POSTGIS.cursor()

cursor.execute("""
 SELECT ugc, issue, init_expire, wfo from warnings where phenomena = 'WS' and
 significance = 'A' and issue > '2005-10-01'
""")
total = cursor.rowcount
print 'Events is ', total

hits = {}
totals = {}
misses = 0
for row in cursor:
    wfo = row[3]
    if not hits.has_key(wfo):
        hits[wfo] = {}
    if not totals.has_key(wfo):
        totals[wfo] = 0
    totals[wfo] += 1
    cursor2.execute("""
    SELECT distinct phenomena, significance from warnings
    where ugc = %s and expire > %s and issue < %s and wfo = %s 
    """, (row[0], row[1], row[2], wfo))
    for row2 in cursor2:
        key = "%s.%s" % (row2[0], row2[1])
        if not hits[wfo].has_key(key):
            hits[wfo][key] = 0
        hits[wfo][key] += 1
    if cursor2.rowcount == 0:
        misses += 1

data = {}
for wfo in hits.keys():
    data[wfo] = hits[wfo].get('WS.W', 0) / float(totals[wfo]) * 100.0
    
from pyiem.plot import MapPlot

m = MapPlot(sector='nws',
            title='Conversion [%] of Winter Storm Watch Zones into Winter Storm Warnings',
            subtitle='1 Oct 2005 - 28 Feb 2014')
m.fill_cwas(data)
m.postprocess(filename='test.png')

#print 'Misses %s %.1f%%' % (misses, misses / float(total) * 100.0)
#for key in hits.keys():
#    print '%s %s %.1f%%' % (key, hits[key], hits[key] / float(total) * 100.0)         
