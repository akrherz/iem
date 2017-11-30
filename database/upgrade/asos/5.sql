---
create table t2018( 
  CONSTRAINT __t2018_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz 
        and valid < '2019-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_station_idx on t2018(station);
CREATE INDEX t2018_valid_idx on t2018(valid);
GRANT SELECT on t2018 to nobody,apache;
GRANT ALL on t2018 to ldm,mesonet;

---
create table t2018_1minute(
  CONSTRAINT __t2018_1minute_check
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2018_1minte_station_idx on t2018_1minute(station);
CREATE INDEX t2018_1minute_valid_idx on t2018_1minute(valid);
GRANT SELECT on t2018_1minute to nobody,apache;
