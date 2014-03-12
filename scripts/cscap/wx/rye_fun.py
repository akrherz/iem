import psycopg2
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

SUSTAIN = psycopg2.connect(database='sustainablecorn', host='iemdb', user='nobody')
scursor = SUSTAIN.cursor()

import ConfigParser
import sys
sys.path.insert(0, '../')
import util
config = ConfigParser.ConfigParser()
config.read('../mytokens.cfg')

sitemeta = util.get_site_metadata(config)

scursor.execute("""SELECT uniqueid, valid, operation, biomassdate1, biomassdate2
 from operations where operation ~* 'rye' ORDER by valid ASC""")

biodates1 = {}
biodates2 = {}
plantdates = {}
termdates = {}

for row in scursor:
    site = row[0]
    if not biodates1.has_key(site):
        biodates1[site] = {2011: [], 2012: [], 2013: [], 2014: [], 2015: []}
    if not biodates2.has_key(site):
        biodates2[site] = {2011: [], 2012: [], 2013: [], 2014: [], 2015: []}
    if not plantdates.has_key(site):
        plantdates[site] = {2011: [], 2012: [], 2013: [], 2014: [], 2015: []}
    if not termdates.has_key(site):
        termdates[site] = {2011: [], 2012: [], 2013: [], 2014: [], 2015: []}
    valid = row[1]
    operation = row[2]
    bm1 = row[3]
    bm2 = row[4]
    #print "%-15.15s %-20s %10s %10s %10s" % (site, operation, valid, bm1, bm2)
    if operation.find('termination') == 0:
        cropyear = valid.year
        termdates[site][cropyear].append( [valid, bm1, bm2] )
    if operation.find('plant') == 0:
        cropyear = valid.year + 1
        plantdates[site][cropyear].append( valid )
        
for site in plantdates.keys():
    climate_site = sitemeta[site]['climate_site']
    table = "alldata_%s" % (climate_site[:2],)
    for yr in range(2011,2014):
        for plantdate in plantdates[site][yr]:
            for (termdate, bm1, bm2) in termdates[site][yr]:
                ccursor.execute("""
    SELECT sum(precip), sum(gddxx(0,100,f2c(low)::real,f2c(high)::real)),
    sum(gddxx(4,100,f2c(low)::real,f2c(high)::real))
    from """+table+""" WHERE station = %s and
    day between %s and %s
                """, (climate_site, plantdate, termdate))
                row = ccursor.fetchone()
                ccursor.execute("""
    SELECT sum(precip), sum(gddxx(0,100,f2c(low)::real,f2c(high)::real)),
    sum(gddxx(4,100,f2c(low)::real,f2c(high)::real)) 
    from """+table+""" WHERE station = %s and
    day between %s and %s
                """, (climate_site, plantdate, bm1))
                row2 = ccursor.fetchone()
                if bm2:
                    ccursor.execute("""
    SELECT sum(precip), sum(gddxx(0,100,f2c(low)::real,f2c(high)::real)),
    sum(gddxx(4,100,f2c(low)::real,f2c(high)::real)) 
    from """+table+""" WHERE station = %s and
    day between %s and %s
                """, (climate_site, plantdate, bm1))
                    row3 = ccursor.fetchone()
                else:
                    row3 = [0,0,0]
                print("%-12.12s, %s, %s, %5.2f, %4.0f, %4.0f, %5.2f, %4.0f, %4.0f, %5.2f, %4.0f, %4.0f, %s, %s, %s, %s" % (site, sitemeta[site]['climate_site'],
                                                yr, 
                                                row[0], row[1], row[2],
                                                row2[0], row2[1], row2[2],
                                                row3[0], row3[1], row3[2],
                                                plantdate, termdate, bm1,
                                                bm2 or ""))
        
