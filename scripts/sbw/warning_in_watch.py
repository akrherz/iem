import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()
pcursor2 = POSTGIS.cursor()

no_watch = {'SV': 0, 'TO': 0}
in_watch = {'SV': {'SV': 0, 'TO': 0}, 'TO': {'SV': 0, 'TO': 0}}
totals = {'SV': 0, 'TO': 0}

FORMAT = "%s %6s %6s | %6s %6s | %6s %6s | %6s %6s"
print FORMAT % ('Year', 'TOR', 'SVR', 'TinTA', 'SinTA', 'TinSA', 'TinTA', 
                'TinNo', 'SinNo') 

for yr in range(2006,2013):
    print 'Processing year ', yr
    pcursor.execute("""
    SELECT ugc, issue, expire, phenomena from warnings_%s WHERE phenomena in ('TO','SV')
    and significance = 'W' and gtype = 'C'
    """ % (yr,) )
    for row in pcursor:
        totals[ row[3] ] += 1
        pcursor2.execute("""
        SELECT phenomena from warnings_%s WHERE phenomena in ('TO','SV') and
        significance = 'A' and gtype = 'C' and ugc = '%s' and issue <= '%s'
        and expire > '%s'
        """ % (yr, row[0], row[1], row[1]))
        for row2 in pcursor2:
            in_watch[ row[3] ][ row2[0] ] += 1
        if pcursor2.rowcount == 0:
            no_watch[row[3]] += 1
            
print no_watch
print in_watch
print totals