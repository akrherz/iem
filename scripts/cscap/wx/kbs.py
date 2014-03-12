import psycopg2
import datetime

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

iem = {}
cursor.execute("""
 SELECT day, precip from alldata_mi where station = 'MI3504' and year > 1987
""")
for row in cursor:
    iem[ row[0] ] = row[1] * 2.45
    
kbs = {}
# http://lter.kbs.msu.edu/datatables/7
for i, line in enumerate(open('kbs_wx.csv')):
    if i == 0:
        continue
    tokens = line.split(",")
    if len(tokens) < 9:
        continue
    ts = datetime.datetime.strptime(tokens[0], '%Y-%m-%d')
    kbs[ ts.date() ] = float(tokens[1]) / 10.0
    
for year in range(1988,2015):
    total_kbs = 0
    total_iem = 0
    for d in iem:
        if d.year == year:
            total_iem += iem[d]
    for d in kbs:
        if d.year == year:
            total_kbs += kbs[d]
            
    print '%s %6.1f %6.1f %6.1f (%.1f%%)' % (year, total_iem, total_kbs, 
                total_iem - total_kbs, 
                (total_iem - total_kbs) / total_kbs * 100.0)

print

sts = datetime.date(1999,1,1)
ets = datetime.date(2000,1,1)
interval = datetime.timedelta(days=1)
now = sts
while now < ets:
    if abs( iem[now] - kbs[now] ) > 0:
        print '%s %6.1f %6.1f %6.1f (%.1f%%)' % (now, iem[now], kbs[now], 
                iem[now] - kbs[now], 
                (iem[now] - kbs[now]) / (0.01 if kbs[now] == 0 else kbs[now]) * 100.0)
    
    now += interval
