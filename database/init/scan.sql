-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (3, now());

CREATE TABLE alldata(
	station varchar(5),
	valid timestamptz,
	tmpf real,
	dwpf real,
	srad real,
	drct real,
	sknt real,
	relh real,
	pres real,
	c1tmpf real,
	c2tmpf real,
	c3tmpf real,
	c4tmpf real,
	c5tmpf real,
	c1smv real,
	c2smv real,
	c3smv real,
	c4smv real,
	c5smv real,
	phour real
);
GRANT SELECT on alldata to nobody,apache;

create table t2000_hourly( 
  CONSTRAINT __t2000_hourly_check 
  CHECK(valid >= '2000-01-01 00:00+00'::timestamptz 
        and valid < '2001-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_hourly_idx on t2000_hourly(station, valid);
GRANT SELECT on t2000_hourly to nobody,apache;
    

create table t2001_hourly( 
  CONSTRAINT __t2001_hourly_check 
  CHECK(valid >= '2001-01-01 00:00+00'::timestamptz 
        and valid < '2002-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_hourly_idx on t2001_hourly(station, valid);
GRANT SELECT on t2001_hourly to nobody,apache;
    

create table t2002_hourly( 
  CONSTRAINT __t2002_hourly_check 
  CHECK(valid >= '2002-01-01 00:00+00'::timestamptz 
        and valid < '2003-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_hourly_idx on t2002_hourly(station, valid);
GRANT SELECT on t2002_hourly to nobody,apache;
    

create table t2003_hourly( 
  CONSTRAINT __t2003_hourly_check 
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz 
        and valid < '2004-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_hourly_idx on t2003_hourly(station, valid);
GRANT SELECT on t2003_hourly to nobody,apache;
    

create table t2004_hourly( 
  CONSTRAINT __t2004_hourly_check 
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz 
        and valid < '2005-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_hourly_idx on t2004_hourly(station, valid);
GRANT SELECT on t2004_hourly to nobody,apache;
    

create table t2005_hourly( 
  CONSTRAINT __t2005_hourly_check 
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz 
        and valid < '2006-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_hourly_idx on t2005_hourly(station, valid);
GRANT SELECT on t2005_hourly to nobody,apache;
    

create table t2006_hourly( 
  CONSTRAINT __t2006_hourly_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz 
        and valid < '2007-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_hourly_idx on t2006_hourly(station, valid);
GRANT SELECT on t2006_hourly to nobody,apache;
    

create table t2007_hourly( 
  CONSTRAINT __t2007_hourly_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz 
        and valid < '2008-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_hourly_idx on t2007_hourly(station, valid);
GRANT SELECT on t2007_hourly to nobody,apache;
    

create table t2008_hourly( 
  CONSTRAINT __t2008_hourly_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_hourly_idx on t2008_hourly(station, valid);
GRANT SELECT on t2008_hourly to nobody,apache;
    

create table t2009_hourly( 
  CONSTRAINT __t2009_hourly_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_hourly_idx on t2009_hourly(station, valid);
GRANT SELECT on t2009_hourly to nobody,apache;
    

create table t2010_hourly( 
  CONSTRAINT __t2010_hourly_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_hourly_idx on t2010_hourly(station, valid);
GRANT SELECT on t2010_hourly to nobody,apache;
    

create table t2011_hourly( 
  CONSTRAINT __t2011_hourly_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_hourly_idx on t2011_hourly(station, valid);
GRANT SELECT on t2011_hourly to nobody,apache;
    

create table t2012_hourly( 
  CONSTRAINT __t2012_hourly_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_hourly_idx on t2012_hourly(station, valid);
GRANT SELECT on t2012_hourly to nobody,apache;
    

create table t2013_hourly( 
  CONSTRAINT __t2013_hourly_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_hourly_idx on t2013_hourly(station, valid);
GRANT SELECT on t2013_hourly to nobody,apache;

create table t2014_hourly( 
  CONSTRAINT __t2014_hourly_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_hourly_idx on t2014_hourly(station, valid);
GRANT SELECT on t2014_hourly to nobody,apache;

create table t2015_hourly( 
  CONSTRAINT __t2015_hourly_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_hourly_idx on t2015_hourly(station, valid);
GRANT SELECT on t2015_hourly to nobody,apache;

create table t2016_hourly( 
  CONSTRAINT __t2016_hourly_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_hourly_idx on t2016_hourly(station, valid);
GRANT SELECT on t2016_hourly to nobody,apache;

create table t2017_hourly( 
  CONSTRAINT __t2017_hourly_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_hourly_idx on t2017_hourly(station, valid);
GRANT SELECT on t2017_hourly to nobody,apache;

create table t2018_hourly( 
  CONSTRAINT __t2018_hourly_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz 
        and valid < '2019-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_hourly_idx on t2018_hourly(station, valid);
GRANT SELECT on t2018_hourly to nobody,apache;
