import sys
import pg
import mx.DateTime
import iemdb
import psycopg2.extras
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
ccursor2 = COOP.cursor()

sts = mx.DateTime.DateTime( int(sys.argv[1]), int(sys.argv[2]), 1)
ets = sts + mx.DateTime.RelativeDateTime(months=1)

cnt = {'climate': {'max_high': 0, 'min_high': 0, 'max_low': 0, 
                   'min_low': 0, 'max_precip': 0},
       'climate51': {'max_high': 0, 'min_high': 0, 'max_low': 0, 
                     'min_low': 0, 'max_precip': 0}
      }

def update(tbl, col, val, yr, station, valid):
    sql = """UPDATE %s SET %s = %s, %s_yr = %s WHERE station = '%s' and 
       valid = '%s'""" % (tbl, col, val, col, yr, station, valid)
    ccursor2.execute(sql)
    cnt[tbl][col] += 1

for tbl in ['climate51','climate']:
    # Load up records
    sql = "SELECT * from %s" % (tbl,)
    ccursor.execute( sql )
    records = {}
    for row in ccursor:
        station = row['station']
        if (not records.has_key(station)):
            records[station] = {}
        records[station][row['valid'].strftime("%Y-%m-%d")] = row

    # Now, load up obs!
    sql = """SELECT * from alldata_ia WHERE day >= '%s' 
        and day < '%s' and high is not null and low is not null""" % (
        sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d") )
    ccursor.execute(sql)
    for row in ccursor:
        dkey = "2000-%s" % (row['day'].strftime("%m-%d"), )
        stid = row['station']
        if not records.has_key(stid):
            continue
        r = records[stid][dkey]
        if row['high'] > r['max_high']:
            update(tbl, 'max_high', row['high'], row['day'].year, stid, dkey)

        if row['high'] < r['min_high']:
            update(tbl, 'min_high', row['high'], row['day'].year, stid, dkey)

        if row['low'] > r['max_low']:
            update(tbl, 'max_low', row['low'], row['day'].year, stid, dkey)

        if row['low'] < r['min_low']:
            update(tbl, 'min_low', row['low'], row['day'].year, stid, dkey)

        if  row['precip'] > r['max_precip']:
            update(tbl, 'max_precip', row['precip'], row['day'].year, stid, dkey)

print cnt
