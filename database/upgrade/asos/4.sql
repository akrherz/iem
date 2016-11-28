---
create table t2017( 
  CONSTRAINT __t2017_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_station_idx on t2017(station);
CREATE INDEX t2017_valid_idx on t2017(valid);
GRANT SELECT on t2017 to nobody,apache;


---
create table t2017_1minute( 
  CONSTRAINT __t2017_1minute_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00')) 
  INHERITS (alldata_1minute);
CREATE INDEX t2017_1minte_station_idx on t2017_1minute(station);
CREATE INDEX t2017_1minute_valid_idx on t2017_1minute(valid);
GRANT SELECT on t2017_1minute to nobody,apache;
