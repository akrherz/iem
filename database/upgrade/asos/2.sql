---
create table t2016( 
  CONSTRAINT __t2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_station_idx on t2016(station);
CREATE INDEX t2016_valid_idx on t2016(valid);
GRANT SELECT on t2016 to nobody,apache;


---
create table t2016_1minute( 
  CONSTRAINT __t2016_1minute_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (alldata_1minute);
CREATE INDEX t2016_1minte_station_idx on t2016_1minute(station);
CREATE INDEX t2016_1minute_valid_idx on t2016_1minute(valid);
GRANT SELECT on t2016_1minute to nobody,apache;
