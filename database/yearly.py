"""Simple helper script to generate schema"""
import datetime

for year in range(2006, 2019):
    print """
create table uscrn_t%(y)s( 
  CONSTRAINT __t%(y)s_check 
  CHECK(valid >= '%(y)s-01-01 00:00+00'::timestamptz 
        and valid < '%(y2)s-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t%(y)s_station_idx on uscrn_t%(y)s(station);
CREATE INDEX uscrn_t%(y)s_valid_idx on uscrn_t%(y)s(valid);
GRANT SELECT on uscrn_t%(y)s to nobody,apache;
GRANT ALL on uscrn_t%(y)s to ldm,mesonet;
    """ % dict(y=year, y2=(year + 1))
