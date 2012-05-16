"""
 Dump!
"""
import constants
import network
nt = network.Table("IACLIMATE")
import iemdb
import psycopg2.extras
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

for id in nt.sts.keys():
    fn = "coop_data/%s.csv" % (nt.sts[id]['name'].replace(" ", "_"), )
    out = open(fn, 'w')
    out.write("station,station_name,lat,lon,day,high,low,precip,snow,\n")
    sql = "SELECT * from %s WHERE station = '%s' ORDER by day ASC" % (
         constants.get_table(id), id)

    ccursor.execute( sql )
    for row in ccursor:
        out.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,\n" % (id.lower(), 
                nt.sts[id]['name'], nt.sts[id]['lat'], nt.sts[id]['lon'],
                row['day'], row['high'], row['low'], row['precip'], 
                row['snow']) )

    out.close()
