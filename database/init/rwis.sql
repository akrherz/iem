-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (4, now());

CREATE TABLE sensors(
  station varchar(5),
  sensor0 varchar(100),
  sensor1 varchar(100),
  sensor2 varchar(100),
  sensor3 varchar(100)
);
GRANT SELECT on sensors to nobody,apache;
  

CREATE TABLE alldata(
  station varchar(6),
  valid timestamptz,
  tmpf real,
  dwpf real,
  drct smallint,
  sknt real,
  tfs0 real,
  tfs1 real,
  tfs2 real,
  tfs3 real,
  subf real,
  gust real,
  tfs0_text varchar(20),
  tfs1_text varchar(20),
  tfs2_text varchar(20),
  tfs3_text varchar(20),
  pcpn real,
  vsby real
);
GRANT SELECT on alldata to nobody,apache;

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

create table t1994( 
  CONSTRAINT __t1994_check 
  CHECK(valid >= '1994-01-01 00:00+00'::timestamptz 
        and valid < '1995-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1994_station_idx on t1994(station);
CREATE INDEX t1994_valid_idx on t1994(valid);
GRANT SELECT on t1994 to nobody,apache;
    

create table t1995( 
  CONSTRAINT __t1995_check 
  CHECK(valid >= '1995-01-01 00:00+00'::timestamptz 
        and valid < '1996-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1995_station_idx on t1995(station);
CREATE INDEX t1995_valid_idx on t1995(valid);
GRANT SELECT on t1995 to nobody,apache;
    

create table t1996( 
  CONSTRAINT __t1996_check 
  CHECK(valid >= '1996-01-01 00:00+00'::timestamptz 
        and valid < '1997-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1996_station_idx on t1996(station);
CREATE INDEX t1996_valid_idx on t1996(valid);
GRANT SELECT on t1996 to nobody,apache;
    

create table t1997( 
  CONSTRAINT __t1997_check 
  CHECK(valid >= '1997-01-01 00:00+00'::timestamptz 
        and valid < '1998-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1997_station_idx on t1997(station);
CREATE INDEX t1997_valid_idx on t1997(valid);
GRANT SELECT on t1997 to nobody,apache;
    

create table t1998( 
  CONSTRAINT __t1998_check 
  CHECK(valid >= '1998-01-01 00:00+00'::timestamptz 
        and valid < '1999-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1998_station_idx on t1998(station);
CREATE INDEX t1998_valid_idx on t1998(valid);
GRANT SELECT on t1998 to nobody,apache;
    

create table t1999( 
  CONSTRAINT __t1999_check 
  CHECK(valid >= '1999-01-01 00:00+00'::timestamptz 
        and valid < '2000-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1999_station_idx on t1999(station);
CREATE INDEX t1999_valid_idx on t1999(valid);
GRANT SELECT on t1999 to nobody,apache;
    

create table t2000( 
  CONSTRAINT __t2000_check 
  CHECK(valid >= '2000-01-01 00:00+00'::timestamptz 
        and valid < '2001-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_station_idx on t2000(station);
CREATE INDEX t2000_valid_idx on t2000(valid);
GRANT SELECT on t2000 to nobody,apache;
    

create table t2001( 
  CONSTRAINT __t2001_check 
  CHECK(valid >= '2001-01-01 00:00+00'::timestamptz 
        and valid < '2002-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_station_idx on t2001(station);
CREATE INDEX t2001_valid_idx on t2001(valid);
GRANT SELECT on t2001 to nobody,apache;
    

create table t2002( 
  CONSTRAINT __t2002_check 
  CHECK(valid >= '2002-01-01 00:00+00'::timestamptz 
        and valid < '2003-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_station_idx on t2002(station);
CREATE INDEX t2002_valid_idx on t2002(valid);
GRANT SELECT on t2002 to nobody,apache;
    

create table t2003( 
  CONSTRAINT __t2003_check 
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz 
        and valid < '2004-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_station_idx on t2003(station);
CREATE INDEX t2003_valid_idx on t2003(valid);
GRANT SELECT on t2003 to nobody,apache;
    

create table t2004( 
  CONSTRAINT __t2004_check 
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz 
        and valid < '2005-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_station_idx on t2004(station);
CREATE INDEX t2004_valid_idx on t2004(valid);
GRANT SELECT on t2004 to nobody,apache;
    

create table t2005( 
  CONSTRAINT __t2005_check 
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz 
        and valid < '2006-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_station_idx on t2005(station);
CREATE INDEX t2005_valid_idx on t2005(valid);
GRANT SELECT on t2005 to nobody,apache;
    

create table t2006( 
  CONSTRAINT __t2006_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz 
        and valid < '2007-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_station_idx on t2006(station);
CREATE INDEX t2006_valid_idx on t2006(valid);
GRANT SELECT on t2006 to nobody,apache;
    

create table t2007( 
  CONSTRAINT __t2007_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz 
        and valid < '2008-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_station_idx on t2007(station);
CREATE INDEX t2007_valid_idx on t2007(valid);
GRANT SELECT on t2007 to nobody,apache;
    

create table t2008( 
  CONSTRAINT __t2008_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_station_idx on t2008(station);
CREATE INDEX t2008_valid_idx on t2008(valid);
GRANT SELECT on t2008 to nobody,apache;
    

create table t2009( 
  CONSTRAINT __t2009_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_station_idx on t2009(station);
CREATE INDEX t2009_valid_idx on t2009(valid);
GRANT SELECT on t2009 to nobody,apache;
    

create table t2010( 
  CONSTRAINT __t2010_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_station_idx on t2010(station);
CREATE INDEX t2010_valid_idx on t2010(valid);
GRANT SELECT on t2010 to nobody,apache;
    

create table t2011( 
  CONSTRAINT __t2011_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_station_idx on t2011(station);
CREATE INDEX t2011_valid_idx on t2011(valid);
GRANT SELECT on t2011 to nobody,apache;
    

create table t2012( 
  CONSTRAINT __t2012_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_station_idx on t2012(station);
CREATE INDEX t2012_valid_idx on t2012(valid);
GRANT SELECT on t2012 to nobody,apache;
    

create table t2013( 
  CONSTRAINT __t2013_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_station_idx on t2013(station);
CREATE INDEX t2013_valid_idx on t2013(valid);
GRANT SELECT on t2013 to nobody,apache;


create table t2014( 
  CONSTRAINT __t2014_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_station_idx on t2014(station);
CREATE INDEX t2014_valid_idx on t2014(valid);
GRANT SELECT on t2014 to nobody,apache;

create table t2008_traffic( 
  CONSTRAINT __t2008_traffic_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (alldata_traffic);
CREATE INDEX t2008_traffic_station_idx on t2008_traffic(station);
CREATE INDEX t2008_traffic_valid_idx on t2008_traffic(valid);
GRANT SELECT on t2008_traffic to nobody,apache;
    

create table t2009_traffic( 
  CONSTRAINT __t2009_traffic_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (alldata_traffic);
CREATE INDEX t2009_traffic_station_idx on t2009_traffic(station);
CREATE INDEX t2009_traffic_valid_idx on t2009_traffic(valid);
GRANT SELECT on t2009_traffic to nobody,apache;
    

create table t2010_traffic( 
  CONSTRAINT __t2010_traffic_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (alldata_traffic);
CREATE INDEX t2010_traffic_station_idx on t2010_traffic(station);
CREATE INDEX t2010_traffic_valid_idx on t2010_traffic(valid);
GRANT SELECT on t2010_traffic to nobody,apache;
    

create table t2011_traffic( 
  CONSTRAINT __t2011_traffic_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (alldata_traffic);
CREATE INDEX t2011_traffic_station_idx on t2011_traffic(station);
CREATE INDEX t2011_traffic_valid_idx on t2011_traffic(valid);
GRANT SELECT on t2011_traffic to nobody,apache;
    

create table t2012_traffic( 
  CONSTRAINT __t2012_traffic_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (alldata_traffic);
CREATE INDEX t2012_traffic_station_idx on t2012_traffic(station);
CREATE INDEX t2012_traffic_valid_idx on t2012_traffic(valid);
GRANT SELECT on t2012_traffic to nobody,apache;
    

create table t2013_traffic( 
  CONSTRAINT __t2013_traffic_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (alldata_traffic);
CREATE INDEX t2013_traffic_station_idx on t2013_traffic(station);
CREATE INDEX t2013_traffic_valid_idx on t2013_traffic(valid);
GRANT SELECT on t2013_traffic to nobody,apache;

create table t2014_traffic( 
  CONSTRAINT __t2014_traffic_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata_traffic);
CREATE INDEX t2014_traffic_station_idx on t2014_traffic(station);
CREATE INDEX t2014_traffic_valid_idx on t2014_traffic(valid);
GRANT SELECT on t2014_traffic to nobody,apache;

create table t2008_soil( 
  CONSTRAINT __t2008_soil_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (alldata_soil);
CREATE INDEX t2008_soil_station_idx on t2008_soil(station);
CREATE INDEX t2008_soil_valid_idx on t2008_soil(valid);
GRANT SELECT on t2008_soil to nobody,apache;
    

create table t2009_soil( 
  CONSTRAINT __t2009_soil_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (alldata_soil);
CREATE INDEX t2009_soil_station_idx on t2009_soil(station);
CREATE INDEX t2009_soil_valid_idx on t2009_soil(valid);
GRANT SELECT on t2009_soil to nobody,apache;
    

create table t2010_soil( 
  CONSTRAINT __t2010_soil_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (alldata_soil);
CREATE INDEX t2010_soil_station_idx on t2010_soil(station);
CREATE INDEX t2010_soil_valid_idx on t2010_soil(valid);
GRANT SELECT on t2010_soil to nobody,apache;
    

create table t2011_soil( 
  CONSTRAINT __t2011_soil_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (alldata_soil);
CREATE INDEX t2011_soil_station_idx on t2011_soil(station);
CREATE INDEX t2011_soil_valid_idx on t2011_soil(valid);
GRANT SELECT on t2011_soil to nobody,apache;
    

create table t2012_soil( 
  CONSTRAINT __t2012_soil_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (alldata_soil);
CREATE INDEX t2012_soil_station_idx on t2012_soil(station);
CREATE INDEX t2012_soil_valid_idx on t2012_soil(valid);
GRANT SELECT on t2012_soil to nobody,apache;
    

create table t2013_soil( 
  CONSTRAINT __t2013_soil_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (alldata_soil);
CREATE INDEX t2013_soil_station_idx on t2013_soil(station);
CREATE INDEX t2013_soil_valid_idx on t2013_soil(valid);
GRANT SELECT on t2013_soil to nobody,apache;


create table t2014_soil( 
  CONSTRAINT __t2014_soil_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata_soil);
CREATE INDEX t2014_soil_station_idx on t2014_soil(station);
CREATE INDEX t2014_soil_valid_idx on t2014_soil(valid);
GRANT SELECT on t2014_soil to nobody,apache;

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
