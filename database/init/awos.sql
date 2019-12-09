
-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (0, now());

---
--- Main table that all children inherit from
---
CREATE TABLE alldata(
	station varchar(5),
	valid timestamptz,
	tmpf smallint,
	dwpf smallint,
	sknt smallint,
	drct smallint,
	gust smallint,
	p01i real,
	cl1 smallint,
	ca1 smallint,
	cl2 smallint,
	ca2 smallint,
	cl3 smallint,
	ca3 smallint,
	vsby real,
	alti real,
	qc varchar(5)
) PARTITION by range(valid);
ALTER TABLE alldata OWNER to mesonet;
GRANT ALL on alldata to ldm;
GRANT SELECT on alldata to nobody,apache;

do
$do$
declare
     year int;
     month int;
     mytable varchar;
begin
    for year in 1994..2011
    loop
        for month in 1..12
        loop
            mytable := format($f$t%s_%s$f$,
                year, lpad(month::text, 2, '0'));
            execute format($f$
                create table %s partition of alldata
                for values from ('%s-%s-01 00:00+00') to ('%s-%s-01 00:00+00')
                $f$, mytable,
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
            -- Indices
            execute format($f$
                CREATE INDEX %s_valid_idx on %s(valid)
            $f$, mytable, mytable);
            execute format($f$
                CREATE INDEX %s_station_idx on %s(station)
            $f$, mytable, mytable);
        end loop;
    end loop;
end;
$do$;
