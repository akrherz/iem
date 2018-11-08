---
create table t2019( 
  CONSTRAINT __t2019_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz 
        and valid < '2020-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_station_idx on t2019(station);
CREATE INDEX t2019_valid_idx on t2019(valid);
GRANT SELECT on t2019 to nobody,apache;
GRANT ALL on t2019 to ldm,mesonet;

---
create table t2019_1minute(
  CONSTRAINT __t2019_1minute_check
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2019_1minte_station_idx on t2019_1minute(station);
CREATE INDEX t2019_1minute_valid_idx on t2019_1minute(valid);
GRANT SELECT on t2019_1minute to nobody,apache;
