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

create table model_gridpoint_2014( 
  CONSTRAINT __model_gridpoint_2014_check 
  CHECK(runtime >= '2014-01-01 00:00+00'::timestamptz 
        and runtime < '2015-01-01 00:00+00')) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2014_idx 
	on model_gridpoint_2014(station, model, runtime);
GRANT SELECT on model_gridpoint_2014 to nobody,apache;

---
--- Not sure why, just something to hold a curiousity of large MOS differences
---
CREATE TABLE large_difference(
  model varchar(5),
  valid timestamp with time zone,
  station varchar(5),
  ob real,
  mos real);
GRANT SELECT on large_difference to nobody,apache;

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
 typ    character(2)      
);
GRANT SELECT on alldata to nobody,apache;


create table t2014( 
  CONSTRAINT __t2014_check 
  CHECK(runtime >= '2014-01-01 00:00+00'::timestamptz 
        and runtime < '2015-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_idx on t2014(station, model, runtime);
CREATE INDEX t2014_runtime_idx on t2014(runtime);
GRANT SELECT on t2014 to nobody,apache;
