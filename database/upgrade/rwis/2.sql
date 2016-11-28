create table t2017( 
  CONSTRAINT __t2017_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00'::timestamptz)) 
  INHERITS (alldata);
CREATE INDEX t2017_station_idx on t2017(station);
CREATE INDEX t2017_valid_idx on t2017(valid);
GRANT SELECT on t2017 to nobody,apache;

create table t2017_traffic( 
  CONSTRAINT __t2017_traffic_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00'::timestamptz)) 
  INHERITS (alldata_traffic);
CREATE INDEX t2017_traffic_station_idx on t2017_traffic(station);
CREATE INDEX t2017_traffic_valid_idx on t2017_traffic(valid);
GRANT SELECT on t2017_traffic to nobody,apache;

create table t2017_soil( 
  CONSTRAINT __t2017_soil_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00'::timestamptz)) 
  INHERITS (alldata_soil);
CREATE INDEX t2017_soil_station_idx on t2017_soil(station);
CREATE INDEX t2017_soil_valid_idx on t2017_soil(valid);
GRANT SELECT on t2017_soil to nobody,apache;
