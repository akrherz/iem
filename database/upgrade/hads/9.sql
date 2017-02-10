ALTER TABLE raw2002 NO INHERIT alldata;
ALTER TABLE raw2003 NO INHERIT alldata;
ALTER TABLE raw2004 NO INHERIT alldata;
ALTER TABLE raw2005 NO INHERIT alldata;
ALTER TABLE raw2006 NO INHERIT alldata;
ALTER TABLE raw2007 NO INHERIT alldata;
ALTER TABLE raw2008 NO INHERIT alldata;
ALTER TABLE raw2009 NO INHERIT alldata;
ALTER TABLE raw2010 NO INHERIT alldata;
ALTER TABLE raw2011 NO INHERIT alldata;
ALTER TABLE raw2012 NO INHERIT alldata;
ALTER TABLE raw2013 NO INHERIT alldata;
ALTER TABLE raw2014 NO INHERIT alldata;
ALTER TABLE raw2015 NO INHERIT alldata;
ALTER TABLE raw2016 NO INHERIT alldata;
ALTER TABLE raw2017 NO INHERIT alldata;

DROP TABLE alldata;

-- Storage of common / instantaneous data values
CREATE TABLE alldata(
	station varchar(8),
	valid timestamptz,
	tmpf real,
	dwpf real,
	sknt real,
	drct real);
GRANT SELECT on alldata to nobody,apache;

create table t2002( 
  CONSTRAINT __t2002_check 
  CHECK(valid >= '2002-01-01 00:00+00'::timestamptz 
        and valid < '2003-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_idx on t2002(station, valid);
CREATE INDEX t2002_valid_idx on t2002(valid);
grant select on t2002 to nobody,apache;

create table t2003( 
  CONSTRAINT __t2003_check 
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz 
        and valid < '2004-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_idx on t2003(station, valid);
CREATE INDEX t2003_valid_idx on t2003(valid);
grant select on t2003 to nobody,apache;


create table t2004( 
  CONSTRAINT __t2004_check 
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz 
        and valid < '2005-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_idx on t2004(station, valid);
CREATE INDEX t2004_valid_idx on t2004(valid);
grant select on t2004 to nobody,apache;


create table t2005( 
  CONSTRAINT __t2005_check 
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz 
        and valid < '2006-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_idx on t2005(station, valid);
CREATE INDEX t2005_valid_idx on t2005(valid);
grant select on t2005 to nobody,apache;


create table t2006( 
  CONSTRAINT __t2006_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz 
        and valid < '2007-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_idx on t2006(station, valid);
CREATE INDEX t2006_valid_idx on t2006(valid);
grant select on t2006 to nobody,apache;


create table t2007( 
  CONSTRAINT __t2007_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz 
        and valid < '2008-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_idx on t2007(station, valid);
CREATE INDEX t2007_valid_idx on t2007(valid);
grant select on t2007 to nobody,apache;


create table t2008( 
  CONSTRAINT __t2008_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_idx on t2008(station, valid);
CREATE INDEX t2008_valid_idx on t2008(valid);
grant select on t2008 to nobody,apache;


create table t2009( 
  CONSTRAINT __t2009_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_idx on t2009(station, valid);
CREATE INDEX t2009_valid_idx on t2009(valid);
grant select on t2009 to nobody,apache;


create table t2010( 
  CONSTRAINT __t2010_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_idx on t2010(station, valid);
CREATE INDEX t2010_valid_idx on t2010(valid);
grant select on t2010 to nobody,apache;


create table t2011( 
  CONSTRAINT __t2011_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_idx on t2011(station, valid);
CREATE INDEX t2011_valid_idx on t2011(valid);
grant select on t2011 to nobody,apache;


create table t2012( 
  CONSTRAINT __t2012_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_idx on t2012(station, valid);
CREATE INDEX t2012_valid_idx on t2012(valid);
grant select on t2012 to nobody,apache;


create table t2013( 
  CONSTRAINT __t2013_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_idx on t2013(station, valid);
CREATE INDEX t2013_valid_idx on t2013(valid);
grant select on t2013 to nobody,apache;


create table t2014( 
  CONSTRAINT __t2014_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_idx on t2014(station, valid);
CREATE INDEX t2014_valid_idx on t2014(valid);
grant select on t2014 to nobody,apache;


create table t2015( 
  CONSTRAINT __t2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_idx on t2015(station, valid);
CREATE INDEX t2015_valid_idx on t2015(valid);
grant select on t2015 to nobody,apache;


create table t2016( 
  CONSTRAINT __t2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_idx on t2016(station, valid);
CREATE INDEX t2016_valid_idx on t2016(valid);
grant select on t2016 to nobody,apache;


create table t2017( 
  CONSTRAINT __t2017_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_idx on t2017(station, valid);
CREATE INDEX t2017_valid_idx on t2017(valid);
grant select on t2017 to nobody,apache;
