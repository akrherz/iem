-- initial definition was not range partitioned, so we have to a convoluted
-- dance
ALTER TABLE alldata RENAME to alldata_old;
ALTER TABLE alldata_traffic RENAME to alldata_traffic_old;
ALTER TABLE alldata_soil RENAME to alldata_soil_old;

CREATE TABLE alldata(
  station varchar(6),
  valid timestamptz,
  tmpf real,
  dwpf real,
  drct smallint,
  sknt real,
  tfs0 real,
  tfs1 real,
  tfs2 real,
  tfs3 real,
  subf real,
  gust real,
  tfs0_text varchar(20),
  tfs1_text varchar(20),
  tfs2_text varchar(20),
  tfs3_text varchar(20),
  pcpn real,
  vsby real
) PARTITION by range(valid);
ALTER TABLE alldata OWNER to mesonet;
GRANT ALL on alldata to ldm;
GRANT SELECT on alldata to nobody,apache;

CREATE TABLE alldata_traffic(
  station char(5),
  valid timestamp with time zone,
  lane_id smallint,
  avg_speed real,
  avg_headway real,
  normal_vol real,
  long_vol real,
  occupancy real
) PARTITION by range(valid);
ALTER TABLE alldata_traffic OWNER to mesonet;
GRANT ALL on alldata_traffic to ldm;
GRANT select on alldata_traffic to nobody,apache;


CREATE TABLE alldata_soil(
  station char(5),
  valid timestamp with time zone,
  s0temp real,
  s1temp real,
  s2temp real,
  s3temp real,
  s4temp real,
  s5temp real,
  s6temp real,
  s7temp real,
  s8temp real,
  s9temp real,
  s10temp real,
  s11temp real,
  s12temp real,
  s13temp real,
  s14temp real
) PARTITION by range(valid);
ALTER TABLE alldata_soil OWNER to mesonet;
GRANT ALL on alldata_soil to ldm;
GRANT select on alldata_soil to nobody,apache;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 1994..2019
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
            CREATE INDEX %s_station_idx on %s(station)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_valid_idx on %s(valid)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

DROP TABLE alldata_old;

-- -----------------------------

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2008..2019
    loop
        mytable := format($f$t%s_traffic$f$, year);
        execute format($f$
            ALTER TABLE %s NO INHERIT alldata_traffic_old
            $f$, mytable);
        execute format($f$
            ALTER TABLE alldata_traffic ATTACH PARTITION %s
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
        mytable := format($f$t%s_traffic$f$, year);
        execute format($f$
            create table %s partition of alldata_traffic
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
            CREATE INDEX %s_station_idx on %s(station)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_valid_idx on %s(valid)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

DROP TABLE alldata_traffic_old;

-- ----------------------------------

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2008..2019
    loop
        mytable := format($f$t%s_soil$f$, year);
        execute format($f$
            ALTER TABLE %s NO INHERIT alldata_soil_old
            $f$, mytable);
        execute format($f$
            ALTER TABLE alldata_soil ATTACH PARTITION %s
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
        mytable := format($f$t%s_soil$f$, year);
        execute format($f$
            create table %s partition of alldata_soil
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
            CREATE INDEX %s_station_idx on %s(station)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_valid_idx on %s(valid)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

DROP TABLE alldata_soil_old;
