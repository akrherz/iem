CREATE EXTENSION postgis;

-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (-1, now());

---
--- NEXRAD Attributes
---
CREATE TABLE nexrad_attributes(
    nexrad character(3),   
    storm_id character(2),     
    azimuth smallint,
    range smallint,
    tvs character varying(10),
    meso character varying(10),
    posh smallint,
    poh smallint,
    max_size real,
    vil smallint,
    max_dbz smallint,
    max_dbz_height real,
    top real,
    drct smallint,
    sknt smallint,
    valid timestamp with time zone,
    geom geometry(Point, 4326)
 );
GRANT ALL on nexrad_attributes to ldm,mesonet;
GRANT SELECT on nexrad_attributes to apache,nobody;


CREATE TABLE nexrad_attributes_log(
    nexrad character(3),   
    storm_id character(2),     
    azimuth smallint,
    range smallint,
    tvs character varying(10),
    meso character varying(10),
    posh smallint,
    poh smallint,
    max_size real,
    vil smallint,
    max_dbz smallint,
    max_dbz_height real,
    top real,
    drct smallint,
    sknt smallint,
    valid timestamp with time zone,
    geom geometry(Point, 4326)
 ) PARTITION by RANGE (valid);
GRANT ALL on nexrad_attributes_log to ldm,mesonet;
GRANT SELECT on nexrad_attributes_log to apache,nobody;
CREATE INDEX on nexrad_attributes_log(valid);
CREATE INDEX on nexrad_attributes_log(nexrad);

do
$do$
declare
     year int;
begin
    for year in 2000..2030
    loop
        execute format($f$
            create table nexrad_attributes_%s partition of nexrad_attributes_log
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
        $f$, year, year, year + 1);
        execute format($f$
            GRANT ALL on nexrad_attributes_%s to mesonet,ldm
        $f$, year);
        execute format($f$
            GRANT SELECT on nexrad_attributes_%s to nobody,apache
        $f$, year);
    end loop;
end;
$do$;