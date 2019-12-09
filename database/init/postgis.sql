CREATE EXTENSION postgis;

-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (37, now());

---
--- TABLES THAT ARE LOADED VIA shp2pgsql
---   + cities
---   + climate_div
---   + counties
---   + iacounties
---   + iowatorn
---   + placepoly
---   + tz
---   + uscounties
---   + warnings_import

--- states table is loaded by some shp2pgsql load that has unknown origins :(
CREATE TABLE states(
  gid int,
  state_name varchar,
  state_fips varchar,
  state_abbr varchar,
  the_geom geometry(MultiPolygon, 4326),
  simple_geom geometry(MultiPolygon, 4326)
);
GRANT ALL on states to mesonet,ldm;
GRANT SELECT on states to nobody,apache;

---
--- cwsu table, manually got this at some point :/
---  pg_dump -t cwsu -h localhost -p 5555 postgis | psql postgis

---
--- Quasi synced from mesosite database
---
CREATE TABLE stations(
	id varchar(20),
	synop int,
	name varchar(64),
	state char(2),
	country char(2),
	elevation real,
	network varchar(20),
	online boolean,
	params varchar(300),
	county varchar(50),
	plot_name varchar(64),
	climate_site varchar(6),
	remote_id int,
	nwn_id int,
	spri smallint,
	wfo varchar(3),
	archive_begin timestamptz,
	archive_end timestamp with time zone,
	modified timestamp with time zone,
	tzname varchar(32),
	iemid SERIAL,
	metasite boolean,
	sigstage_low real,
	sigstage_action real,
	sigstage_bankfull real,
	sigstage_flood real,
	sigstage_moderate real,
	sigstage_major real,
	sigstage_record real,
	ugc_county char(6),
	ugc_zone char(6),
	ncdc81 varchar(11),
	temp24_hour smallint,
	precip24_hour smallint
);
CREATE UNIQUE index stations_idx on stations(id, network);
create UNIQUE index stations_iemid_idx on stations(iemid);
SELECT AddGeometryColumn('stations', 'geom', 4326, 'POINT', 2);
GRANT SELECT on stations to apache,nobody;
grant all on stations_iemid_seq to nobody,apache;
GRANT ALL on stations to mesonet,ldm;
GRANT ALL on stations_iemid_seq to mesonet,ldm;


---
--- road conditions archive
---
CREATE TABLE roads_2003_2004_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint
);
GRANT SELECT on roads_2003_2004_log to nobody,apache;

CREATE TABLE roads_2004_2005_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint
);
GRANT SELECT on roads_2004_2005_log to nobody,apache;

CREATE TABLE roads_2005_2006_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint
);
GRANT SELECT on roads_2005_2006_log to nobody,apache;

CREATE TABLE roads_2006_2007_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint,
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar
);
GRANT SELECT on roads_2006_2007_log to nobody,apache;

CREATE TABLE roads_2007_2008_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint,
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar
);
GRANT SELECT on roads_2007_2008_log to nobody,apache;

CREATE TABLE roads_2008_2009_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint,
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar
);
GRANT SELECT on roads_2008_2009_log to nobody,apache;

CREATE TABLE roads_2009_2010_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint,
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar
);
GRANT SELECT on roads_2009_2010_log to nobody,apache;

CREATE TABLE roads_2010_2011_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint,
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar
);
GRANT SELECT on roads_2010_2011_log to nobody,apache;



CREATE TABLE roads_2013_2014_log(
  segid int,
  valid timestamptz,
  cond_code smallint,
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar);
GRANT SELECT on roads_2013_2014_log to nobody,apache;

---
--- Cruft from the old days
---
CREATE TABLE iemchat_room_participation(
  room varchar(100),
  valid timestamptz,
  users smallint
);

---
--- Bot Warnings
---
CREATE TABLE bot_warnings(
  issue timestamptz,
  expire timestamptz,
  report text,
  type char(3),
  gtype char(1),
  wfo char(3),
  eventid smallint,
  status char(3),
  fips int,
  updated timestamptz,
  fcster varchar(24),
  svs text,
  ugc varchar(6),
  phenomena char(2),
  significance char(1),
  hvtec_nwsli varchar(5),
  hailtag int,
  windtag int
);
SELECT AddGeometryColumn('bot_warnings', 'geom', 4326, 'MULTIPOLYGON', 2);
GRANT SELECT on bot_warnings to nobody,apache;

CREATE TABLE robins(
  id SERIAL,
  name varchar,
  city varchar,
  day date);
SELECT AddGeometryColumn('robins', 'the_geom', 4326, 'POINT', 2);

---
--- NWS Forecast / WWA Zones / Boundaries
---
CREATE TABLE ugcs(
	gid SERIAL UNIQUE NOT NULL,
	ugc char(6) NOT NULL,
	name varchar(256),
	state char(2),
	tzname varchar(32),
	wfo varchar(9),
	begin_ts timestamptz NOT NULL,
	end_ts timestamptz,
	area2163 real
);
SELECT AddGeometryColumn('ugcs', 'geom', 4326, 'MULTIPOLYGON', 2);
SELECT AddGeometryColumn('ugcs', 'simple_geom', 4326, 'MULTIPOLYGON', 2);
SELECT AddGeometryColumn('ugcs', 'centroid', 4326, 'POINT', 2);
GRANT SELECT on ugcs to nobody,apache;
CREATE INDEX ugcs_ugc_idx on ugcs(ugc);
create index ugcs_gix on ugcs USING GIST(geom);

---
--- Helper function to find a GID for a given UGC code and date!
---
CREATE OR REPLACE FUNCTION get_gid(varchar, timestamptz)
RETURNS int
LANGUAGE sql
AS $_$
  select gid from ugcs WHERE ugc = $1 and begin_ts <= $2 and
  (end_ts is null or end_ts > $2) LIMIT 1
$_$;


---
--- Store IDOT dashcam stuff
---
CREATE TABLE idot_dashcam_current(
	label varchar(20) UNIQUE not null,
	valid timestamptz,
	idnum int
);
SELECT AddGeometryColumn('idot_dashcam_current', 'geom', 4326, 'POINT', 2);
GRANT SELECT on idot_dashcam_current to nobody,apache;

CREATE TABLE idot_dashcam_log(
	label varchar(20) not null,
	valid timestamptz,
	idnum int
);
SELECT AddGeometryColumn('idot_dashcam_log', 'geom', 4326, 'POINT', 2);
CREATE INDEX idot_dashcam_log_valid_idx on idot_dashcam_log(valid);
CREATE INDEX idot_dashcam_log_label_idx on idot_dashcam_log(label);
GRANT SELECT on idot_dashcam_current to nobody,apache;

CREATE OR REPLACE FUNCTION idot_dashcam_insert_before_F()
RETURNS TRIGGER
 AS $BODY$
DECLARE
    result INTEGER; 
BEGIN
    result = (select count(*) from idot_dashcam_current
                where label = new.label 
               );

	-- Label exists, update table
    IF result = 1 THEN
	    UPDATE idot_dashcam_current SET idnum = new.idnum, geom = new.geom,
	    valid = new.valid WHERE label = new.label;
    END IF;

	-- Insert into log
	INSERT into idot_dashcam_log(label, valid, idnum, geom) VALUES
	(new.label, new.valid, new.idnum, new.geom);
	
	-- Stop insert from happening
	IF result = 1 THEN
		RETURN null;
	END IF;
	
    -- Allow insert to happen
    RETURN new;

END; $BODY$
LANGUAGE 'plpgsql' SECURITY DEFINER;

CREATE TRIGGER idot_dashcam_current_insert_before_T
   before insert
   ON idot_dashcam_current
   FOR EACH ROW
   EXECUTE PROCEDURE idot_dashcam_insert_before_F();

---
--- Store DOT snowplow data
---
CREATE TABLE idot_snowplow_current(
	label varchar(20) UNIQUE not null,
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
	road_temp_code smallint
);
SELECT AddGeometryColumn('idot_snowplow_current', 'geom', 4326, 'POINT', 2);
GRANT SELECT on idot_snowplow_current to nobody,apache;

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

---
--- Rawinsonde data!
---
CREATE TABLE raob_flights(
    fid SERIAL PRIMARY KEY,
    valid timestamptz,  -- Standard time of ob
    station varchar(4),
    hydro_level real,
    maxwd_level real,
    tropo_level real,
    release_time timestamptz, -- Time of Release
    sbcape_jkg real,
    sbcin_jkg real,
    mucape_jkg real,
    mucin_jkg real,
    pwater_mm real,
    computed boolean,
    lcl_agl_m real,
    lcl_pressure_hpa real,
    lcl_tmpc real,
    lfc_agl_m real,
    lfc_pressure_hpa real,
    lfc_tmpc real,
    el_agl_m real,
    el_pressure_hpa real,
    el_tmpc real,
    total_totals real,
    sweat_index real,
    bunkers_lm_smps real,
    bunkers_lm_drct real,
    bunkers_rm_smps real,
    bunkers_rm_drct real,
    mean_sfc_6km_smps real,
    mean_sfc_6km_drct real,
    srh_sfc_1km_pos real,
    srh_sfc_1km_neg real,
    srh_sfc_1km_total real,
    srh_sfc_3km_pos real,
    srh_sfc_3km_neg real,
    srh_sfc_3km_total real,
    shear_sfc_1km_smps real,
    shear_sfc_3km_smps real,
    shear_sfc_6km_smps real
);
ALTER TABLE raob_flights OWNER to mesonet;
GRANT ALL on raob_flights to ldm,mesonet;
create unique index raob_flights_idx on raob_flights(valid, station);
GRANT SELECT on raob_flights to nobody,apache;

CREATE TABLE raob_profile(
    fid int REFERENCES raob_flights(fid) ON DELETE CASCADE ON UPDATE CASCADE,
    ts timestamptz,
    levelcode smallint,
    pressure real, -- mb
    height real, -- m
    tmpc real, -- C
    dwpc real, -- C
    drct real, -- deg
    smps real, -- wind speed in MPS
    bearing real, -- deg
    range_miles real -- miles
);
ALTER TABLE raob_profile OWNER to mesonet;
CREATE INDEX raob_profile_fid_idx on raob_profile(fid);
GRANT SELECT on raob_profile to nobody,apache;

do
$do$
declare
     y int;
begin
    for y in 1946..2030
    loop
    execute format($f$
        CREATE TABLE raob_profile_%s
            (LIKE raob_profile INCLUDING all);
        ALTER TABLE raob_profile_%s INHERIT raob_profile;
        ALTER TABLE raob_profile_%s OWNER to mesonet;
        alter table raob_profile_%s add constraint fid_fk FOREIGN KEY (fid)
            REFERENCES raob_flights(fid) ON DELETE CASCADE ON UPDATE CASCADE;
        GRANT SELECT on raob_profile_%s to nobody,apache;
    $f$, y, y, y, y, y
    );
    end loop;
end;
$do$;


---
--- Missing VTEC eventids
---
CREATE TABLE vtec_missing_events(
  year smallint,
  wfo char(3),
  phenomena char(2),
  significance char(1),
  eventid int
);
GRANT ALL on vtec_missing_events to mesonet,ldm;
GRANT select on vtec_missing_events to nobody,apache;

---
--- Text Products
---
CREATE TABLE text_products (
    product text,
    product_id character varying(32),
    pil char(6),
    product_num smallint,
    issue timestamptz,
    expire timestamptz,
    geom geometry(MultiPolygon, 4326)
);

grant select on text_products to apache,nobody;

create index text_products_idx  on text_products(product_id);
CREATE INDEX text_products_issue_idx on text_products(issue);
CREATE INDEX text_products_expire_idx on text_products(expire);
create index text_products_pil_idx  on text_products(pil);

GRANT SELECT on text_products to nobody,apache;

---
--- riverpro
---
CREATE TABLE riverpro (
    nwsli character varying(5),
    stage_text text,
    flood_text text,
    forecast_text text,
    severity character(1),
    impact_text text
);

grant select on riverpro to apache,nobody;

CREATE UNIQUE INDEX riverpro_nwsli_idx ON riverpro USING btree (nwsli);

CREATE RULE replace_riverpro
 AS ON INSERT TO riverpro WHERE
 (EXISTS (SELECT 1 FROM riverpro
 WHERE ((riverpro.nwsli)::text = (new.nwsli)::text)))
 DO INSTEAD UPDATE riverpro SET stage_text = new.stage_text,
 flood_text = new.flood_text, forecast_text = new.forecast_text,
 severity = new.severity, impact_text = new.impact_text
 WHERE ((riverpro.nwsli)::text = (new.nwsli)::text);



---
--- VTEC Table
---
CREATE TABLE warnings (
    issue timestamp with time zone not null,
    expire timestamp with time zone not null,
    updated timestamp with time zone not null,
    wfo character(3) NOT NULL,
    eventid smallint NOT NULL,
    status character(3) NOT NULL,
    fcster character varying(24),
    report text,
    svs text,
    ugc character varying(6) NOT NULL,
    phenomena character(2) NOT NULL,
    significance character(1) NOT NULL,
    hvtec_nwsli character(5),
    gid int references ugcs(gid),
    init_expire timestamp with time zone not null,
    product_issue timestamp with time zone not null,
    is_emergency boolean
);
ALTER TABLE warnings OWNER to mesonet;
GRANT ALL on warnings to ldm;
grant select on warnings to apache,nobody;


do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 1986..2030
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


---
--- Storm Based Warnings Geo Tables
---
create table sbw(
  wfo char(3),
  eventid smallint,
  significance char(1),
  phenomena char(2),
  status char(3),
  issue timestamp with time zone,
  init_expire timestamp with time zone,
  expire timestamp with time zone,
  polygon_begin timestamp with time zone,
  polygon_end timestamp with time zone,
  report text,
  windtag real,
  hailtag real,
  tornadotag varchar(64),
  tornadodamagetag varchar(64),
  waterspouttag varchar(64),
  tml_valid timestamp with time zone,
  tml_direction smallint,
  tml_sknt smallint,
  updated timestamptz,
  is_emergency boolean,
  floodtag_heavyrain varchar(64),
  floodtag_flashflood varchar(64),
  floodtag_damage varchar(64),
  floodtag_leeve varchar(64),
  floodtag_dam varchar(64),
  geom geometry(MultiPolygon, 4326),
  tml_geom geometry(Point, 4326),
  tml_geom_line geometry(Linestring, 4326)
);
ALTER TABLE sbw OWNER to mesonet;
GRANT ALL on sbw to ldm;
grant select on sbw to apache,nobody;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 1986..2030
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


---
--- LSRs!
--- 
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
    for year in 1986..2030
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

---
--- HVTEC Table
---
CREATE TABLE hvtec_nwsli (
    nwsli character(5),
    river_name character varying(128),
    proximity character varying(16),
    name character varying(128),
    state character(2),
    geom geometry(Point, 4326)
);
grant select on hvtec_nwsli to apache,nobody;

---
--- UGC Lookup Table
---
CREATE TABLE nws_ugc (
    gid serial,
    polygon_class character varying(1),
    ugc character varying(6),
    name character varying(238),
    state character varying(2),
    time_zone character varying(2),
    wfo character varying(9),
    fe_area character varying(2),
    geom geometry(MultiPolygon, 4326),
    centroid geometry(Point, 4326),
    simple_geom geometry(MultiPolygon, 4326)
);

grant select on nws_ugc to apache,nobody;

---
--- SIGMET Convective Outlook
---
CREATE TABLE sigmets_current(
	sigmet_type char(1),
	label varchar(16),
	issue timestamp with time zone,
	expire timestamp with time zone,
	raw text
);
SELECT AddGeometryColumn('sigmets_current', 'geom', 4326, 'POLYGON', 2);
GRANT SELECT on sigmets_current to nobody,apache;

CREATE TABLE sigmets_archive(
	sigmet_type char(1),
	label varchar(16),
	issue timestamp with time zone,
	expire timestamp with time zone,
	raw text
);
SELECT AddGeometryColumn('sigmets_archive', 'geom', 4326, 'POLYGON', 2);
GRANT SELECT on sigmets_archive to nobody,apache;


---
--- NEXRAD N0R Composites 
---
CREATE TABLE nexrad_n0r_tindex(
 datetime timestamp without time zone,
 filepath varchar
 );
SELECT AddGeometryColumn('nexrad_n0r_tindex', 'the_geom', 4326, 'MULTIPOLYGON', 2);
GRANT SELECT on nexrad_n0r_tindex to nobody,apache;
CREATE INDEX nexrad_n0r_tindex_idx on nexrad_n0r_tindex(datetime);
create index nexrad_n0r_tindex_date_trunc on nexrad_n0r_tindex( date_trunc('minute', datetime) );


---
--- NEXRAD N0Q Composites 
---
CREATE TABLE nexrad_n0q_tindex(
 datetime timestamp without time zone,
 filepath varchar
 );
SELECT AddGeometryColumn('nexrad_n0q_tindex', 'the_geom', 4326, 'MULTIPOLYGON', 2);
GRANT SELECT on nexrad_n0q_tindex to nobody,apache;
CREATE INDEX nexrad_n0q_tindex_idx on nexrad_n0q_tindex(datetime);
create index nexrad_n0q_tindex_date_trunc on nexrad_n0q_tindex( date_trunc('minute', datetime) );

---
---
---
CREATE table roads_base(
	segid SERIAL unique,
	major varchar(32),
	minor varchar(128),
	us1 smallint,
	st1 smallint,
	int1 smallint,
	type smallint,
	wfo char(3),
	longname varchar(256),
	idot_id int,
	archive_begin timestamptz,
	archive_end timestamptz
);

SELECT AddGeometryColumn('roads_base', 'geom', 26915, 'MULTILINESTRING', 2);
SELECT AddGeometryColumn('roads_base', 'simple_geom', 26915, 'MULTILINESTRING', 2);

GRANT SELECT on roads_base to nobody,apache;

CREATE TABLE roads_conditions(
  code smallint unique,
  label varchar(128)
  );
GRANT SELECT on roads_conditions TO nobody,apache;

CREATE TABLE roads_current(
  segid int REFERENCES roads_base(segid),
  valid timestamp with time zone,
  cond_code smallint REFERENCES roads_conditions(code),
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar);
GRANT SELECT on roads_current to nobody,apache;

CREATE TABLE roads_2011_2012_log(
  segid int REFERENCES roads_base(segid),
  valid timestamptz,
  cond_code smallint REFERENCES roads_conditions(code),
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar);
GRANT SELECT on roads_2011_2012_log to nobody,apache;

CREATE TABLE roads_2012_2013_log(
  segid int REFERENCES roads_base(segid),
  valid timestamptz,
  cond_code smallint REFERENCES roads_conditions(code),
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar);
GRANT SELECT on roads_2012_2013_log to nobody,apache;

---
--- SPC Convective Outlooks
---
CREATE TABLE spc_outlooks (
  issue timestamp with time zone,
  product_issue timestamp with time zone,
  expire timestamp with time zone,
  threshold varchar(4),
  category varchar(64),
  day smallint,
  outlook_type char(1)
);
SELECT addGeometryColumn('', 'spc_outlooks', 'geom', 4326, 'MULTIPOLYGON', 2);
GRANT SELECT on spc_outlooks to apache,nobody;
CREATE index spc_outlooks_valid_idx on spc_outlooks(product_issue);
CREATE INDEX spc_outlooks_gix ON spc_outlooks USING GIST (geom);

-- Numeric prioritization of SPC Outlook Thresholds
CREATE TABLE spc_outlook_thresholds(
  priority smallint UNIQUE,
  threshold varchar(4));
GRANT SELECT on spc_outlook_thresholds to nobody,apache;
GRANT ALL on spc_outlook_thresholds to ldm,mesonet;

INSERT into spc_outlook_thresholds VALUES 
 (10, '0.02'),
 (20, '0.05'),
 (30, '0.10'),
 (40, '0.15'),
 (50, '0.25'),
 (60, '0.30'),
 (70, '0.35'),
 (80, '0.40'),
 (90, '0.45'),
 (100, '0.60'),
 (110, 'TSTM'),
 (120, 'MRGL'),
 (130, 'SLGT'),
 (140, 'ENH'),
 (150, 'MDT'),
 (160, 'HIGH'),
 (170, 'CRIT'),
 (180, 'EXTM');

CREATE TABLE watches (
	fid serial,
    sel character(5),
    issued timestamp with time zone,
    expired timestamp with time zone,
    type character(3),
    report text,
    num smallint,
    geom geometry(MultiPolygon, 4326)
);
grant select on watches to apache,nobody;

CREATE UNIQUE INDEX watches_idx ON watches USING btree (issued, num);

CREATE TABLE watches_current (
    sel character(5),
    issued timestamp with time zone,
    expired timestamp with time zone,
    type character(3),
    report text,
    num smallint,
    geom geometry(MultiPolygon, 4326)
);
GRANT ALL on watches_current to mesonet,ldm;
grant select on watches_current to apache,nobody;



-- !!!!!!!!!!!!! WARNING !!!!!!!!!!!!
-- look what was done in 9.sql and replicate that for 2016 updates


CREATE TABLE roads_2014_2015_log(
  segid int,
  valid timestamptz,
  cond_code smallint,
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar);
GRANT SELECT on roads_2014_2015_log to nobody,apache;

--
-- Storage of PIREPs
--
CREATE TABLE pireps(
  valid timestamptz,
  geom geography(POINT,4326),
  is_urgent boolean,
  aircraft_type varchar,
  report varchar
);
CREATE INDEX pireps_valid_idx on pireps(valid);
GRANT SELECT on pireps to nobody,apache;

-- Storage of Winter Road Conditions for 2015 - 2016
CREATE TABLE roads_2015_2016_log(
        segid int REFERENCES roads_base(segid),
        valid timestamptz,
        cond_code smallint REFERENCES roads_conditions(code),
        towing_prohibited boolean,
        limited_vis boolean,
        raw varchar);
GRANT SELECT on roads_2015_2016_log to nobody;

CREATE TABLE roads_2016_2017_log(
        segid int REFERENCES roads_base(segid),
        valid timestamptz,
        cond_code smallint REFERENCES roads_conditions(code),
        towing_prohibited boolean,
        limited_vis boolean,
        raw varchar);
GRANT SELECT on roads_2016_2017_log to nobody;

CREATE TABLE roads_2017_2018_log(
  segid INT references roads_base(segid),
  valid timestamptz,
  cond_code smallint references roads_conditions(code),
  towing_prohibited bool,
  limited_vis bool,
  raw varchar);

GRANT ALL on roads_2017_2018_log to mesonet,ldm;
GRANT SELECT on roads_2017_2018_log to apache,nobody;

CREATE TABLE roads_2018_2019_log(
  segid INT references roads_base(segid),
  valid timestamptz,
  cond_code smallint references roads_conditions(code),
  towing_prohibited bool,
  limited_vis bool,
  raw varchar);

GRANT ALL on roads_2018_2019_log to mesonet,ldm;
GRANT SELECT on roads_2018_2019_log to apache,nobody;

CREATE TABLE roads_2019_2020_log(
  segid INT references roads_base(segid),
  valid timestamptz,
  cond_code smallint references roads_conditions(code),
  towing_prohibited bool,
  limited_vis bool,
  raw varchar);

GRANT ALL on roads_2019_2020_log to mesonet,ldm;
GRANT SELECT on roads_2019_2020_log to apache,nobody;

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
    for year in 2000..2030
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



-- Storage of USDM
CREATE TABLE usdm(
  valid date,
  dm smallint,
  geom geometry(MultiPolygon, 4326));
CREATE INDEX usdm_valid_idx on usdm(valid);
GRANT SELECT on usdm to nobody,apache;
GRANT ALL on usdm to mesonet,ldm;

-- Storage of MCDs
CREATE TABLE mcd(
    product_id varchar(32),
    geom geometry(Polygon,4326),
    product text,
    year int NOT NULL,
    num int NOT NULL,
    issue timestamptz,
    expire timestamptz,
    watch_confidence smallint
);
ALTER TABLE mcd OWNER to mesonet;
GRANT ALL on mcd to ldm;
GRANT SELECT on mcd to nobody;

CREATE INDEX ON mcd(issue);
CREATE INDEX ON mcd(num);
CREATE INDEX mcd_geom_index on mcd USING GIST(geom);

-- Storage of MPDs
CREATE TABLE mpd(
    product_id varchar(32),
    geom geometry(Polygon,4326),
    product text,
    year int NOT NULL,
    num int NOT NULL,
    issue timestamptz,
    expire timestamptz,
    watch_confidence smallint
);
ALTER TABLE mpd OWNER to mesonet;
GRANT ALL on mpd to ldm;
GRANT SELECT on mpd to nobody;

CREATE INDEX ON mpd(issue);
CREATE INDEX ON mpd(num);
CREATE INDEX mpd_geom_index on mpd USING GIST(geom);
