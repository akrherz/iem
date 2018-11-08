
create table t2019_hourly( 
  CONSTRAINT __t2019_hourly_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz 
        and valid < '2020-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_hourly_idx on t2019_hourly(station, valid);
GRANT SELECT on t2019_hourly to nobody,apache;
