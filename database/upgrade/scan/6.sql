-- initial definition was not range partitioned, so we have to a convoluted
-- dance
ALTER TABLE alldata RENAME to alldata_old;

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
) PARTITION by range(valid);
ALTER TABLE alldata OWNER to mesonet;
GRANT ALL on alldata to ldm;
GRANT SELECT on alldata to nobody,apache;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 1983..2019
    loop
        mytable := format($f$t%s_hourly$f$, year);
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
        mytable := format($f$t%s_hourly$f$, year);
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
            CREATE INDEX %s_idx on %s(station, valid)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

DROP TABLE alldata_old;
