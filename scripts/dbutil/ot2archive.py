"""
Dump iem database of OT data to archive
"""
import mx.DateTime
import sys
import traceback
import iemdb
import psycopg2.extras
OTHER = iemdb.connect('other')
ocursor = OTHER.cursor(cursor_factory=psycopg2.extras.DictCursor)
IEM = iemdb.connect('iem')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)

# Delete any obs from yesterday
sql = "DELETE from t%s WHERE date(valid) = '%s'" % (ts.year, 
      ts.strftime("%Y-%m-%d") )
ocursor.execute(sql)

# Get obs from Access
sql = """SELECT c.*, t.id from current_log c JOIN stations t on 
    (t.iemid = c.iemid) WHERE date(valid) = '%s' 
    and t.network = 'OT'""" % (ts.strftime("%Y-%m-%d"), )
icursor.execute( sql )

for row in icursor:
    pday = 0
    if (row['pday'] is not None and float(row['pday']) > 0):
        pday = row['pday'] 
    alti = row['alti']
    if alti is None and row['mslp'] is not None:
        alti = row['mslp'] * .03 
    sql = """INSERT into t%s (station, valid, tmpf, dwpf, drct, sknt,  alti, 
         pday, gust, c1tmpf,srad) values('%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s)
         """ % (ts.year,row['id'], row['valid'], (row['tmpf'] or "Null"), 
  (row['dwpf'] or "Null"), (row['drct'] or "Null"), (row['sknt'] or "Null"),
  (alti or "Null"), pday, (row['gust'] or "Null") , 
   (row['c1tmpf'] or "Null"), (row['srad'] or "Null"))
    icursor.execute(sql)

icursor.close()
IEM.commit()