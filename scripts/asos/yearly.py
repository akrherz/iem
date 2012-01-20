#!/mesonet/python/bin/python

import pg, mx.DateTime
mydb = pg.connect('asos', 'iemdb')

sts = mx.DateTime.DateTime(1928,1,1)
ets = mx.DateTime.DateTime(2013,1,1)
interval = mx.DateTime.RelativeDateTime(years=1)

now = sts
while (now < ets):
  print now
  #sql = "create table t%s() inherits (alldata)" % (now.strftime("%Y_%m"), )
  #mydb.query(sql)
  #sql = "grant select on t%s to nobody,apache" % (now.strftime("%Y_%m"), )
  #mydb.query(sql)
  #for tbl in ['valid','station']:
  #  sql = "create index t%s_%s_idx on t%s(%s)" % (
  #     now.strftime("%Y_%m"), tbl, now.strftime("%Y_%m"), tbl )
  #  mydb.query(sql)

  sql = "update t%s set p01i = round((p01m / 25.4)::numeric, 2) where p01m > 0" % (now.strftime("%Y"), )
  mydb.query(sql)
  #sql = "alter table t%s alter gust TYPE real" % (now.strftime("%Y_%m"), )
  #mydb.query(sql)
  #sql = "alter table summary_%s alter max_sknt_ts TYPE timestamp with time zone" % (now.strftime("%Y"), )
  #mydb.query(sql)
  #sql = "alter table summary_%s alter max_drct TYPE real" % (now.strftime("%Y"), )
  #mydb.query(sql)
  #sql = "CREATE table t%s() inherits (alldata)" % (now.year,)
  #mydb.query( sql )
  #sql = "grant select on t%s to nobody,apache" % (now.year, )
  #mydb.query( sql )
  #sql = "CREATE index warnings_%s_combo_idx on warnings_%s(wfo, phenomena, eventid, significance)" % (now.year, now.year)
  #mydb.query( sql )
  #sql = "CREATE index warnings_%s_expire_idx on warnings_%s(expire)" % (now.year, now.year)
  #mydb.query( sql )
  #sql = "CREATE index warnings_%s_issue_idx on warnings_%s(issue)" % (now.year, now.year)
  #mydb.query( sql )
  #sql = "CREATE index t%s_idx on t%s(station, valid)" % (now.year, now.year)
  #mydb.query( sql )
  #sql = "CREATE index t%s_valid_idx on t%s(valid)" % (now.year, now.year)
  #mydb.query( sql )
  #sql = "update summary_%s c SET iemid = s.iemid FROM stations s WHERE c.station = s.id and c.network = s.network and c.day = '%s'" % (now.year, now.strftime("%Y-%m-%d") )
  #mydb.query( sql )

  now += interval
