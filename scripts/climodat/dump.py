"""Dump!"""
import constants
from pyiem.network import Table as NetworkTable
import psycopg2.extras

nt = NetworkTable("IACLIMATE")
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

BASEDIR = "/mesonet/share/pickup/coop_data"

for sid in nt.sts.keys():
    fn = "%s/%s.csv" % (BASEDIR, nt.sts[sid]['name'].replace(" ", "_"))
    out = open(fn, 'w')
    out.write("station,station_name,lat,lon,day,high,low,precip,snow,\n")
    sql = """
        SELECT * from %s WHERE station = '%s' ORDER by day ASC
    """ % (constants.get_table(sid), sid)
    ccursor.execute(sql)

    for row in ccursor:
        out.write(("%s,%s,%s,%s,%s,%s,%s,%s,%s,\n"
                   "") % (sid.lower(), nt.sts[sid]['name'], nt.sts[sid]['lat'],
                          nt.sts[sid]['lon'], row['day'], row['high'],
                          row['low'], row['precip'], row['snow']))

    out.close()
