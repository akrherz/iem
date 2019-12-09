-- initial definition was not range partitioned, so we have to a convoluted
-- dance
ALTER TABLE alldata RENAME to alldata_old;

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
) PARTITION by RANGE (valid);
ALTER TABLE alldata OWNER to mesonet;
GRANT ALL on alldata to ldm;
GRANT SELECT on alldata to nobody,apache;

-- create tables as some of these do not currently exists
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
                create table IF NOT EXISTS %s() INHERITS (alldata_old)
                $f$, mytable);
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
                CREATE INDEX IF NOT EXISTS %s_valid_idx on %s(valid)
            $f$, mytable, mytable);
            execute format($f$
                CREATE INDEX IF NOT EXISTS %s_station_idx on %s(station)
            $f$, mytable, mytable);
        end loop;
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
    for year in 1994..2011
    loop
        for month in 1..12
        loop
            mytable := format($f$t%s_%s$f$,
                year, lpad(month::text, 2, '0'));
            execute format($f$
                ALTER TABLE %s NO INHERIT alldata_old
                $f$, mytable);
            execute format($f$
                ALTER TABLE alldata ATTACH PARTITION %s
                FOR VALUES FROM ('%s-%s-01 00:00+00') to ('%s-%s-01 00:00+00')
            $f$, mytable, year, month,
                case when month = 12 then year + 1 else year end,
                case when month = 12 then 1 else month + 1 end);
        end loop;
    end loop;
end;
$do$;

DROP TABLE alldata_old;
