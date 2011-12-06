import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

ccursor.execute("""
 SELECT valid, max_high, max_high_yr from climate where station = 'IA2203' 
 and max_high_yr > 1932 ORDER by valid
""")
cnt = [0]*4
tot = [0]*4
for row in ccursor:
    acursor.execute("""
    SELECT date(valid) as d, max(sknt) from t%s WHERE station = 'DSM' and 
    valid BETWEEN '%s-%s 00:00'::timestamp + '1 day'::interval and 
    '%s-%s 23:59'::timestamp + '4 days'::interval GROUP by d ORDER by d ASC
    """ % (row[2], 
           row[2], row[0].strftime("%m-%d"), 
           row[2], row[0].strftime("%m-%d")))
    d = 0
    for row2 in acursor:
        print row[0], row[1], row[2], row2[1], d
        tot[d] += row2[1]
        cnt[d] += 1
        d += 1

for i in range(4):
    print '%.2f' % (tot[i] / cnt[i],)

