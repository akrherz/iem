"""Simple helper script to generate schema"""
import datetime

for year in range(1928, 2018):
    print """
create table t%(y)s( 
  CONSTRAINT __t%(y)s_check 
  CHECK(valid >= '%(y)s-01-01 00:00+00'::timestamptz 
        and valid < '%(y2)s-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t%(y)s_station_idx on t%(y)s(station);
CREATE INDEX t%(y)s_valid_idx on t%(y)s(valid);
GRANT SELECT on t%(y)s to nobody,apache;
GRANT ALL on t%(y)s to ldm,mesonet;
    """ % dict(y=year, y2=(year + 1))
