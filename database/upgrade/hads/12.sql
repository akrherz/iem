CREATE TABLE raw(
    station varchar(8),
    valid timestamptz,
    key varchar(11),
    value real
) PARTITION by range(valid);
ALTER TABLE raw OWNER to mesonet;
GRANT ALL on raw to ldm;
GRANT SELECT on raw to nobody,apache;

do
$do$
declare
     year int;
     month int;
     mytable varchar;
begin
    for year in 2002..2019
    loop
        execute format($f$
            ALTER TABLE raw%s RENAME to raw%s_old
        $f$, year, year);
        execute format($f$
            create table raw%s partition of raw
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
            PARTITION by range(valid)
            $f$, year, year, year + 1);
        execute format($f$
            ALTER TABLE raw%s OWNER to mesonet
        $f$, year);
        execute format($f$
            GRANT ALL on raw%s to ldm
        $f$, year);
        execute format($f$
            GRANT SELECT on raw%s to nobody,apache
        $f$, year);
        -- Indices
        execute format($f$
            CREATE INDEX raw%s_idx on raw%s(station, valid)
        $f$, year, year);
        execute format($f$
            CREATE INDEX raw%s_station_idx on raw%s(station)
        $f$, year, year);
        for month in 1..12
        loop
            mytable := format($f$raw%s_%s$f$,
                year, lpad(month::text, 2, '0'));
            execute format($f$
                ALTER table %s NO INHERIT raw%s_old
                $f$, mytable, year);
            execute format($f$
                ALTER TABLE raw%s ATTACH PARTITION %s
                FOR VALUES FROM ('%s-%s-01 00:00+00') to ('%s-%s-01 00:00+00')
                $f$, year, mytable,
                year, month,
                case when month = 12 then year + 1 else year end,
                case when month = 12 then 1 else month + 1 end);
        end loop;
        execute format($f$
            DROP TABLE raw%s_old
        $f$, year);
    end loop;
end;
$do$;

do
$do$
declare
     year int;
     month int;
     mytable varchar;
begin
    for year in 2020..2030
    loop
        execute format($f$
            create table raw%s partition of raw
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
            PARTITION by range(valid)
            $f$, year, year, year + 1);
        execute format($f$
            ALTER TABLE raw%s OWNER to mesonet
        $f$, year);
        execute format($f$
            GRANT ALL on raw%s to ldm
        $f$, year);
        execute format($f$
            GRANT SELECT on raw%s to nobody,apache
        $f$, year);
        -- Indices
        execute format($f$
            CREATE INDEX raw%s_idx on raw%s(station, valid)
        $f$, year, year);
        execute format($f$
            CREATE INDEX raw%s_station_idx on raw%s(station)
        $f$, year, year);
        for month in 1..12
        loop
            mytable := format($f$raw%s_%s$f$,
                year, lpad(month::text, 2, '0'));
            execute format($f$
                create table %s partition of raw%s
                for values from ('%s-%s-01 00:00+00') to ('%s-%s-01 00:00+00')
                $f$, mytable,
                year,
                year, month,
                case when month = 12 then year + 1 else year end,
                case when month = 12 then 1 else month + 1 end);
            execute format($f$
                ALTER TABLE %s OWNER to mesonet
            $f$, mytable);
            execute format($f$
                GRANT ALL on %s to ldm
            $f$, mytable);
            execute format($f$
                GRANT SELECT on %s to nobody,apache
            $f$, mytable);

        end loop;
    end loop;
end;
$do$;
