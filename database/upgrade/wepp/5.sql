-- initial definition was not range partitioned, so we have to a convoluted
-- dance
ALTER TABLE daily_rainfall RENAME to daily_rainfall_old;

CREATE TABLE daily_rainfall(
  hrap_i smallint,
  valid date,
  rainfall real,
  peak_15min real,
  hr_cnt smallint
) PARTITION by range(valid);
ALTER TABLE daily_rainfall OWNER to mesonet;
GRANT SELECT on daily_rainfall to nobody,apache;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 1997..2019
    loop
        mytable := format($f$daily_rainfall_%s$f$, year);
        execute format($f$
            ALTER TABLE %s NO INHERIT daily_rainfall_old
            $f$, mytable);
        execute format($f$
            ALTER TABLE daily_rainfall ATTACH PARTITION %s
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
        mytable := format($f$daily_rainfall_%s$f$,
            year);
        execute format($f$
            create table %s partition of daily_rainfall
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
            $f$, mytable,
            year, year +1);
        execute format($f$
            ALTER TABLE %s OWNER to mesonet
        $f$, mytable);
        execute format($f$
            GRANT ALL on %s to ldm
        $f$, mytable);
        execute format($f$
            GRANT SELECT on %s to nobody,apache
        $f$, mytable);
        execute format($f$
            CREATE INDEX %s_valid_idx on %s(valid)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_hrap_i_idx on %s(hrap_i)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

DROP TABLE daily_rainfall_old;

-- ------------------------------

ALTER TABLE monthly_rainfall RENAME to monthly_rainfall_old;

CREATE TABLE monthly_rainfall(
  hrap_i smallint,
  valid date,
  rainfall real,
  peak_15min real,
  hr_cnt smallint
) PARTITION by range(valid);
ALTER TABLE monthly_rainfall OWNER to mesonet;
GRANT SELECT on monthly_rainfall to nobody,apache;


do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 1997..2019
    loop
        mytable := format($f$monthly_rainfall_%s$f$, year);
        execute format($f$
            ALTER TABLE %s NO INHERIT monthly_rainfall_old
            $f$, mytable);
        execute format($f$
            ALTER TABLE monthly_rainfall ATTACH PARTITION %s
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
        mytable := format($f$monthly_rainfall_%s$f$,
            year);
        execute format($f$
            create table %s partition of monthly_rainfall
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
            $f$, mytable,
            year, year +1);
        execute format($f$
            ALTER TABLE %s OWNER to mesonet
        $f$, mytable);
        execute format($f$
            GRANT ALL on %s to ldm
        $f$, mytable);
        execute format($f$
            GRANT SELECT on %s to nobody,apache
        $f$, mytable);
        execute format($f$
            CREATE INDEX %s_valid_idx on %s(valid)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

DROP TABLE monthly_rainfall_old;
