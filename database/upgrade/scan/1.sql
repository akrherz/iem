create table t2016_hourly( 
  CONSTRAINT __t2016_hourly_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_hourly_idx on t2016_hourly(station, valid);
GRANT SELECT on t2016_hourly to nobody,apache;
