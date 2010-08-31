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

CREATE TABLE stations(
 id varchar(20),
 synop int,
 name varchar(40),
 state char(2),
 country char(2),
 elevation real,
 network varchar(20),
 online boolean,
 params varchar(300),
 county varchar(50),
 plot_name varchar(40),
 climate_site varchar(6),
 remote_id int,
 wfo char(3),
 archive_begin timestamp with time zone,
 archive_end timestamp with time zone
);

SELECT addgeometrycolumn('stations', 'geom', 4326, 'POINT', 2);

GRANT SELECT on stations to nobody,apache;
