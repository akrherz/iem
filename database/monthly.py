"""Simple helper script to generate schema"""
import datetime

prefix = "nldn"
year = 2016
for month in range(1, 13):
    sts = datetime.date(year, month, 1)
    ets = sts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)
    p1 = sts.strftime("%Y_%m")

    print """CREATE TABLE %(p)s%(p1)s(
  CONSTRAINT __%(p)s%(p1)s_check
  CHECK(valid >= '%(d1)s 00:00+00'::timestamptz
        and valid < '%(d2)s 00:00+00'::timestamptz))
  INHERITS (%(p)s_all);
CREATE INDEX %(p)s%(p1)s_valid_idx on %(p)s%(p1)s(valid);
GRANT ALL on %(p)s%(p1)s to ldm,mesonet;
GRANT SELECT on %(p)s%(p1)s to nobody,apache;
    """ % dict(p=prefix, p1=p1, d1=sts.strftime("%Y-%m-%d"),
               d2=ets.strftime("%Y-%m-%d"))
