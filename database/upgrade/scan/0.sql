create table t2015_hourly( 
  CONSTRAINT __t2015_hourly_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_hourly_idx on t2015_hourly(station, valid);
GRANT SELECT on t2015_hourly to nobody,apache;
