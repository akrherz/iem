#!/mesonet/python/bin/python

import pg, mx.DateTime
mydb = pg.connect('asos', 'iemdb')

sts = mx.DateTime.DateTime(1928,1,1)
ets = mx.DateTime.DateTime(1941,1,1)
interval = mx.DateTime.RelativeDateTime(years=1)

now = sts
while (now < ets):
  print now
  #for t in ('station', 'valid'):
  #  sql = "create index t%s_%s_idx on t%s(%s)" % (now.strftime("%Y_%m"), t, now.strftime("%Y_%m"), t )
  #sql = "grant select on raw%s to nobody,apache" % (now.strftime("%Y_%m"), )
  #sql = "alter table t%s alter gust TYPE real" % (now.strftime("%Y_%m"), )
  #mydb.query(sql)
  #sql = "alter table summary_%s alter max_sknt_ts TYPE timestamp with time zone" % (now.strftime("%Y"), )
  #mydb.query(sql)
  #sql = "alter table summary_%s alter max_drct TYPE real" % (now.strftime("%Y"), )
  #mydb.query(sql)
  sql = "CREATE table t%s() inherits (alldata)" % (now.year,)
  mydb.query( sql )
  sql = "grant select on t%s to nobody,apache" % (now.year, )
  mydb.query( sql )
  #sql = "CREATE index warnings_%s_combo_idx on warnings_%s(wfo, phenomena, eventid, significance)" % (now.year, now.year)
  #mydb.query( sql )
  #sql = "CREATE index warnings_%s_expire_idx on warnings_%s(expire)" % (now.year, now.year)
  #mydb.query( sql )
  #sql = "CREATE index warnings_%s_issue_idx on warnings_%s(issue)" % (now.year, now.year)
  #mydb.query( sql )
  sql = "CREATE index t%s_idx on t%s(station, valid)" % (now.year, now.year)
  mydb.query( sql )
  sql = "CREATE index t%s_valid_idx on t%s(valid)" % (now.year, now.year)
  mydb.query( sql )


  now += interval
