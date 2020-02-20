-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (6, now());

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
) PARTITION by range(runtime);
ALTER TABLE model_gridpoint OWNER to mesonet;
GRANT ALL on model_gridpoint to ldm;
GRANT SELECT on model_gridpoint to nobody,apache;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2004..2030
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

CREATE TABLE alldata(
  station text,
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
  swh smallint,
  dur smallint,
  mht smallint,
  twd smallint,
  tws smallint,
  hid smallint,
  sol smallint
) PARTITION by range(runtime);
ALTER TABLE alldata OWNER to mesonet;
GRANT ALL on alldata to ldm;
GRANT SELECT on alldata to nobody,apache;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2000..2030
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
