
-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (6, now());

CREATE TABLE products(
  data text,
  pil char(6),
  entered timestamptz,
  source char(4),
  wmo char(6)
);
GRANT SELECT on products to nobody,apache;

-- ________________________________________________________________
create table products_1996_0106(
  CONSTRAINT __products19960106_check
  CHECK(entered >= '1996-01-01 00:00+00'::timestamptz
        and entered < '1996-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1996_0106_pil_idx on products_1996_0106(pil);
CREATE INDEX products_1996_0106_entered_idx on products_1996_0106(entered);
CREATE INDEX products_1996_0106_source_idx on products_1996_0106(source);
create index products_1996_0106_pe_idx on products_1996_0106(pil, entered);
GRANT all on products_1996_0106 to mesonet,ldm;
grant select on products_1996_0106 to nobody,apache;

-- ________________________________________________________________
create table products_1996_0712(
  CONSTRAINT __products19960712_check
  CHECK(entered >= '1996-07-01 00:00+00'::timestamptz
        and entered < '1997-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1996_0712_pil_idx on products_1996_0712(pil);
CREATE INDEX products_1996_0712_entered_idx on products_1996_0712(entered);
CREATE INDEX products_1996_0712_source_idx on products_1996_0712(source);
create index products_1996_0712_pe_idx on products_1996_0712(pil, entered);
GRANT all on products_1996_0712 to mesonet,ldm;
grant select on products_1996_0712 to nobody,apache;
    

-- ________________________________________________________________
create table products_1997_0106(
  CONSTRAINT __products19970106_check
  CHECK(entered >= '1997-01-01 00:00+00'::timestamptz
        and entered < '1997-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1997_0106_pil_idx on products_1997_0106(pil);
CREATE INDEX products_1997_0106_entered_idx on products_1997_0106(entered);
CREATE INDEX products_1997_0106_source_idx on products_1997_0106(source);
create index products_1997_0106_pe_idx on products_1997_0106(pil, entered);
GRANT all on products_1997_0106 to mesonet,ldm;
grant select on products_1997_0106 to nobody,apache;

-- ________________________________________________________________
create table products_1997_0712(
  CONSTRAINT __products19970712_check
  CHECK(entered >= '1997-07-01 00:00+00'::timestamptz
        and entered < '1998-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1997_0712_pil_idx on products_1997_0712(pil);
CREATE INDEX products_1997_0712_entered_idx on products_1997_0712(entered);
CREATE INDEX products_1997_0712_source_idx on products_1997_0712(source);
create index products_1997_0712_pe_idx on products_1997_0712(pil, entered);
GRANT all on products_1997_0712 to mesonet,ldm;
grant select on products_1997_0712 to nobody,apache;
    

-- ________________________________________________________________
create table products_1998_0106(
  CONSTRAINT __products19980106_check
  CHECK(entered >= '1998-01-01 00:00+00'::timestamptz
        and entered < '1998-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1998_0106_pil_idx on products_1998_0106(pil);
CREATE INDEX products_1998_0106_entered_idx on products_1998_0106(entered);
CREATE INDEX products_1998_0106_source_idx on products_1998_0106(source);
create index products_1998_0106_pe_idx on products_1998_0106(pil, entered);
GRANT all on products_1998_0106 to mesonet,ldm;
grant select on products_1998_0106 to nobody,apache;

-- ________________________________________________________________
create table products_1998_0712(
  CONSTRAINT __products19980712_check
  CHECK(entered >= '1998-07-01 00:00+00'::timestamptz
        and entered < '1999-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1998_0712_pil_idx on products_1998_0712(pil);
CREATE INDEX products_1998_0712_entered_idx on products_1998_0712(entered);
CREATE INDEX products_1998_0712_source_idx on products_1998_0712(source);
create index products_1998_0712_pe_idx on products_1998_0712(pil, entered);
GRANT all on products_1998_0712 to mesonet,ldm;
grant select on products_1998_0712 to nobody,apache;
    

-- ________________________________________________________________
create table products_1999_0106(
  CONSTRAINT __products19990106_check
  CHECK(entered >= '1999-01-01 00:00+00'::timestamptz
        and entered < '1999-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1999_0106_pil_idx on products_1999_0106(pil);
CREATE INDEX products_1999_0106_entered_idx on products_1999_0106(entered);
CREATE INDEX products_1999_0106_source_idx on products_1999_0106(source);
create index products_1999_0106_pe_idx on products_1999_0106(pil, entered);
GRANT all on products_1999_0106 to mesonet,ldm;
grant select on products_1999_0106 to nobody,apache;

-- ________________________________________________________________
create table products_1999_0712(
  CONSTRAINT __products19990712_check
  CHECK(entered >= '1999-07-01 00:00+00'::timestamptz
        and entered < '2000-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1999_0712_pil_idx on products_1999_0712(pil);
CREATE INDEX products_1999_0712_entered_idx on products_1999_0712(entered);
CREATE INDEX products_1999_0712_source_idx on products_1999_0712(source);
create index products_1999_0712_pe_idx on products_1999_0712(pil, entered);
GRANT all on products_1999_0712 to mesonet,ldm;
grant select on products_1999_0712 to nobody,apache;


-- ________________________________________________________________
create table products_2000_0106( 
  CONSTRAINT __products20000106_check 
  CHECK(entered >= '2000-01-01 00:00+00'::timestamptz 
        and entered < '2000-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2000_0106_pil_idx on products_2000_0106(pil);
CREATE INDEX products_2000_0106_entered_idx on products_2000_0106(entered);
CREATE INDEX products_2000_0106_source_idx on products_2000_0106(source);
grant select on products_2000_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2000_0712( 
  CONSTRAINT __products20000712_check 
  CHECK(entered >= '2000-07-01 00:00+00'::timestamptz 
        and entered < '2001-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2000_0712_pil_idx on products_2000_0712(pil);
CREATE INDEX products_2000_0712_entered_idx on products_2000_0712(entered);
CREATE INDEX products_2000_0712_source_idx on products_2000_0712(source);
grant select on products_2000_0712 to nobody,apache;

  

-- ________________________________________________________________
create table products_2001_0106( 
  CONSTRAINT __products20010106_check 
  CHECK(entered >= '2001-01-01 00:00+00'::timestamptz 
        and entered < '2001-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2001_0106_pil_idx on products_2001_0106(pil);
CREATE INDEX products_2001_0106_entered_idx on products_2001_0106(entered);
CREATE INDEX products_2001_0106_source_idx on products_2001_0106(source);
grant select on products_2001_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2001_0712( 
  CONSTRAINT __products20010712_check 
  CHECK(entered >= '2001-07-01 00:00+00'::timestamptz 
        and entered < '2002-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2001_0712_pil_idx on products_2001_0712(pil);
CREATE INDEX products_2001_0712_entered_idx on products_2001_0712(entered);
CREATE INDEX products_2001_0712_source_idx on products_2001_0712(source);
grant select on products_2001_0712 to nobody,apache;

  

-- ________________________________________________________________
create table products_2002_0106( 
  CONSTRAINT __products20020106_check 
  CHECK(entered >= '2002-01-01 00:00+00'::timestamptz 
        and entered < '2002-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2002_0106_pil_idx on products_2002_0106(pil);
CREATE INDEX products_2002_0106_entered_idx on products_2002_0106(entered);
CREATE INDEX products_2002_0106_source_idx on products_2002_0106(source);
grant select on products_2002_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2002_0712( 
  CONSTRAINT __products20020712_check 
  CHECK(entered >= '2002-07-01 00:00+00'::timestamptz 
        and entered < '2003-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2002_0712_pil_idx on products_2002_0712(pil);
CREATE INDEX products_2002_0712_entered_idx on products_2002_0712(entered);
CREATE INDEX products_2002_0712_source_idx on products_2002_0712(source);
grant select on products_2002_0712 to nobody,apache;

  

-- ________________________________________________________________
create table products_2003_0106( 
  CONSTRAINT __products20030106_check 
  CHECK(entered >= '2003-01-01 00:00+00'::timestamptz 
        and entered < '2003-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2003_0106_pil_idx on products_2003_0106(pil);
CREATE INDEX products_2003_0106_entered_idx on products_2003_0106(entered);
CREATE INDEX products_2003_0106_source_idx on products_2003_0106(source);
grant select on products_2003_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2003_0712( 
  CONSTRAINT __products20030712_check 
  CHECK(entered >= '2003-07-01 00:00+00'::timestamptz 
        and entered < '2004-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2003_0712_pil_idx on products_2003_0712(pil);
CREATE INDEX products_2003_0712_entered_idx on products_2003_0712(entered);
CREATE INDEX products_2003_0712_source_idx on products_2003_0712(source);
grant select on products_2003_0712 to nobody,apache;

  

-- ________________________________________________________________
create table products_2004_0106( 
  CONSTRAINT __products20040106_check 
  CHECK(entered >= '2004-01-01 00:00+00'::timestamptz 
        and entered < '2004-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2004_0106_pil_idx on products_2004_0106(pil);
CREATE INDEX products_2004_0106_entered_idx on products_2004_0106(entered);
CREATE INDEX products_2004_0106_source_idx on products_2004_0106(source);
grant select on products_2004_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2004_0712( 
  CONSTRAINT __products20040712_check 
  CHECK(entered >= '2004-07-01 00:00+00'::timestamptz 
        and entered < '2005-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2004_0712_pil_idx on products_2004_0712(pil);
CREATE INDEX products_2004_0712_entered_idx on products_2004_0712(entered);
CREATE INDEX products_2004_0712_source_idx on products_2004_0712(source);
grant select on products_2004_0712 to nobody,apache;

  

-- ________________________________________________________________
create table products_2005_0106( 
  CONSTRAINT __products20050106_check 
  CHECK(entered >= '2005-01-01 00:00+00'::timestamptz 
        and entered < '2005-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2005_0106_pil_idx on products_2005_0106(pil);
CREATE INDEX products_2005_0106_entered_idx on products_2005_0106(entered);
CREATE INDEX products_2005_0106_source_idx on products_2005_0106(source);
grant select on products_2005_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2005_0712( 
  CONSTRAINT __products20050712_check 
  CHECK(entered >= '2005-07-01 00:00+00'::timestamptz 
        and entered < '2006-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2005_0712_pil_idx on products_2005_0712(pil);
CREATE INDEX products_2005_0712_entered_idx on products_2005_0712(entered);
CREATE INDEX products_2005_0712_source_idx on products_2005_0712(source);
grant select on products_2005_0712 to nobody,apache;

  

-- ________________________________________________________________
create table products_2006_0106( 
  CONSTRAINT __products20060106_check 
  CHECK(entered >= '2006-01-01 00:00+00'::timestamptz 
        and entered < '2006-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2006_0106_pil_idx on products_2006_0106(pil);
CREATE INDEX products_2006_0106_entered_idx on products_2006_0106(entered);
CREATE INDEX products_2006_0106_source_idx on products_2006_0106(source);
grant select on products_2006_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2006_0712( 
  CONSTRAINT __products20060712_check 
  CHECK(entered >= '2006-07-01 00:00+00'::timestamptz 
        and entered < '2007-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2006_0712_pil_idx on products_2006_0712(pil);
CREATE INDEX products_2006_0712_entered_idx on products_2006_0712(entered);
CREATE INDEX products_2006_0712_source_idx on products_2006_0712(source);
grant select on products_2006_0712 to nobody,apache;

  

-- ________________________________________________________________
create table products_2007_0106( 
  CONSTRAINT __products20070106_check 
  CHECK(entered >= '2007-01-01 00:00+00'::timestamptz 
        and entered < '2007-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2007_0106_pil_idx on products_2007_0106(pil);
CREATE INDEX products_2007_0106_entered_idx on products_2007_0106(entered);
CREATE INDEX products_2007_0106_source_idx on products_2007_0106(source);
grant select on products_2007_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2007_0712( 
  CONSTRAINT __products20070712_check 
  CHECK(entered >= '2007-07-01 00:00+00'::timestamptz 
        and entered < '2008-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2007_0712_pil_idx on products_2007_0712(pil);
CREATE INDEX products_2007_0712_entered_idx on products_2007_0712(entered);
CREATE INDEX products_2007_0712_source_idx on products_2007_0712(source);
grant select on products_2007_0712 to nobody,apache;

  

-- ________________________________________________________________
create table products_2008_0106( 
  CONSTRAINT __products20080106_check 
  CHECK(entered >= '2008-01-01 00:00+00'::timestamptz 
        and entered < '2008-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2008_0106_pil_idx on products_2008_0106(pil);
CREATE INDEX products_2008_0106_entered_idx on products_2008_0106(entered);
CREATE INDEX products_2008_0106_source_idx on products_2008_0106(source);
grant select on products_2008_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2008_0712( 
  CONSTRAINT __products20080712_check 
  CHECK(entered >= '2008-07-01 00:00+00'::timestamptz 
        and entered < '2009-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2008_0712_pil_idx on products_2008_0712(pil);
CREATE INDEX products_2008_0712_entered_idx on products_2008_0712(entered);
CREATE INDEX products_2008_0712_source_idx on products_2008_0712(source);
grant select on products_2008_0712 to nobody,apache;

  

-- ________________________________________________________________
create table products_2009_0106( 
  CONSTRAINT __products20090106_check 
  CHECK(entered >= '2009-01-01 00:00+00'::timestamptz 
        and entered < '2009-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2009_0106_pil_idx on products_2009_0106(pil);
CREATE INDEX products_2009_0106_entered_idx on products_2009_0106(entered);
CREATE INDEX products_2009_0106_source_idx on products_2009_0106(source);
grant select on products_2009_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2009_0712( 
  CONSTRAINT __products20090712_check 
  CHECK(entered >= '2009-07-01 00:00+00'::timestamptz 
        and entered < '2010-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2009_0712_pil_idx on products_2009_0712(pil);
CREATE INDEX products_2009_0712_entered_idx on products_2009_0712(entered);
CREATE INDEX products_2009_0712_source_idx on products_2009_0712(source);
grant select on products_2009_0712 to nobody,apache;

  

-- ________________________________________________________________
create table products_2010_0106( 
  CONSTRAINT __products20100106_check 
  CHECK(entered >= '2010-01-01 00:00+00'::timestamptz 
        and entered < '2010-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2010_0106_pil_idx on products_2010_0106(pil);
CREATE INDEX products_2010_0106_entered_idx on products_2010_0106(entered);
CREATE INDEX products_2010_0106_source_idx on products_2010_0106(source);
grant select on products_2010_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2010_0712( 
  CONSTRAINT __products20100712_check 
  CHECK(entered >= '2010-07-01 00:00+00'::timestamptz 
        and entered < '2011-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2010_0712_pil_idx on products_2010_0712(pil);
CREATE INDEX products_2010_0712_entered_idx on products_2010_0712(entered);
CREATE INDEX products_2010_0712_source_idx on products_2010_0712(source);
grant select on products_2010_0712 to nobody,apache;

  

-- ________________________________________________________________
create table products_2011_0106( 
  CONSTRAINT __products20110106_check 
  CHECK(entered >= '2011-01-01 00:00+00'::timestamptz 
        and entered < '2011-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2011_0106_pil_idx on products_2011_0106(pil);
CREATE INDEX products_2011_0106_entered_idx on products_2011_0106(entered);
CREATE INDEX products_2011_0106_source_idx on products_2011_0106(source);
grant select on products_2011_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2011_0712( 
  CONSTRAINT __products20110712_check 
  CHECK(entered >= '2011-07-01 00:00+00'::timestamptz 
        and entered < '2012-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2011_0712_pil_idx on products_2011_0712(pil);
CREATE INDEX products_2011_0712_entered_idx on products_2011_0712(entered);
CREATE INDEX products_2011_0712_source_idx on products_2011_0712(source);
grant select on products_2011_0712 to nobody,apache;

  

-- ________________________________________________________________
create table products_2012_0106( 
  CONSTRAINT __products20120106_check 
  CHECK(entered >= '2012-01-01 00:00+00'::timestamptz 
        and entered < '2012-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2012_0106_pil_idx on products_2012_0106(pil);
CREATE INDEX products_2012_0106_entered_idx on products_2012_0106(entered);
CREATE INDEX products_2012_0106_source_idx on products_2012_0106(source);
grant select on products_2012_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2012_0712( 
  CONSTRAINT __products20120712_check 
  CHECK(entered >= '2012-07-01 00:00+00'::timestamptz 
        and entered < '2013-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2012_0712_pil_idx on products_2012_0712(pil);
CREATE INDEX products_2012_0712_entered_idx on products_2012_0712(entered);
CREATE INDEX products_2012_0712_source_idx on products_2012_0712(source);
grant select on products_2012_0712 to nobody,apache;

  

-- ________________________________________________________________
create table products_2013_0106( 
  CONSTRAINT __products20130106_check 
  CHECK(entered >= '2013-01-01 00:00+00'::timestamptz 
        and entered < '2013-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2013_0106_pil_idx on products_2013_0106(pil);
CREATE INDEX products_2013_0106_entered_idx on products_2013_0106(entered);
CREATE INDEX products_2013_0106_source_idx on products_2013_0106(source);
grant select on products_2013_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2013_0712( 
  CONSTRAINT __products20130712_check 
  CHECK(entered >= '2013-07-01 00:00+00'::timestamptz 
        and entered < '2014-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2013_0712_pil_idx on products_2013_0712(pil);
CREATE INDEX products_2013_0712_entered_idx on products_2013_0712(entered);
CREATE INDEX products_2013_0712_source_idx on products_2013_0712(source);
grant select on products_2013_0712 to nobody,apache;

  

-- ________________________________________________________________
create table products_2014_0106( 
  CONSTRAINT __products20140106_check 
  CHECK(entered >= '2014-01-01 00:00+00'::timestamptz 
        and entered < '2014-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2014_0106_pil_idx on products_2014_0106(pil);
CREATE INDEX products_2014_0106_entered_idx on products_2014_0106(entered);
CREATE INDEX products_2014_0106_source_idx on products_2014_0106(source);
grant select on products_2014_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2014_0712( 
  CONSTRAINT __products20140712_check 
  CHECK(entered >= '2014-07-01 00:00+00'::timestamptz 
        and entered < '2015-01-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2014_0712_pil_idx on products_2014_0712(pil);
CREATE INDEX products_2014_0712_entered_idx on products_2014_0712(entered);
CREATE INDEX products_2014_0712_source_idx on products_2014_0712(source);
grant select on products_2014_0712 to nobody,apache;

-- ________________________________________________________________
create table products_2015_0106(
  CONSTRAINT __products20150106_check
  CHECK(entered >= '2015-01-01 00:00+00'::timestamptz
        and entered < '2015-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_2015_0106_pil_idx on products_2015_0106(pil);
CREATE INDEX products_2015_0106_entered_idx on products_2015_0106(entered);
CREATE INDEX products_2015_0106_source_idx on products_2015_0106(source);
grant select on products_2015_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2015_0712(
  CONSTRAINT __products20150712_check
  CHECK(entered >= '2015-07-01 00:00+00'::timestamptz
        and entered < '2016-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_2015_0712_pil_idx on products_2015_0712(pil);
CREATE INDEX products_2015_0712_entered_idx on products_2015_0712(entered);
CREATE INDEX products_2015_0712_source_idx on products_2015_0712(source);
grant select on products_2015_0712 to nobody,apache;

-- ________________________________________________________________
create table products_2016_0106(
  CONSTRAINT __products20160106_check
  CHECK(entered >= '2016-01-01 00:00+00'::timestamptz
        and entered < '2016-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_2016_0106_pil_idx on products_2016_0106(pil);
CREATE INDEX products_2016_0106_entered_idx on products_2016_0106(entered);
CREATE INDEX products_2016_0106_source_idx on products_2016_0106(source);
grant select on products_2016_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2016_0712(
  CONSTRAINT __products20160712_check
  CHECK(entered >= '2016-07-01 00:00+00'::timestamptz
        and entered < '2017-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_2016_0712_pil_idx on products_2016_0712(pil);
CREATE INDEX products_2016_0712_entered_idx on products_2016_0712(entered);
CREATE INDEX products_2016_0712_source_idx on products_2016_0712(source);
grant select on products_2016_0712 to nobody,apache;

create index products_2000_0106_pe_idx on products_2000_0106(pil, entered);
create index products_2000_0712_pe_idx on products_2000_0712(pil, entered);

create index products_2001_0106_pe_idx on products_2001_0106(pil, entered);
create index products_2001_0712_pe_idx on products_2001_0712(pil, entered);

create index products_2002_0106_pe_idx on products_2002_0106(pil, entered);
create index products_2002_0712_pe_idx on products_2002_0712(pil, entered);

create index products_2003_0106_pe_idx on products_2003_0106(pil, entered);
create index products_2003_0712_pe_idx on products_2003_0712(pil, entered);

create index products_2004_0106_pe_idx on products_2004_0106(pil, entered);
create index products_2004_0712_pe_idx on products_2004_0712(pil, entered);

create index products_2005_0106_pe_idx on products_2005_0106(pil, entered);
create index products_2005_0712_pe_idx on products_2005_0712(pil, entered);

create index products_2006_0106_pe_idx on products_2006_0106(pil, entered);
create index products_2006_0712_pe_idx on products_2006_0712(pil, entered);

create index products_2007_0106_pe_idx on products_2007_0106(pil, entered);
create index products_2007_0712_pe_idx on products_2007_0712(pil, entered);

create index products_2008_0106_pe_idx on products_2008_0106(pil, entered);
create index products_2008_0712_pe_idx on products_2008_0712(pil, entered);

create index products_2009_0106_pe_idx on products_2009_0106(pil, entered);
create index products_2009_0712_pe_idx on products_2009_0712(pil, entered);

create index products_2010_0106_pe_idx on products_2010_0106(pil, entered);
create index products_2010_0712_pe_idx on products_2010_0712(pil, entered);

create index products_2011_0106_pe_idx on products_2011_0106(pil, entered);
create index products_2011_0712_pe_idx on products_2011_0712(pil, entered);

create index products_2012_0106_pe_idx on products_2012_0106(pil, entered);
create index products_2012_0712_pe_idx on products_2012_0712(pil, entered);

create index products_2013_0106_pe_idx on products_2013_0106(pil, entered);
create index products_2013_0712_pe_idx on products_2013_0712(pil, entered);

create index products_2014_0106_pe_idx on products_2014_0106(pil, entered);
create index products_2014_0712_pe_idx on products_2014_0712(pil, entered);

create index products_2015_0106_pe_idx on products_2015_0106(pil, entered);
create index products_2015_0712_pe_idx on products_2015_0712(pil, entered);

create index products_2016_0106_pe_idx on products_2016_0106(pil, entered);
create index products_2016_0712_pe_idx on products_2016_0712(pil, entered);

-- ________________________________________________________________
create table products_2017_0106(
  CONSTRAINT __products20170106_check
  CHECK(entered >= '2017-01-01 00:00+00'::timestamptz
        and entered < '2017-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_2017_0106_pil_idx on products_2017_0106(pil);
CREATE INDEX products_2017_0106_entered_idx on products_2017_0106(entered);
CREATE INDEX products_2017_0106_source_idx on products_2017_0106(source);
create index products_2017_0106_pe_idx on products_2017_0106(pil, entered);
grant select on products_2017_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2017_0712(
  CONSTRAINT __products20170712_check
  CHECK(entered >= '2017-07-01 00:00+00'::timestamptz
        and entered < '2018-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_2017_0712_pil_idx on products_2017_0712(pil);
CREATE INDEX products_2017_0712_entered_idx on products_2017_0712(entered);
CREATE INDEX products_2017_0712_source_idx on products_2017_0712(source);
create index products_2017_0712_pe_idx on products_2017_0712(pil, entered);
grant select on products_2017_0712 to nobody,apache;

-- ________________________________________________________________
create table products_2018_0106(
  CONSTRAINT __products20180106_check
  CHECK(entered >= '2018-01-01 00:00+00'::timestamptz
        and entered < '2018-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_2018_0106_pil_idx on products_2018_0106(pil);
CREATE INDEX products_2018_0106_entered_idx on products_2018_0106(entered);
CREATE INDEX products_2018_0106_source_idx on products_2018_0106(source);
create index products_2018_0106_pe_idx on products_2018_0106(pil, entered);
GRANT all on products_2018_0106 to mesonet,ldm;
grant select on products_2018_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2018_0712(
  CONSTRAINT __products20180712_check
  CHECK(entered >= '2018-07-01 00:00+00'::timestamptz
        and entered < '2019-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_2018_0712_pil_idx on products_2018_0712(pil);
CREATE INDEX products_2018_0712_entered_idx on products_2018_0712(entered);
CREATE INDEX products_2018_0712_source_idx on products_2018_0712(source);
create index products_2018_0712_pe_idx on products_2018_0712(pil, entered);
GRANT all on products_2018_0712 to mesonet,ldm;
grant select on products_2018_0712 to nobody,apache;

-- ________________________________________________________________
create table products_2019_0106(
  CONSTRAINT __products20190106_check
  CHECK(entered >= '2019-01-01 00:00+00'::timestamptz
        and entered < '2019-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_2019_0106_pil_idx on products_2019_0106(pil);
CREATE INDEX products_2019_0106_entered_idx on products_2019_0106(entered);
CREATE INDEX products_2019_0106_source_idx on products_2019_0106(source);
create index products_2019_0106_pe_idx on products_2019_0106(pil, entered);
GRANT all on products_2019_0106 to mesonet,ldm;
grant select on products_2019_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2019_0712(
  CONSTRAINT __products20190712_check
  CHECK(entered >= '2019-07-01 00:00+00'::timestamptz
        and entered < '2020-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_2019_0712_pil_idx on products_2019_0712(pil);
CREATE INDEX products_2019_0712_entered_idx on products_2019_0712(entered);
CREATE INDEX products_2019_0712_source_idx on products_2019_0712(source);
create index products_2019_0712_pe_idx on products_2019_0712(pil, entered);
GRANT all on products_2019_0712 to mesonet,ldm;
grant select on products_2019_0712 to nobody,apache;
