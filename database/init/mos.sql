-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (5, now());

CREATE TABLE model_gridpoint (
    station character varying(4),
    model character varying(12),
    runtime timestamp with time zone,
    ftime timestamp with time zone,
    sbcape real,
    sbcin real,
    pwater real,
    precipcon real,
    precip real
);

create table model_gridpoint_2004( 
  CONSTRAINT __model_gridpoint_2004_check 
  CHECK(runtime >= '2004-01-01 00:00+00'::timestamptz 
        and runtime < '2005-01-01 00:00+00')) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2004_idx 
	on model_gridpoint_2004(station, model, runtime);
GRANT SELECT on model_gridpoint_2004 to nobody,apache;
    

create table model_gridpoint_2005( 
  CONSTRAINT __model_gridpoint_2005_check 
  CHECK(runtime >= '2005-01-01 00:00+00'::timestamptz 
        and runtime < '2006-01-01 00:00+00')) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2005_idx 
	on model_gridpoint_2005(station, model, runtime);
GRANT SELECT on model_gridpoint_2005 to nobody,apache;
    

create table model_gridpoint_2006( 
  CONSTRAINT __model_gridpoint_2006_check 
  CHECK(runtime >= '2006-01-01 00:00+00'::timestamptz 
        and runtime < '2007-01-01 00:00+00')) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2006_idx 
	on model_gridpoint_2006(station, model, runtime);
GRANT SELECT on model_gridpoint_2006 to nobody,apache;
    

create table model_gridpoint_2007( 
  CONSTRAINT __model_gridpoint_2007_check 
  CHECK(runtime >= '2007-01-01 00:00+00'::timestamptz 
        and runtime < '2008-01-01 00:00+00')) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2007_idx 
	on model_gridpoint_2007(station, model, runtime);
GRANT SELECT on model_gridpoint_2007 to nobody,apache;
    

create table model_gridpoint_2008( 
  CONSTRAINT __model_gridpoint_2008_check 
  CHECK(runtime >= '2008-01-01 00:00+00'::timestamptz 
        and runtime < '2009-01-01 00:00+00')) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2008_idx 
	on model_gridpoint_2008(station, model, runtime);
GRANT SELECT on model_gridpoint_2008 to nobody,apache;
    

create table model_gridpoint_2009( 
  CONSTRAINT __model_gridpoint_2009_check 
  CHECK(runtime >= '2009-01-01 00:00+00'::timestamptz 
        and runtime < '2010-01-01 00:00+00')) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2009_idx 
	on model_gridpoint_2009(station, model, runtime);
GRANT SELECT on model_gridpoint_2009 to nobody,apache;
    

create table model_gridpoint_2010( 
  CONSTRAINT __model_gridpoint_2010_check 
  CHECK(runtime >= '2010-01-01 00:00+00'::timestamptz 
        and runtime < '2011-01-01 00:00+00')) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2010_idx 
	on model_gridpoint_2010(station, model, runtime);
GRANT SELECT on model_gridpoint_2010 to nobody,apache;
    

create table model_gridpoint_2011( 
  CONSTRAINT __model_gridpoint_2011_check 
  CHECK(runtime >= '2011-01-01 00:00+00'::timestamptz 
        and runtime < '2012-01-01 00:00+00')) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2011_idx 
	on model_gridpoint_2011(station, model, runtime);
GRANT SELECT on model_gridpoint_2011 to nobody,apache;
    

create table model_gridpoint_2012( 
  CONSTRAINT __model_gridpoint_2012_check 
  CHECK(runtime >= '2012-01-01 00:00+00'::timestamptz 
        and runtime < '2013-01-01 00:00+00')) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2012_idx 
	on model_gridpoint_2012(station, model, runtime);
GRANT SELECT on model_gridpoint_2012 to nobody,apache;
    

create table model_gridpoint_2013( 
  CONSTRAINT __model_gridpoint_2013_check 
  CHECK(runtime >= '2013-01-01 00:00+00'::timestamptz 
        and runtime < '2014-01-01 00:00+00')) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2013_idx 
	on model_gridpoint_2013(station, model, runtime);
GRANT SELECT on model_gridpoint_2013 to nobody,apache;


create table model_gridpoint_2014( 
  CONSTRAINT __model_gridpoint_2014_check 
  CHECK(runtime >= '2014-01-01 00:00+00'::timestamptz 
        and runtime < '2015-01-01 00:00+00')) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2014_idx 
	on model_gridpoint_2014(station, model, runtime);
GRANT SELECT on model_gridpoint_2014 to nobody,apache;


CREATE TABLE alldata(
 station character(4)           ,
 model character varying(12)  ,
 runtime timestamp with time zone ,
 ftime  timestamp with time zone ,
 n_x   smallint           ,
 tmp    smallint             ,
 dpt     smallint               ,
 cld    character(2)         ,
 wdr    smallint             ,
 wsp   smallint          ,
 p06   smallint             ,
 p12    smallint             ,
 q06   smallint              ,
 q12   smallint       ,
 t06_1   smallint         ,
 t06_2   smallint        ,
 t12_1   smallint         ,
 t12_2   smallint     ,
 snw    smallint         ,
 cig    smallint      ,
 vis   smallint          ,
 obv  character(2)  ,
 poz    smallint           ,
 pos    smallint        ,
 typ    character(2),
  sky smallint,
  gst smallint,
  t03 smallint,
  pzr smallint,
  psn smallint,
  ppl smallint,
  pra smallint,
  s06 smallint,
  slv smallint,
  i06 smallint,
  lcb smallint,
  swh smallint
);
GRANT SELECT on alldata to nobody,apache;

create table t2000( 
  CONSTRAINT __t2000_check 
  CHECK(runtime >= '2000-01-01 00:00+00'::timestamptz 
        and runtime < '2001-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_idx on t2000(station, model, runtime);
CREATE INDEX t2000_runtime_idx on t2000(runtime);
GRANT SELECT on t2000 to nobody,apache;
    

create table t2001( 
  CONSTRAINT __t2001_check 
  CHECK(runtime >= '2001-01-01 00:00+00'::timestamptz 
        and runtime < '2002-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_idx on t2001(station, model, runtime);
CREATE INDEX t2001_runtime_idx on t2001(runtime);
GRANT SELECT on t2001 to nobody,apache;
    

create table t2002( 
  CONSTRAINT __t2002_check 
  CHECK(runtime >= '2002-01-01 00:00+00'::timestamptz 
        and runtime < '2003-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_idx on t2002(station, model, runtime);
CREATE INDEX t2002_runtime_idx on t2002(runtime);
GRANT SELECT on t2002 to nobody,apache;
    

create table t2003( 
  CONSTRAINT __t2003_check 
  CHECK(runtime >= '2003-01-01 00:00+00'::timestamptz 
        and runtime < '2004-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_idx on t2003(station, model, runtime);
CREATE INDEX t2003_runtime_idx on t2003(runtime);
GRANT SELECT on t2003 to nobody,apache;
    

create table t2004( 
  CONSTRAINT __t2004_check 
  CHECK(runtime >= '2004-01-01 00:00+00'::timestamptz 
        and runtime < '2005-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_idx on t2004(station, model, runtime);
CREATE INDEX t2004_runtime_idx on t2004(runtime);
GRANT SELECT on t2004 to nobody,apache;
    

create table t2005( 
  CONSTRAINT __t2005_check 
  CHECK(runtime >= '2005-01-01 00:00+00'::timestamptz 
        and runtime < '2006-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_idx on t2005(station, model, runtime);
CREATE INDEX t2005_runtime_idx on t2005(runtime);
GRANT SELECT on t2005 to nobody,apache;
    

create table t2006( 
  CONSTRAINT __t2006_check 
  CHECK(runtime >= '2006-01-01 00:00+00'::timestamptz 
        and runtime < '2007-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_idx on t2006(station, model, runtime);
CREATE INDEX t2006_runtime_idx on t2006(runtime);
GRANT SELECT on t2006 to nobody,apache;
    

create table t2007( 
  CONSTRAINT __t2007_check 
  CHECK(runtime >= '2007-01-01 00:00+00'::timestamptz 
        and runtime < '2008-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_idx on t2007(station, model, runtime);
CREATE INDEX t2007_runtime_idx on t2007(runtime);
GRANT SELECT on t2007 to nobody,apache;
    

create table t2008( 
  CONSTRAINT __t2008_check 
  CHECK(runtime >= '2008-01-01 00:00+00'::timestamptz 
        and runtime < '2009-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_idx on t2008(station, model, runtime);
CREATE INDEX t2008_runtime_idx on t2008(runtime);
GRANT SELECT on t2008 to nobody,apache;
    

create table t2009( 
  CONSTRAINT __t2009_check 
  CHECK(runtime >= '2009-01-01 00:00+00'::timestamptz 
        and runtime < '2010-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_idx on t2009(station, model, runtime);
CREATE INDEX t2009_runtime_idx on t2009(runtime);
GRANT SELECT on t2009 to nobody,apache;
    

create table t2010( 
  CONSTRAINT __t2010_check 
  CHECK(runtime >= '2010-01-01 00:00+00'::timestamptz 
        and runtime < '2011-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_idx on t2010(station, model, runtime);
CREATE INDEX t2010_runtime_idx on t2010(runtime);
GRANT SELECT on t2010 to nobody,apache;
    

create table t2011( 
  CONSTRAINT __t2011_check 
  CHECK(runtime >= '2011-01-01 00:00+00'::timestamptz 
        and runtime < '2012-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_idx on t2011(station, model, runtime);
CREATE INDEX t2011_runtime_idx on t2011(runtime);
GRANT SELECT on t2011 to nobody,apache;
    

create table t2012( 
  CONSTRAINT __t2012_check 
  CHECK(runtime >= '2012-01-01 00:00+00'::timestamptz 
        and runtime < '2013-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_idx on t2012(station, model, runtime);
CREATE INDEX t2012_runtime_idx on t2012(runtime);
GRANT SELECT on t2012 to nobody,apache;
    

create table t2013( 
  CONSTRAINT __t2013_check 
  CHECK(runtime >= '2013-01-01 00:00+00'::timestamptz 
        and runtime < '2014-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_idx on t2013(station, model, runtime);
CREATE INDEX t2013_runtime_idx on t2013(runtime);
GRANT SELECT on t2013 to nobody,apache;


create table t2014( 
  CONSTRAINT __t2014_check 
  CHECK(runtime >= '2014-01-01 00:00+00'::timestamptz 
        and runtime < '2015-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_idx on t2014(station, model, runtime);
CREATE INDEX t2014_runtime_idx on t2014(runtime);
GRANT SELECT on t2014 to nobody,apache;

create table model_gridpoint_2015(
  CONSTRAINT __model_gridpoint_2015_check
  CHECK(runtime >= '2015-01-01 00:00+00'::timestamptz
        and runtime < '2016-01-01 00:00+00'))
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2015_idx
        on model_gridpoint_2015(station, model, runtime);
GRANT SELECT on model_gridpoint_2015 to nobody,apache;

create table t2015(
  CONSTRAINT __t2015_check
  CHECK(runtime >= '2015-01-01 00:00+00'::timestamptz
        and runtime < '2016-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t2015_idx on t2015(station, model, runtime);
CREATE INDEX t2015_runtime_idx on t2015(runtime);
GRANT SELECT on t2015 to nobody,apache;

create table model_gridpoint_2016(
  CONSTRAINT __model_gridpoint_2016_check
  CHECK(runtime >= '2016-01-01 00:00+00'::timestamptz
        and runtime < '2017-01-01 00:00+00'))
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2016_idx
        on model_gridpoint_2016(station, model, runtime);
GRANT SELECT on model_gridpoint_2016 to nobody,apache;

create table t2016(
  CONSTRAINT __t2016_check
  CHECK(runtime >= '2016-01-01 00:00+00'::timestamptz
        and runtime < '2017-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t2016_idx on t2016(station, model, runtime);
CREATE INDEX t2016_runtime_idx on t2016(runtime);
GRANT SELECT on t2016 to nobody,apache;

create table model_gridpoint_2017(
  CONSTRAINT __model_gridpoint_2017_check
  CHECK(runtime >= '2017-01-01 00:00+00'::timestamptz
        and runtime < '2018-01-01 00:00+00'::timestamptz))
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2017_idx
        on model_gridpoint_2017(station, model, runtime);
GRANT SELECT on model_gridpoint_2017 to nobody,apache;

create table t2017(
  CONSTRAINT __t2017_check
  CHECK(runtime >= '2017-01-01 00:00+00'::timestamptz
        and runtime < '2018-01-01 00:00+00'::timestamptz))
  INHERITS (alldata);
CREATE INDEX t2017_idx on t2017(station, model, runtime);
CREATE INDEX t2017_runtime_idx on t2017(runtime);
GRANT SELECT on t2017 to nobody,apache;

create table model_gridpoint_2018(
  CONSTRAINT __model_gridpoint_2018_check
  CHECK(runtime >= '2018-01-01 00:00+00'::timestamptz
        and runtime < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2018_idx
        on model_gridpoint_2018(station, model, runtime);
GRANT SELECT on model_gridpoint_2018 to nobody,apache;

create table t2018(
  CONSTRAINT __t2018_check
  CHECK(runtime >= '2018-01-01 00:00+00'::timestamptz
        and runtime < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (alldata);
CREATE INDEX t2018_idx on t2018(station, model, runtime);
CREATE INDEX t2018_runtime_idx on t2018(runtime);
GRANT SELECT on t2018 to nobody,apache;

create table model_gridpoint_2019(
  CONSTRAINT __model_gridpoint_2019_check
  CHECK(runtime >= '2019-01-01 00:00+00'::timestamptz
        and runtime < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2019_idx
        on model_gridpoint_2019(station, model, runtime);
GRANT SELECT on model_gridpoint_2019 to nobody,apache;

create table t2019(
  CONSTRAINT __t2019_check
  CHECK(runtime >= '2019-01-01 00:00+00'::timestamptz
        and runtime < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (alldata);
CREATE INDEX t2019_idx on t2019(station, model, runtime);
CREATE INDEX t2019_runtime_idx on t2019(runtime);
GRANT SELECT on t2019 to nobody,apache;
