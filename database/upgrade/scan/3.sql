
create table t2018_hourly( 
  CONSTRAINT __t2018_hourly_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz 
        and valid < '2019-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_hourly_idx on t2018_hourly(station, valid);
GRANT SELECT on t2018_hourly to nobody,apache;
