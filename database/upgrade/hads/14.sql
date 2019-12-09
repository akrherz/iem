-- initial definition was not range partitioned, so we have to a convoluted
-- dance
ALTER TABLE alldata RENAME to alldata_old;

CREATE TABLE alldata(
	station varchar(8),
	valid timestamptz,
	tmpf real,
	dwpf real,
	sknt real,
	drct real)
    PARTITION by range(valid);
ALTER TABLE alldata OWNER to mesonet;
GRANT ALL on alldata to ldm;
GRANT SELECT on alldata to nobody,apache;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2002..2019
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
            CREATE INDEX %s_idx on %s(station, valid)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_valid_idx on %s(valid)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

DROP TABLE alldata_old;

