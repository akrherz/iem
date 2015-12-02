create table t2016( 
  CONSTRAINT __t2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_station_idx on t2016(station);
CREATE INDEX t2016_valid_idx on t2016(valid);
GRANT SELECT on t2016 to nobody,apache;

create table t2016_traffic( 
  CONSTRAINT __t2016_traffic_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (alldata_traffic);
CREATE INDEX t2016_traffic_station_idx on t2016_traffic(station);
CREATE INDEX t2016_traffic_valid_idx on t2016_traffic(valid);
GRANT SELECT on t2016_traffic to nobody,apache;

create table t2016_soil( 
  CONSTRAINT __t2016_soil_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (alldata_soil);
CREATE INDEX t2016_soil_station_idx on t2016_soil(station);
CREATE INDEX t2016_soil_valid_idx on t2016_soil(valid);
GRANT SELECT on t2016_soil to nobody,apache;
