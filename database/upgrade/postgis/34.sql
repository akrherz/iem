CREATE TABLE idot_snowplow_archive(
	label varchar(20) not null,
	valid timestamptz not null,
	heading real,
	velocity real,
	roadtemp real,
	airtemp real,
	solidmaterial varchar(256),
	liquidmaterial varchar(256),
	prewetmaterial varchar(256),
	solidsetrate real,
	liquidsetrate real,
	prewetsetrate real,
	leftwingplowstate smallint,
	rightwingplowstate smallint,
	frontplowstate smallint,
	underbellyplowstate smallint,
	solid_spread_code smallint,
	road_temp_code smallint,
    geom geometry(Point, 4326)
) PARTITION by RANGE (valid);
CREATE INDEX on idot_snowplow_archive(label);
CREATE INDEX on idot_snowplow_archive(valid);
ALTER TABLE idot_snowplow_archive OWNER to mesonet;
GRANT ALL on idot_snowplow_archive to ldm;
GRANT SELECT on idot_snowplow_archive to nobody,apache;

do
$do$
declare
     year int;
begin
    for year in 2013..2030
    loop
        execute format($f$
            create table idot_snowplow_%s partition of idot_snowplow_archive
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
        $f$, year, year, year + 1);
        execute format($f$
            GRANT ALL on idot_snowplow_%s to mesonet,ldm
        $f$, year);
        execute format($f$
            GRANT SELECT on idot_snowplow_%s to nobody,apache
        $f$, year);
    end loop;
end;
$do$;
