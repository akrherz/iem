-- Storage of USCRN sub-hourly data

CREATE TABLE uscrn_alldata(
  station varchar(5),
  valid timestamptz,
  tmpc real,
  precip_mm real,
  srad real,
  srad_flag char(1),
  skinc real,
  skinc_flag char(1),
  skinc_type char(1),
  rh real,
  rh_flag real,
  vsm5 real,
  soilc5 real,
  wetness real,
  wetness_flag char(1),
  wind_mps real,
  wind_mps_flag char(1));
GRANT SELECT on uscrn_alldata to nobody,apache;
GRANT ALL on uscrn_alldata to mesonet,ldm;

create table uscrn_t2006( 
  CONSTRAINT __t2006_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz 
        and valid < '2007-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2006_station_idx on uscrn_t2006(station);
CREATE INDEX uscrn_t2006_valid_idx on uscrn_t2006(valid);
GRANT SELECT on uscrn_t2006 to nobody,apache;
GRANT ALL on uscrn_t2006 to ldm,mesonet;
    

create table uscrn_t2007( 
  CONSTRAINT __t2007_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz 
        and valid < '2008-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2007_station_idx on uscrn_t2007(station);
CREATE INDEX uscrn_t2007_valid_idx on uscrn_t2007(valid);
GRANT SELECT on uscrn_t2007 to nobody,apache;
GRANT ALL on uscrn_t2007 to ldm,mesonet;
    

create table uscrn_t2008( 
  CONSTRAINT __t2008_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2008_station_idx on uscrn_t2008(station);
CREATE INDEX uscrn_t2008_valid_idx on uscrn_t2008(valid);
GRANT SELECT on uscrn_t2008 to nobody,apache;
GRANT ALL on uscrn_t2008 to ldm,mesonet;
    

create table uscrn_t2009( 
  CONSTRAINT __t2009_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2009_station_idx on uscrn_t2009(station);
CREATE INDEX uscrn_t2009_valid_idx on uscrn_t2009(valid);
GRANT SELECT on uscrn_t2009 to nobody,apache;
GRANT ALL on uscrn_t2009 to ldm,mesonet;
    

create table uscrn_t2010( 
  CONSTRAINT __t2010_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2010_station_idx on uscrn_t2010(station);
CREATE INDEX uscrn_t2010_valid_idx on uscrn_t2010(valid);
GRANT SELECT on uscrn_t2010 to nobody,apache;
GRANT ALL on uscrn_t2010 to ldm,mesonet;
    

create table uscrn_t2011( 
  CONSTRAINT __t2011_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2011_station_idx on uscrn_t2011(station);
CREATE INDEX uscrn_t2011_valid_idx on uscrn_t2011(valid);
GRANT SELECT on uscrn_t2011 to nobody,apache;
GRANT ALL on uscrn_t2011 to ldm,mesonet;
    

create table uscrn_t2012( 
  CONSTRAINT __t2012_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2012_station_idx on uscrn_t2012(station);
CREATE INDEX uscrn_t2012_valid_idx on uscrn_t2012(valid);
GRANT SELECT on uscrn_t2012 to nobody,apache;
GRANT ALL on uscrn_t2012 to ldm,mesonet;
    

create table uscrn_t2013( 
  CONSTRAINT __t2013_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2013_station_idx on uscrn_t2013(station);
CREATE INDEX uscrn_t2013_valid_idx on uscrn_t2013(valid);
GRANT SELECT on uscrn_t2013 to nobody,apache;
GRANT ALL on uscrn_t2013 to ldm,mesonet;
    

create table uscrn_t2014( 
  CONSTRAINT __t2014_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2014_station_idx on uscrn_t2014(station);
CREATE INDEX uscrn_t2014_valid_idx on uscrn_t2014(valid);
GRANT SELECT on uscrn_t2014 to nobody,apache;
GRANT ALL on uscrn_t2014 to ldm,mesonet;
    

create table uscrn_t2015( 
  CONSTRAINT __t2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2015_station_idx on uscrn_t2015(station);
CREATE INDEX uscrn_t2015_valid_idx on uscrn_t2015(valid);
GRANT SELECT on uscrn_t2015 to nobody,apache;
GRANT ALL on uscrn_t2015 to ldm,mesonet;
    

create table uscrn_t2016( 
  CONSTRAINT __t2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2016_station_idx on uscrn_t2016(station);
CREATE INDEX uscrn_t2016_valid_idx on uscrn_t2016(valid);
GRANT SELECT on uscrn_t2016 to nobody,apache;
GRANT ALL on uscrn_t2016 to ldm,mesonet;
    

create table uscrn_t2017( 
  CONSTRAINT __t2017_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2017_station_idx on uscrn_t2017(station);
CREATE INDEX uscrn_t2017_valid_idx on uscrn_t2017(valid);
GRANT SELECT on uscrn_t2017 to nobody,apache;
GRANT ALL on uscrn_t2017 to ldm,mesonet;
    

create table uscrn_t2018( 
  CONSTRAINT __t2018_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz 
        and valid < '2019-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2018_station_idx on uscrn_t2018(station);
CREATE INDEX uscrn_t2018_valid_idx on uscrn_t2018(valid);
GRANT SELECT on uscrn_t2018 to nobody,apache;
GRANT ALL on uscrn_t2018 to ldm,mesonet;
    
