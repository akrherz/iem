create table t2014_hourly( 
  CONSTRAINT __t2014_hourly_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_hourly_idx on t2014_hourly(station, valid);
GRANT SELECT on t2014_hourly to nobody,apache;