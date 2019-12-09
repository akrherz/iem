--- ugly dance here
ALTER TABLE hourly RENAME to hourly_old;

CREATE TABLE hourly(
  station varchar(20),
  network varchar(10),
  valid timestamptz,
  phour real,
  iemid int references stations(iemid)
) PARTITION by range(valid);
ALTER TABLE hourly OWNER to mesonet;
GRANT ALL on hourly to ldm;
GRANT SELECT on hourly to apache,nobody;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 1941..2019
    loop
        mytable := format($f$hourly_%s$f$, year);
        execute format($f$
            ALTER TABLE %s NO INHERIT hourly_old
            $f$, mytable);
        execute format($f$
            ALTER TABLE hourly ATTACH PARTITION %s
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
        mytable := format($f$hourly_%s$f$, year);
        execute format($f$
            create table %s partition of hourly
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
            $f$, mytable, year, year + 1);
        execute format($f$
            ALTER TABLE %s ADD foreign key(iemid)
            references stations(iemid) ON DELETE CASCADE;
        $f$, mytable);
        execute format($f$
CREATE RULE replace_%s as
    ON INSERT TO %s
   WHERE (EXISTS ( SELECT 1
           FROM %s
          WHERE %s.station::text = new.station::text
          AND %s.network::text = new.network::text
          AND %s.valid = new.valid)) DO INSTEAD
         UPDATE %s SET phour = new.phour
  WHERE %s.station::text = new.station::text AND
  %s.network::text = new.network::text AND
  %s.valid = new.valid
        $f$, mytable, mytable, mytable, mytable, mytable,
        mytable, mytable, mytable, mytable, mytable);
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
            CREATE INDEX %s_idx on %s(station, network, valid)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_valid_idx on %s(valid)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

DROP TABLE hourly_old;
