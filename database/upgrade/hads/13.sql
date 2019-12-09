-- initial definition was not range partitioned, so we have to a convoluted
-- dance
ALTER TABLE hml_observed_data RENAME to hml_observed_data_old;

CREATE TABLE hml_observed_data(
	station varchar(8),
	valid timestamptz,
	key smallint REFERENCES hml_observed_keys(id),
	value real)
    PARTITION by range(valid);
ALTER TABLE hml_observed_data OWNER to mesonet;
GRANT ALL on hml_observed_data to ldm;
GRANT SELECT on hml_observed_data to nobody,apache;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2012..2019
    loop
        mytable := format($f$hml_observed_data_%s$f$, year);
        execute format($f$
            ALTER TABLE %s NO INHERIT hml_observed_data_old
            $f$, mytable);
        execute format($f$
            ALTER TABLE hml_observed_data ATTACH PARTITION %s
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
        mytable := format($f$hml_observed_data_%s$f$, year);
        execute format($f$
            create table %s partition of hml_observed_data
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