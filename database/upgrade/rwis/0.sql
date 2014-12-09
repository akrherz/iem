create table t2015( 
  CONSTRAINT __t2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_station_idx on t2015(station);
CREATE INDEX t2015_valid_idx on t2015(valid);
GRANT SELECT on t2015 to nobody,apache;

create table t2015_traffic( 
  CONSTRAINT __t2015_traffic_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (alldata_traffic);
CREATE INDEX t2015_traffic_station_idx on t2015_traffic(station);
CREATE INDEX t2015_traffic_valid_idx on t2015_traffic(valid);
GRANT SELECT on t2015_traffic to nobody,apache;

create table t2015_soil( 
  CONSTRAINT __t2015_soil_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (alldata_soil);
CREATE INDEX t2015_soil_station_idx on t2015_soil(station);
CREATE INDEX t2015_soil_valid_idx on t2015_soil(valid);
GRANT SELECT on t2015_soil to nobody,apache;
