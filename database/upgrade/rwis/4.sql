--
create table t2019(
  CONSTRAINT __t2019_check
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (alldata);
CREATE INDEX t2019_station_idx on t2019(station);
CREATE INDEX t2019_valid_idx on t2019(valid);
GRANT SELECT on t2019 to nobody,apache;

create table t2019_traffic(
  CONSTRAINT __t2019_traffic_check
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (alldata_traffic);
CREATE INDEX t2019_traffic_station_idx on t2019_traffic(station);
CREATE INDEX t2019_traffic_valid_idx on t2019_traffic(valid);
GRANT SELECT on t2019_traffic to nobody,apache;

create table t2019_soil(
  CONSTRAINT __t2019_soil_check
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (alldata_soil);
CREATE INDEX t2019_soil_station_idx on t2019_soil(station);
CREATE INDEX t2019_soil_valid_idx on t2019_soil(valid);
GRANT SELECT on t2019_soil to nobody,apache;
