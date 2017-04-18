-- Storage of FFG Guidance
CREATE TABLE ffg(
  ugc char(6),
  valid timestamptz,
  hour01 real,
  hour03 real,
  hour06 real,
  hour12 real,
  hour24 real);
GRANT SELECT on ffg to nobody,apache;
GRANT ALL on ffg to ldm,mesonet;

CREATE TABLE ffg_2000(
  CONSTRAINT __ffg_2000_check 
  CHECK(valid >= '2000-01-01 00:00+00'::timestamptz
        and valid < '2001-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2000_ugc_idx on ffg_2000(ugc);
CREATE INDEX ffg_2000_valid_idx on ffg_2000(valid);
GRANT ALL on ffg_2000 to ldm,mesonet;
GRANT SELECT on ffg_2000 to nobody,apache;
    

CREATE TABLE ffg_2001(
  CONSTRAINT __ffg_2001_check 
  CHECK(valid >= '2001-01-01 00:00+00'::timestamptz
        and valid < '2002-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2001_ugc_idx on ffg_2001(ugc);
CREATE INDEX ffg_2001_valid_idx on ffg_2001(valid);
GRANT ALL on ffg_2001 to ldm,mesonet;
GRANT SELECT on ffg_2001 to nobody,apache;
    

CREATE TABLE ffg_2002(
  CONSTRAINT __ffg_2002_check 
  CHECK(valid >= '2002-01-01 00:00+00'::timestamptz
        and valid < '2003-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2002_ugc_idx on ffg_2002(ugc);
CREATE INDEX ffg_2002_valid_idx on ffg_2002(valid);
GRANT ALL on ffg_2002 to ldm,mesonet;
GRANT SELECT on ffg_2002 to nobody,apache;


CREATE TABLE ffg_2003(
  CONSTRAINT __ffg_2003_check 
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz
        and valid < '2004-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2003_ugc_idx on ffg_2003(ugc);
CREATE INDEX ffg_2003_valid_idx on ffg_2003(valid);
GRANT ALL on ffg_2003 to ldm,mesonet;
GRANT SELECT on ffg_2003 to nobody,apache;
    

CREATE TABLE ffg_2004(
  CONSTRAINT __ffg_2004_check 
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz
        and valid < '2005-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2004_ugc_idx on ffg_2004(ugc);
CREATE INDEX ffg_2004_valid_idx on ffg_2004(valid);
GRANT ALL on ffg_2004 to ldm,mesonet;
GRANT SELECT on ffg_2004 to nobody,apache;
    

CREATE TABLE ffg_2005(
  CONSTRAINT __ffg_2005_check 
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz
        and valid < '2006-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2005_ugc_idx on ffg_2005(ugc);
CREATE INDEX ffg_2005_valid_idx on ffg_2005(valid);
GRANT ALL on ffg_2005 to ldm,mesonet;
GRANT SELECT on ffg_2005 to nobody,apache;
    

CREATE TABLE ffg_2006(
  CONSTRAINT __ffg_2006_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz
        and valid < '2007-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2006_ugc_idx on ffg_2006(ugc);
CREATE INDEX ffg_2006_valid_idx on ffg_2006(valid);
GRANT ALL on ffg_2006 to ldm,mesonet;
GRANT SELECT on ffg_2006 to nobody,apache;
    

CREATE TABLE ffg_2007(
  CONSTRAINT __ffg_2007_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz
        and valid < '2008-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2007_ugc_idx on ffg_2007(ugc);
CREATE INDEX ffg_2007_valid_idx on ffg_2007(valid);
GRANT ALL on ffg_2007 to ldm,mesonet;
GRANT SELECT on ffg_2007 to nobody,apache;
    

CREATE TABLE ffg_2008(
  CONSTRAINT __ffg_2008_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz
        and valid < '2009-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2008_ugc_idx on ffg_2008(ugc);
CREATE INDEX ffg_2008_valid_idx on ffg_2008(valid);
GRANT ALL on ffg_2008 to ldm,mesonet;
GRANT SELECT on ffg_2008 to nobody,apache;
    

CREATE TABLE ffg_2009(
  CONSTRAINT __ffg_2009_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz
        and valid < '2010-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2009_ugc_idx on ffg_2009(ugc);
CREATE INDEX ffg_2009_valid_idx on ffg_2009(valid);
GRANT ALL on ffg_2009 to ldm,mesonet;
GRANT SELECT on ffg_2009 to nobody,apache;
    

CREATE TABLE ffg_2010(
  CONSTRAINT __ffg_2010_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz
        and valid < '2011-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2010_ugc_idx on ffg_2010(ugc);
CREATE INDEX ffg_2010_valid_idx on ffg_2010(valid);
GRANT ALL on ffg_2010 to ldm,mesonet;
GRANT SELECT on ffg_2010 to nobody,apache;
    

CREATE TABLE ffg_2011(
  CONSTRAINT __ffg_2011_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz
        and valid < '2012-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2011_ugc_idx on ffg_2011(ugc);
CREATE INDEX ffg_2011_valid_idx on ffg_2011(valid);
GRANT ALL on ffg_2011 to ldm,mesonet;
GRANT SELECT on ffg_2011 to nobody,apache;
    

CREATE TABLE ffg_2012(
  CONSTRAINT __ffg_2012_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz
        and valid < '2013-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2012_ugc_idx on ffg_2012(ugc);
CREATE INDEX ffg_2012_valid_idx on ffg_2012(valid);
GRANT ALL on ffg_2012 to ldm,mesonet;
GRANT SELECT on ffg_2012 to nobody,apache;
    

CREATE TABLE ffg_2013(
  CONSTRAINT __ffg_2013_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz
        and valid < '2014-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2013_ugc_idx on ffg_2013(ugc);
CREATE INDEX ffg_2013_valid_idx on ffg_2013(valid);
GRANT ALL on ffg_2013 to ldm,mesonet;
GRANT SELECT on ffg_2013 to nobody,apache;
    

CREATE TABLE ffg_2014(
  CONSTRAINT __ffg_2014_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz
        and valid < '2015-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2014_ugc_idx on ffg_2014(ugc);
CREATE INDEX ffg_2014_valid_idx on ffg_2014(valid);
GRANT ALL on ffg_2014 to ldm,mesonet;
GRANT SELECT on ffg_2014 to nobody,apache;
    

CREATE TABLE ffg_2015(
  CONSTRAINT __ffg_2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz
        and valid < '2016-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2015_ugc_idx on ffg_2015(ugc);
CREATE INDEX ffg_2015_valid_idx on ffg_2015(valid);
GRANT ALL on ffg_2015 to ldm,mesonet;
GRANT SELECT on ffg_2015 to nobody,apache;
    

CREATE TABLE ffg_2016(
  CONSTRAINT __ffg_2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz
        and valid < '2017-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2016_ugc_idx on ffg_2016(ugc);
CREATE INDEX ffg_2016_valid_idx on ffg_2016(valid);
GRANT ALL on ffg_2016 to ldm,mesonet;
GRANT SELECT on ffg_2016 to nobody,apache;
    

CREATE TABLE ffg_2017(
  CONSTRAINT __ffg_2017_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz
        and valid < '2018-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2017_ugc_idx on ffg_2017(ugc);
CREATE INDEX ffg_2017_valid_idx on ffg_2017(valid);
GRANT ALL on ffg_2017 to ldm,mesonet;
GRANT SELECT on ffg_2017 to nobody,apache;

    
