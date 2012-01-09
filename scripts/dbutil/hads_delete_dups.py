"""
Our HADS database gets loaded up with duplicates, this cleans it up.
$Id: $:
"""
import mx.DateTime
import iemdb
HADS = iemdb.connect('hads')
hcursor = HADS.cursor()
hcursor.execute("SET TIME ZONE 'GMT'")

def do(ts):
  # Delete schoolnet data, since we created it in the first place!
  sql = """DELETE from raw%s WHERE station IN 
            (SELECT id from stations WHERE network in ('KCCI','KELO','KIMT')
            )""" % (ts.strftime("%Y_%m"),)
  hcursor.execute(sql)

  # Extract unique obs to special table
  sql = "CREATE table tmp as select distinct * from raw%s WHERE valid BETWEEN \
         '%s' and '%s'" % (ts.strftime("%Y_%m"), ts.strftime("%Y-%m-%d"), \
         (ts + mx.DateTime.RelativeDateTime(days=1)).strftime("%Y-%m-%d"))
  hcursor.execute(sql)

  # Delete them all!
  sql = "delete from raw%s WHERE valid BETWEEN \
         '%s' and '%s'" % (ts.strftime("%Y_%m"), ts.strftime("%Y-%m-%d"), \
         (ts + mx.DateTime.RelativeDateTime(days=1)).strftime("%Y-%m-%d"))
  hcursor.execute(sql)

  # Insert from special table
  sql = "INSERT into raw%s SELECT * from tmp" % (ts.strftime("%Y_%m"),)
  hcursor.execute(sql)

  # drop special table!
  hcursor.execute("DROP table tmp")

do( mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1) )
hcursor.close()
HADS.commit()
HADS.close()

#sts = mx.DateTime.DateTime(2007,12,1)
#ets = mx.DateTime.DateTime(2008,1,1)
#interval = mx.DateTime.RelativeDateTime(days=1)
#now = sts
#while (now < ets):
#  do( now )
#  now += interval
