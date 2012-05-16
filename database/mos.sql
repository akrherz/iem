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

CREATE TABLE t2011() inherits (alldata);
GRANT SELECT on t2011 to nobody,apache;