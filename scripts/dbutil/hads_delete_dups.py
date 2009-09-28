import mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
hads = i['hads']
mesosite = i['mesosite']
hads.query("SET TIME ZONE 'GMT'")

def do(ts):
  snet = []
  rs = mesosite.query("SELECT id from stations WHERE network in ('KCCI','KELO','KIMT')").dictresult()
  for i in range(len(rs)):
    snet.append( rs[i]['id'] )
  snetsites = str( tuple(snet) )

  # Delete schoolnet data, since we created it in the first place!
  sql = "DELETE from raw%s WHERE station IN %s" % (ts.strftime("%Y_%m"),\
         snetsites)
  hads.query(sql)

  # Extract unique obs to special table
  sql = "CREATE table tmp as select distinct * from raw%s WHERE valid BETWEEN \
         '%s' and '%s'" % (ts.strftime("%Y_%m"), ts.strftime("%Y-%m-%d"), \
         (ts + mx.DateTime.RelativeDateTime(days=1)).strftime("%Y-%m-%d"))
  hads.query(sql)

  # Delete them all!
  sql = "delete from raw%s WHERE valid BETWEEN \
         '%s' and '%s'" % (ts.strftime("%Y_%m"), ts.strftime("%Y-%m-%d"), \
         (ts + mx.DateTime.RelativeDateTime(days=1)).strftime("%Y-%m-%d"))
  hads.query(sql)

  # Insert from special table
  sql = "INSERT into raw%s SELECT * from tmp" % (ts.strftime("%Y_%m"),)
  hads.query(sql)

  # drop special table!
  hads.query("DROP table tmp")

do( mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1) )

#sts = mx.DateTime.DateTime(2007,12,1)
#ets = mx.DateTime.DateTime(2008,1,1)
#interval = mx.DateTime.RelativeDateTime(days=1)
#now = sts
#while (now < ets):
#  do( now )
#  now += interval
