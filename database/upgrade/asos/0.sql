---
create table t2015( 
  CONSTRAINT __t2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_station_idx on t2015(station);
CREATE INDEX t2015_valid_idx on t2015(valid);
GRANT SELECT on t2015 to nobody,apache;


---
create table t2015_1minute( 
  CONSTRAINT __t2015_1minute_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (alldata_1minute);
CREATE INDEX t2015_1minte_station_idx on t2015_1minute(station);
CREATE INDEX t2015_1minute_valid_idx on t2015_1minute(valid);
GRANT SELECT on t2015_1minute to nobody,apache;
