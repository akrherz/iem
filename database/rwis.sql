CREATE TABLE alldata_traffic(
  station char(5),
  valid timestamp with time zone,
  lane_id smallint,
  avg_speed real,
  avg_headway real,
  normal_vol real,
  long_vol real,
  occupancy real
);
GRANT select on alldata_traffic to nobody,apache;
CREATE TABLE t2010_traffic() inherits (alldata_traffic);
GRANT select on t2010_traffic to nobody,apache;

CREATE TABLE alldata_soil(
  station char(5),
  valid timestamp with time zone,
  s0temp real,
  s1temp real,
  s2temp real,
  s3temp real,
  s4temp real,
  s5temp real,
  s6temp real,
  s7temp real,
  s8temp real,
  s9temp real,
  s10temp real,
  s11temp real,
  s12temp real,
  s13temp real,
  s14temp real
);

GRANT select on alldata_soil to nobody,apache;
CREATE TABLE t2010_soil() inherits (alldata_soil);
GRANT select on t2010_soil to nobody,apache;

create table t2014( 
  CONSTRAINT __t2014_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_station_idx on t2014(station);
CREATE INDEX t2014_valid_idx on t2014(valid);
GRANT SELECT on t2014 to nobody,apache;

create table t2014_traffic( 
  CONSTRAINT __t2014_traffic_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata_traffic);
CREATE INDEX t2014_traffic_station_idx on t2014_traffic(station);
CREATE INDEX t2014_traffic_valid_idx on t2014_traffic(valid);
GRANT SELECT on t2014_traffic to nobody,apache;

create table t2014_soil( 
  CONSTRAINT __t2014_soil_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata_soil);
CREATE INDEX t2014_soil_station_idx on t2014_soil(station);
CREATE INDEX t2014_soil_valid_idx on t2014_soil(valid);
GRANT SELECT on t2014_soil to nobody,apache;
