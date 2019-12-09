-- initial definition was not range partitioned, so we have to a convoluted
-- dance
ALTER TABLE alldata RENAME to alldata_old;

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
  swh smallint)
    PARTITION by range(runtime);
ALTER TABLE alldata OWNER to mesonet;
GRANT ALL on alldata to ldm;
GRANT SELECT on alldata to nobody,apache;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2000..2019
    loop
        mytable := format($f$t%s$f$, year);
        execute format($f$
            ALTER TABLE %s NO INHERIT alldata_old
            $f$, mytable);
        execute format($f$
            ALTER TABLE alldata ATTACH PARTITION %s
            FOR VALUES FROM ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
        $f$, mytable, year, year + 1);
    end loop;
end;
$do$;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2020..2030
    loop
        mytable := format($f$t%s$f$, year);
        execute format($f$
            create table %s partition of alldata
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
            $f$, mytable, year, year + 1);
        execute format($f$
            ALTER TABLE %s OWNER to mesonet
        $f$, mytable);
        execute format($f$
            GRANT ALL on %s to ldm
        $f$, mytable);
        execute format($f$
            GRANT SELECT on %s to nobody,apache
        $f$, mytable);
        -- Indices
        execute format($f$
            CREATE INDEX %s_idx on %s(station, model, runtime)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_runtime_idx on %s(runtime)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

DROP TABLE alldata_old;

-- ----------------------------

ALTER TABLE model_gridpoint RENAME to model_gridpoint_old;

CREATE TABLE model_gridpoint(
    station character varying(4),
    model character varying(12),
    runtime timestamp with time zone,
    ftime timestamp with time zone,
    sbcape real,
    sbcin real,
    pwater real,
    precipcon real,
    precip real)
    PARTITION by range(runtime);
ALTER TABLE alldata OWNER to mesonet;
GRANT ALL on alldata to ldm;
GRANT SELECT on alldata to nobody,apache;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2004..2019
    loop
        mytable := format($f$model_gridpoint_%s$f$, year);
        execute format($f$
            ALTER TABLE %s NO INHERIT model_gridpoint_old
            $f$, mytable);
        execute format($f$
            ALTER TABLE model_gridpoint ATTACH PARTITION %s
            FOR VALUES FROM ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
        $f$, mytable, year, year + 1);
    end loop;
end;
$do$;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2020..2030
    loop
        mytable := format($f$model_gridpoint_%s$f$, year);
        execute format($f$
            create table %s partition of model_gridpoint
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
            $f$, mytable, year, year + 1);
        execute format($f$
            ALTER TABLE %s OWNER to mesonet
        $f$, mytable);
        execute format($f$
            GRANT ALL on %s to ldm
        $f$, mytable);
        execute format($f$
            GRANT SELECT on %s to nobody,apache
        $f$, mytable);
        -- Indices
        execute format($f$
            CREATE INDEX %s_idx on %s(station, model, runtime)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

DROP TABLE model_gridpoint_old;
