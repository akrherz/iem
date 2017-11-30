--
create table t2018(
  CONSTRAINT __t2018_check
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (alldata);
CREATE INDEX t2018_station_idx on t2018(station);
CREATE INDEX t2018_valid_idx on t2018(valid);
GRANT SELECT on t2018 to nobody,apache;

create table t2018_traffic(
  CONSTRAINT __t2018_traffic_check
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (alldata_traffic);
CREATE INDEX t2018_traffic_station_idx on t2018_traffic(station);
CREATE INDEX t2018_traffic_valid_idx on t2018_traffic(valid);
GRANT SELECT on t2018_traffic to nobody,apache;

create table t2018_soil(
  CONSTRAINT __t2018_soil_check
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (alldata_soil);
CREATE INDEX t2018_soil_station_idx on t2018_soil(station);
CREATE INDEX t2018_soil_valid_idx on t2018_soil(valid);
GRANT SELECT on t2018_soil to nobody,apache;
