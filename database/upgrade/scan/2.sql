create table t2017_hourly( 
  CONSTRAINT __t2017_hourly_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_hourly_idx on t2017_hourly(station, valid);
GRANT SELECT on t2017_hourly to nobody,apache;
