# Update the summary data with hopefully better data from the 
# 1 minute archive...

import sys
import mx.DateTime
from pyIEM import iemdb 
i = iemdb.iemdb()
awos = i['awos']
iem = i['iem']

def compare_with_summary(ts, row):
    station = row['station']
    date    = row['d']
    rainfall= row['rainfall']
    high    = row['high']
    low     = row['low']
    rs = iem.query("""SELECT * from summary_%s WHERE station = '%s' and
         day = '%s'""" % (ts.year, station, date)).dictresult()
    # Check to see if we should add an entry into the database!
    if len(rs) == 0:
        iem.query("""INSERT into summary_%s(station, geom, network, day)
        VALUES ('%s', (select geom from current WHERE station = '%s'), 
        '%s', '%s') """ % ( 
        ts.year, station, station,'AWOS', date ) )
        rs = [{'pday': None, 'max_tmpf': None, 'min_tmpf': None}]

    if (rs[0]['pday'] != rainfall or 
       rs[0]['max_tmpf'] != high or 
       rs[0]['min_tmpf'] != low):
       sql = """UPDATE summary_%s SET max_tmpf = %s, min_tmpf = %s,
              pday = %s WHERE network = 'AWOS' and station = '%s' and
              day = '%s'""" % (ts.year, 
              (rs[0]['max_tmpf'] or 'Null'), 
              (rs[0]['min_tmpf'] or 'Null'), 
              (rs[0]['pday'] or 'Null'), station, date)
       iem.query(sql)

def run_month(ts):
    rs = awos.query("""select station, d,
       sum(rainfall) as rainfall, max(high) as high, min(low) as low 
       from (SELECT station, date(valid) as d, 
       extract(hour from valid) as hr,
       max(p01i) as rainfall, max(tmpf) as high, min(tmpf) as low
       from alldata WHERE valid >= '%s' GROUP by station, d, hr) as foo
       GROUP by station, d""" % (
       ts.strftime("%Y-%m-%d") )).dictresult()
    for i in range(len(rs)):
        compare_with_summary(ts, rs[i] )


ts = mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), 1)
run_month(ts)
