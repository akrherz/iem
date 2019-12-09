do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2020..2030
    loop
        mytable := format($f$warnings_%s$f$, year);
        execute format($f$
            create table %s() INHERITS (warnings)
            $f$, mytable);
        execute format($f$
            alter table %s ADD CONSTRAINT %s_gid_fkey
            FOREIGN KEY(gid) REFERENCES ugcs(gid)
        $f$, mytable, mytable);
        execute format($f$
            alter table %s ALTER WFO SET NOT NULL;
            alter table %s ALTER eventid SET NOT NULL;
            alter table %s ALTER status SET NOT NULL;
            alter table %s ALTER ugc SET NOT NULL;
            alter table %s ALTER phenomena SET NOT NULL;
            alter table %s ALTER significance SET NOT NULL;
        $f$, mytable, mytable, mytable, mytable, mytable, mytable);
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
            CREATE INDEX %s_combo_idx
            on %s(wfo, phenomena, eventid, significance)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_expire_idx
            on %s(expire)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_issue_idx
            on %s(issue)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_ugc_idx
            on %s(ugc)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_wfo_idx
            on %s(wfo)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_gid_idx
            on %s(gid)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

-- -----------------------------------

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2020..2030
    loop
        mytable := format($f$sbw_%s$f$, year);
        execute format($f$
            create table %s() INHERITS (sbw)
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
            CREATE INDEX %s_idx on %s(wfo, eventid, significance, phenomena)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_expire_idx on %s(expire)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_issue_idx on %s(issue)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_wfo_idx on %s(wfo)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_gix ON %s USING GIST (geom)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

-- -----------------------------------

ALTER TABLE lsrs RENAME to lsrs_old;

CREATE TABLE lsrs (
    valid timestamp with time zone,
    type character(1),
    magnitude real,
    city character varying(32),
    county character varying(32),
    state character(2),
    source character varying(32),
    remark text,
    wfo character(3),
    typetext character varying(40),
    geom geometry(Point, 4326)
) PARTITION by range(valid);
ALTER TABLE lsrs OWNER to mesonet;
GRANT ALL on lsrs to ldm;
grant select on lsrs to apache,nobody;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 1986..2019
    loop
        mytable := format($f$lsrs_%s$f$, year);
        execute format($f$
            ALTER TABLE %s NO INHERIT lsrs_old
            $f$, mytable);
        execute format($f$
            ALTER TABLE lsrs ATTACH PARTITION %s
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
        mytable := format($f$lsrs_%s$f$, year);
        execute format($f$
            create table %s partition of lsrs
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
            CREATE INDEX %s_valid_idx on %s(valid)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_wfo_idx on %s(wfo)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

DROP TABLE lsrs_old;

-- --------------------------

ALTER TABLE ffg RENAME to ffg_old;

CREATE TABLE ffg(
  ugc char(6),
  valid timestamptz,
  hour01 real,
  hour03 real,
  hour06 real,
  hour12 real,
  hour24 real)
  PARTITION by range(valid);
ALTER TABLE ffg OWNER to mesonet;
GRANT SELECT on ffg to nobody,apache;
GRANT ALL on ffg to ldm;


do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2000..2019
    loop
        mytable := format($f$ffg_%s$f$, year);
        execute format($f$
            ALTER TABLE %s NO INHERIT ffg_old
            $f$, mytable);
        execute format($f$
            ALTER TABLE ffg ATTACH PARTITION %s
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
        mytable := format($f$ffg_%s$f$, year);
        execute format($f$
            create table %s partition of ffg
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
            CREATE INDEX %s_ugc_idx on %s(ugc)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_valid_idx on %s(valid)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

DROP TABLE ffg_old;
