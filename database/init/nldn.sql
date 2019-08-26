CREATE EXTENSION postgis;

-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (-1, now());

-- Storage of NLDN data, in monthly partitions!
CREATE TABLE nldn_all(
	valid timestamptz,
	geom geometry(Point, 4326),
	signal real,
	multiplicity smallint,
	axis smallint,
	eccentricity smallint,
	ellipse smallint,
	chisqr smallint) PARTITION by RANGE (valid);
GRANT ALL on nldn_all to mesonet,ldm;
GRANT SELECT on nldn_all to apache,nobody;
CREATE INDEX on nldn_all(valid);

do
$do$
declare
     year int;
begin
    for year in 2016..2030
    loop
        for month in 1..12
        loop
            execute format($f$
                create table nldn%s_%s partition of nldn_all
                for values from ('%s-%s-01 00:00+00') to ('%s-%s-01 00:00+00')
            $f$, year, lpad(month::text, 2, '0'), year, month,
            case when month = 12 then year + 1 else year end,
            case when month = 12 then 1 else month + 1 end);
            execute format($f$
                GRANT ALL on nldn%s_%s to mesonet,ldm
            $f$, year, lpad(month::text, 2, '0'));
            execute format($f$
                GRANT SELECT on nldn%s_%s to nobody,apache
            $f$, year, lpad(month::text, 2, '0'));
        end loop;
    end loop;
end;
$do$;
