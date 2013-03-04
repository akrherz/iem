import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
acursor2 = ASOS.cursor()
acursor3 = ASOS.cursor()

acursor.execute("""
 SELECT id, x(geom), y(geom) from stations where
 (network ~* 'ASOS' or network = 'IA_AWOS') and country = 'US' 
 and archive_begin < '2007-01-01' 
 and id = 'SUX' LIMIT 1
""")

def get(sts, ets):
    acursor3.execute("""SELECT count(*), max(mslp), min(mslp) from alldata
    where station = 'FSD' and valid BETWEEN %s and %s""",  (sts, ets))
    print acursor3.fetchone()

for row in acursor:
    acursor2.execute("""SELECT valid, mslp from alldata WHERE
        station = %s and valid > '2007-01-01' and mslp > 0 
        and valid < '2013-01-01'
        ORDER by valid ASC""", (row[0],))
    
    valid = []
    pmsl = []
    maxval = 0
    dates = []
    hits = []
    for row2 in acursor2:
        valid.insert(0, row2[0] )
        pmsl.insert(0, row2[1] )

        while (row2[0] - valid[-1]).days >= 1:
            valid.pop()
            pmsl.pop()
            hits.pop()
            
        diff = max(pmsl) - min(pmsl)
        # Difference greater than 24mb and the value is less than a day ago
        if diff >= 24 and pmsl[0] < pmsl[-1]:
            if diff > maxval:
                maxval = diff
            lkp = row2[0].strftime("%Y%m%d")
            if True not in hits:
                print lkp
                print pmsl
                get(valid[-1], valid[0])
                dates.append( lkp )
            hits.insert(0, True)
        else:
            hits.insert(0, False)
            
    if acursor2.rowcount > (6*365*10):
        print '%s,%.2f,%.2f,%s,%s' % (row[0], row[1], row[2], len(dates),
                                      maxval)
            
    
