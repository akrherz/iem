CREATE EXTENSION postgis;

-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (35, now());

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
    sweat_index real
);
ALTER TABLE raob_flights OWNER to mesonet;
GRANT ALL on raob_flights to ldm,mesonet;
create unique index raob_flights_idx on raob_flights(valid, station);
GRANT SELECT on raob_flights to nobody,apache;

CREATE TABLE raob_profile(
    fid int REFERENCES raob_flights(fid),
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
GRANT SELECT on raob_profile to nobody,apache;

CREATE TABLE raob_profile_1946() inherits (raob_profile);
GRANT SELECT on raob_profile_1946 to nobody,apache;
CREATE INDEX raob_profile_1946_fid_idx 
	on raob_profile_1946(fid);
    

CREATE TABLE raob_profile_1947() inherits (raob_profile);
GRANT SELECT on raob_profile_1947 to nobody,apache;
CREATE INDEX raob_profile_1947_fid_idx 
	on raob_profile_1947(fid);
    

CREATE TABLE raob_profile_1948() inherits (raob_profile);
GRANT SELECT on raob_profile_1948 to nobody,apache;
CREATE INDEX raob_profile_1948_fid_idx 
	on raob_profile_1948(fid);
    

CREATE TABLE raob_profile_1949() inherits (raob_profile);
GRANT SELECT on raob_profile_1949 to nobody,apache;
CREATE INDEX raob_profile_1949_fid_idx 
	on raob_profile_1949(fid);
    

CREATE TABLE raob_profile_1950() inherits (raob_profile);
GRANT SELECT on raob_profile_1950 to nobody,apache;
CREATE INDEX raob_profile_1950_fid_idx 
	on raob_profile_1950(fid);
    

CREATE TABLE raob_profile_1951() inherits (raob_profile);
GRANT SELECT on raob_profile_1951 to nobody,apache;
CREATE INDEX raob_profile_1951_fid_idx 
	on raob_profile_1951(fid);
    

CREATE TABLE raob_profile_1952() inherits (raob_profile);
GRANT SELECT on raob_profile_1952 to nobody,apache;
CREATE INDEX raob_profile_1952_fid_idx 
	on raob_profile_1952(fid);
    

CREATE TABLE raob_profile_1953() inherits (raob_profile);
GRANT SELECT on raob_profile_1953 to nobody,apache;
CREATE INDEX raob_profile_1953_fid_idx 
	on raob_profile_1953(fid);
    

CREATE TABLE raob_profile_1954() inherits (raob_profile);
GRANT SELECT on raob_profile_1954 to nobody,apache;
CREATE INDEX raob_profile_1954_fid_idx 
	on raob_profile_1954(fid);
    

CREATE TABLE raob_profile_1955() inherits (raob_profile);
GRANT SELECT on raob_profile_1955 to nobody,apache;
CREATE INDEX raob_profile_1955_fid_idx 
	on raob_profile_1955(fid);
    

CREATE TABLE raob_profile_1956() inherits (raob_profile);
GRANT SELECT on raob_profile_1956 to nobody,apache;
CREATE INDEX raob_profile_1956_fid_idx 
	on raob_profile_1956(fid);
    

CREATE TABLE raob_profile_1957() inherits (raob_profile);
GRANT SELECT on raob_profile_1957 to nobody,apache;
CREATE INDEX raob_profile_1957_fid_idx 
	on raob_profile_1957(fid);
    

CREATE TABLE raob_profile_1958() inherits (raob_profile);
GRANT SELECT on raob_profile_1958 to nobody,apache;
CREATE INDEX raob_profile_1958_fid_idx 
	on raob_profile_1958(fid);
    

CREATE TABLE raob_profile_1959() inherits (raob_profile);
GRANT SELECT on raob_profile_1959 to nobody,apache;
CREATE INDEX raob_profile_1959_fid_idx 
	on raob_profile_1959(fid);
    

CREATE TABLE raob_profile_1960() inherits (raob_profile);
GRANT SELECT on raob_profile_1960 to nobody,apache;
CREATE INDEX raob_profile_1960_fid_idx 
	on raob_profile_1960(fid);
    

CREATE TABLE raob_profile_1961() inherits (raob_profile);
GRANT SELECT on raob_profile_1961 to nobody,apache;
CREATE INDEX raob_profile_1961_fid_idx 
	on raob_profile_1961(fid);
    

CREATE TABLE raob_profile_1962() inherits (raob_profile);
GRANT SELECT on raob_profile_1962 to nobody,apache;
CREATE INDEX raob_profile_1962_fid_idx 
	on raob_profile_1962(fid);
    

CREATE TABLE raob_profile_1963() inherits (raob_profile);
GRANT SELECT on raob_profile_1963 to nobody,apache;
CREATE INDEX raob_profile_1963_fid_idx 
	on raob_profile_1963(fid);
    

CREATE TABLE raob_profile_1964() inherits (raob_profile);
GRANT SELECT on raob_profile_1964 to nobody,apache;
CREATE INDEX raob_profile_1964_fid_idx 
	on raob_profile_1964(fid);
    

CREATE TABLE raob_profile_1965() inherits (raob_profile);
GRANT SELECT on raob_profile_1965 to nobody,apache;
CREATE INDEX raob_profile_1965_fid_idx 
	on raob_profile_1965(fid);
    

CREATE TABLE raob_profile_1966() inherits (raob_profile);
GRANT SELECT on raob_profile_1966 to nobody,apache;
CREATE INDEX raob_profile_1966_fid_idx 
	on raob_profile_1966(fid);
    

CREATE TABLE raob_profile_1967() inherits (raob_profile);
GRANT SELECT on raob_profile_1967 to nobody,apache;
CREATE INDEX raob_profile_1967_fid_idx 
	on raob_profile_1967(fid);
    

CREATE TABLE raob_profile_1968() inherits (raob_profile);
GRANT SELECT on raob_profile_1968 to nobody,apache;
CREATE INDEX raob_profile_1968_fid_idx 
	on raob_profile_1968(fid);
    

CREATE TABLE raob_profile_1969() inherits (raob_profile);
GRANT SELECT on raob_profile_1969 to nobody,apache;
CREATE INDEX raob_profile_1969_fid_idx 
	on raob_profile_1969(fid);
    

CREATE TABLE raob_profile_1970() inherits (raob_profile);
GRANT SELECT on raob_profile_1970 to nobody,apache;
CREATE INDEX raob_profile_1970_fid_idx 
	on raob_profile_1970(fid);
    

CREATE TABLE raob_profile_1971() inherits (raob_profile);
GRANT SELECT on raob_profile_1971 to nobody,apache;
CREATE INDEX raob_profile_1971_fid_idx 
	on raob_profile_1971(fid);
    

CREATE TABLE raob_profile_1972() inherits (raob_profile);
GRANT SELECT on raob_profile_1972 to nobody,apache;
CREATE INDEX raob_profile_1972_fid_idx 
	on raob_profile_1972(fid);
    

CREATE TABLE raob_profile_1973() inherits (raob_profile);
GRANT SELECT on raob_profile_1973 to nobody,apache;
CREATE INDEX raob_profile_1973_fid_idx 
	on raob_profile_1973(fid);
    

CREATE TABLE raob_profile_1974() inherits (raob_profile);
GRANT SELECT on raob_profile_1974 to nobody,apache;
CREATE INDEX raob_profile_1974_fid_idx 
	on raob_profile_1974(fid);
    

CREATE TABLE raob_profile_1975() inherits (raob_profile);
GRANT SELECT on raob_profile_1975 to nobody,apache;
CREATE INDEX raob_profile_1975_fid_idx 
	on raob_profile_1975(fid);
    

CREATE TABLE raob_profile_1976() inherits (raob_profile);
GRANT SELECT on raob_profile_1976 to nobody,apache;
CREATE INDEX raob_profile_1976_fid_idx 
	on raob_profile_1976(fid);
    

CREATE TABLE raob_profile_1977() inherits (raob_profile);
GRANT SELECT on raob_profile_1977 to nobody,apache;
CREATE INDEX raob_profile_1977_fid_idx 
	on raob_profile_1977(fid);
    

CREATE TABLE raob_profile_1978() inherits (raob_profile);
GRANT SELECT on raob_profile_1978 to nobody,apache;
CREATE INDEX raob_profile_1978_fid_idx 
	on raob_profile_1978(fid);
    

CREATE TABLE raob_profile_1979() inherits (raob_profile);
GRANT SELECT on raob_profile_1979 to nobody,apache;
CREATE INDEX raob_profile_1979_fid_idx 
	on raob_profile_1979(fid);
    

CREATE TABLE raob_profile_1980() inherits (raob_profile);
GRANT SELECT on raob_profile_1980 to nobody,apache;
CREATE INDEX raob_profile_1980_fid_idx 
	on raob_profile_1980(fid);
    

CREATE TABLE raob_profile_1981() inherits (raob_profile);
GRANT SELECT on raob_profile_1981 to nobody,apache;
CREATE INDEX raob_profile_1981_fid_idx 
	on raob_profile_1981(fid);
    

CREATE TABLE raob_profile_1982() inherits (raob_profile);
GRANT SELECT on raob_profile_1982 to nobody,apache;
CREATE INDEX raob_profile_1982_fid_idx 
	on raob_profile_1982(fid);
    

CREATE TABLE raob_profile_1983() inherits (raob_profile);
GRANT SELECT on raob_profile_1983 to nobody,apache;
CREATE INDEX raob_profile_1983_fid_idx 
	on raob_profile_1983(fid);
    

CREATE TABLE raob_profile_1984() inherits (raob_profile);
GRANT SELECT on raob_profile_1984 to nobody,apache;
CREATE INDEX raob_profile_1984_fid_idx 
	on raob_profile_1984(fid);
    

CREATE TABLE raob_profile_1985() inherits (raob_profile);
GRANT SELECT on raob_profile_1985 to nobody,apache;
CREATE INDEX raob_profile_1985_fid_idx 
	on raob_profile_1985(fid);
    

CREATE TABLE raob_profile_1986() inherits (raob_profile);
GRANT SELECT on raob_profile_1986 to nobody,apache;
CREATE INDEX raob_profile_1986_fid_idx 
	on raob_profile_1986(fid);
    

CREATE TABLE raob_profile_1987() inherits (raob_profile);
GRANT SELECT on raob_profile_1987 to nobody,apache;
CREATE INDEX raob_profile_1987_fid_idx 
	on raob_profile_1987(fid);
    

CREATE TABLE raob_profile_1988() inherits (raob_profile);
GRANT SELECT on raob_profile_1988 to nobody,apache;
CREATE INDEX raob_profile_1988_fid_idx 
	on raob_profile_1988(fid);
    

CREATE TABLE raob_profile_1989() inherits (raob_profile);
GRANT SELECT on raob_profile_1989 to nobody,apache;
CREATE INDEX raob_profile_1989_fid_idx 
	on raob_profile_1989(fid);
    

CREATE TABLE raob_profile_1990() inherits (raob_profile);
GRANT SELECT on raob_profile_1990 to nobody,apache;
CREATE INDEX raob_profile_1990_fid_idx 
	on raob_profile_1990(fid);
    

CREATE TABLE raob_profile_1991() inherits (raob_profile);
GRANT SELECT on raob_profile_1991 to nobody,apache;
CREATE INDEX raob_profile_1991_fid_idx 
	on raob_profile_1991(fid);
    

CREATE TABLE raob_profile_1992() inherits (raob_profile);
GRANT SELECT on raob_profile_1992 to nobody,apache;
CREATE INDEX raob_profile_1992_fid_idx 
	on raob_profile_1992(fid);
    

CREATE TABLE raob_profile_1993() inherits (raob_profile);
GRANT SELECT on raob_profile_1993 to nobody,apache;
CREATE INDEX raob_profile_1993_fid_idx 
	on raob_profile_1993(fid);
    

CREATE TABLE raob_profile_1994() inherits (raob_profile);
GRANT SELECT on raob_profile_1994 to nobody,apache;
CREATE INDEX raob_profile_1994_fid_idx 
	on raob_profile_1994(fid);
    

CREATE TABLE raob_profile_1995() inherits (raob_profile);
GRANT SELECT on raob_profile_1995 to nobody,apache;
CREATE INDEX raob_profile_1995_fid_idx 
	on raob_profile_1995(fid);
    

CREATE TABLE raob_profile_1996() inherits (raob_profile);
GRANT SELECT on raob_profile_1996 to nobody,apache;
CREATE INDEX raob_profile_1996_fid_idx 
	on raob_profile_1996(fid);
    

CREATE TABLE raob_profile_1997() inherits (raob_profile);
GRANT SELECT on raob_profile_1997 to nobody,apache;
CREATE INDEX raob_profile_1997_fid_idx 
	on raob_profile_1997(fid);
    

CREATE TABLE raob_profile_1998() inherits (raob_profile);
GRANT SELECT on raob_profile_1998 to nobody,apache;
CREATE INDEX raob_profile_1998_fid_idx 
	on raob_profile_1998(fid);
    

CREATE TABLE raob_profile_1999() inherits (raob_profile);
GRANT SELECT on raob_profile_1999 to nobody,apache;
CREATE INDEX raob_profile_1999_fid_idx 
	on raob_profile_1999(fid);
    

CREATE TABLE raob_profile_2000() inherits (raob_profile);
GRANT SELECT on raob_profile_2000 to nobody,apache;
CREATE INDEX raob_profile_2000_fid_idx 
	on raob_profile_2000(fid);
    

CREATE TABLE raob_profile_2001() inherits (raob_profile);
GRANT SELECT on raob_profile_2001 to nobody,apache;
CREATE INDEX raob_profile_2001_fid_idx 
	on raob_profile_2001(fid);
    

CREATE TABLE raob_profile_2002() inherits (raob_profile);
GRANT SELECT on raob_profile_2002 to nobody,apache;
CREATE INDEX raob_profile_2002_fid_idx 
	on raob_profile_2002(fid);
    

CREATE TABLE raob_profile_2003() inherits (raob_profile);
GRANT SELECT on raob_profile_2003 to nobody,apache;
CREATE INDEX raob_profile_2003_fid_idx 
	on raob_profile_2003(fid);
    

CREATE TABLE raob_profile_2004() inherits (raob_profile);
GRANT SELECT on raob_profile_2004 to nobody,apache;
CREATE INDEX raob_profile_2004_fid_idx 
	on raob_profile_2004(fid);
    

CREATE TABLE raob_profile_2005() inherits (raob_profile);
GRANT SELECT on raob_profile_2005 to nobody,apache;
CREATE INDEX raob_profile_2005_fid_idx 
	on raob_profile_2005(fid);
    

CREATE TABLE raob_profile_2006() inherits (raob_profile);
GRANT SELECT on raob_profile_2006 to nobody,apache;
CREATE INDEX raob_profile_2006_fid_idx 
	on raob_profile_2006(fid);
    

CREATE TABLE raob_profile_2007() inherits (raob_profile);
GRANT SELECT on raob_profile_2007 to nobody,apache;
CREATE INDEX raob_profile_2007_fid_idx 
	on raob_profile_2007(fid);
    

CREATE TABLE raob_profile_2008() inherits (raob_profile);
GRANT SELECT on raob_profile_2008 to nobody,apache;
CREATE INDEX raob_profile_2008_fid_idx 
	on raob_profile_2008(fid);
    

CREATE TABLE raob_profile_2009() inherits (raob_profile);
GRANT SELECT on raob_profile_2009 to nobody,apache;
CREATE INDEX raob_profile_2009_fid_idx 
	on raob_profile_2009(fid);
    

CREATE TABLE raob_profile_2010() inherits (raob_profile);
GRANT SELECT on raob_profile_2010 to nobody,apache;
CREATE INDEX raob_profile_2010_fid_idx 
	on raob_profile_2010(fid);
    

CREATE TABLE raob_profile_2011() inherits (raob_profile);
GRANT SELECT on raob_profile_2011 to nobody,apache;
CREATE INDEX raob_profile_2011_fid_idx 
	on raob_profile_2011(fid);
    

CREATE TABLE raob_profile_2012() inherits (raob_profile);
GRANT SELECT on raob_profile_2012 to nobody,apache;
CREATE INDEX raob_profile_2012_fid_idx 
	on raob_profile_2012(fid);
    

CREATE TABLE raob_profile_2013() inherits (raob_profile);
GRANT SELECT on raob_profile_2013 to nobody,apache;
CREATE INDEX raob_profile_2013_fid_idx 
	on raob_profile_2013(fid);
    

CREATE TABLE raob_profile_2014() inherits (raob_profile);
GRANT SELECT on raob_profile_2014 to nobody,apache;
CREATE INDEX raob_profile_2014_fid_idx 
	on raob_profile_2014(fid);


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
    expire timestamptz
);
select addgeometrycolumn('','text_products','geom',4326,'MULTIPOLYGON',2);

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
    wfo character(3),
    eventid smallint,
    status character(3),
    fcster character varying(24),
    report text,
    svs text,
    ugc character varying(6),
    phenomena character(2),
    significance character(1),
    hvtec_nwsli character(5),
    gid int references ugcs(gid),
    init_expire timestamp with time zone not null,
    product_issue timestamp with time zone not null,
    is_emergency boolean
) WITH OIDS;

grant select on warnings to apache,nobody;

CREATE TABLE warnings_1986() inherits (warnings);
CREATE INDEX warnings_1986_combo_idx on 
	warnings_1986(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1986_expire_idx on warnings_1986(expire);
CREATE INDEX warnings_1986_issue_idx on warnings_1986(issue);
CREATE INDEX warnings_1986_ugc_idx on warnings_1986(ugc);
CREATE INDEX warnings_1986_wfo_idx on warnings_1986(wfo);
grant select on warnings_1986 to nobody,apache;
    

CREATE TABLE warnings_1987() inherits (warnings);
CREATE INDEX warnings_1987_combo_idx on 
	warnings_1987(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1987_expire_idx on warnings_1987(expire);
CREATE INDEX warnings_1987_issue_idx on warnings_1987(issue);
CREATE INDEX warnings_1987_ugc_idx on warnings_1987(ugc);
CREATE INDEX warnings_1987_wfo_idx on warnings_1987(wfo);
grant select on warnings_1987 to nobody,apache;
    

CREATE TABLE warnings_1988() inherits (warnings);
CREATE INDEX warnings_1988_combo_idx on 
	warnings_1988(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1988_expire_idx on warnings_1988(expire);
CREATE INDEX warnings_1988_issue_idx on warnings_1988(issue);
CREATE INDEX warnings_1988_ugc_idx on warnings_1988(ugc);
CREATE INDEX warnings_1988_wfo_idx on warnings_1988(wfo);
grant select on warnings_1988 to nobody,apache;
    

CREATE TABLE warnings_1989() inherits (warnings);
CREATE INDEX warnings_1989_combo_idx on 
	warnings_1989(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1989_expire_idx on warnings_1989(expire);
CREATE INDEX warnings_1989_issue_idx on warnings_1989(issue);
CREATE INDEX warnings_1989_ugc_idx on warnings_1989(ugc);
CREATE INDEX warnings_1989_wfo_idx on warnings_1989(wfo);
grant select on warnings_1989 to nobody,apache;
    

CREATE TABLE warnings_1990() inherits (warnings);
CREATE INDEX warnings_1990_combo_idx on 
	warnings_1990(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1990_expire_idx on warnings_1990(expire);
CREATE INDEX warnings_1990_issue_idx on warnings_1990(issue);
CREATE INDEX warnings_1990_ugc_idx on warnings_1990(ugc);
CREATE INDEX warnings_1990_wfo_idx on warnings_1990(wfo);
grant select on warnings_1990 to nobody,apache;
    

CREATE TABLE warnings_1991() inherits (warnings);
CREATE INDEX warnings_1991_combo_idx on 
	warnings_1991(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1991_expire_idx on warnings_1991(expire);
CREATE INDEX warnings_1991_issue_idx on warnings_1991(issue);
CREATE INDEX warnings_1991_ugc_idx on warnings_1991(ugc);
CREATE INDEX warnings_1991_wfo_idx on warnings_1991(wfo);
grant select on warnings_1991 to nobody,apache;
    

CREATE TABLE warnings_1992() inherits (warnings);
CREATE INDEX warnings_1992_combo_idx on 
	warnings_1992(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1992_expire_idx on warnings_1992(expire);
CREATE INDEX warnings_1992_issue_idx on warnings_1992(issue);
CREATE INDEX warnings_1992_ugc_idx on warnings_1992(ugc);
CREATE INDEX warnings_1992_wfo_idx on warnings_1992(wfo);
grant select on warnings_1992 to nobody,apache;
    

CREATE TABLE warnings_1993() inherits (warnings);
CREATE INDEX warnings_1993_combo_idx on 
	warnings_1993(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1993_expire_idx on warnings_1993(expire);
CREATE INDEX warnings_1993_issue_idx on warnings_1993(issue);
CREATE INDEX warnings_1993_ugc_idx on warnings_1993(ugc);
CREATE INDEX warnings_1993_wfo_idx on warnings_1993(wfo);
grant select on warnings_1993 to nobody,apache;
    

CREATE TABLE warnings_1994() inherits (warnings);
CREATE INDEX warnings_1994_combo_idx on 
	warnings_1994(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1994_expire_idx on warnings_1994(expire);
CREATE INDEX warnings_1994_issue_idx on warnings_1994(issue);
CREATE INDEX warnings_1994_ugc_idx on warnings_1994(ugc);
CREATE INDEX warnings_1994_wfo_idx on warnings_1994(wfo);
grant select on warnings_1994 to nobody,apache;
    

CREATE TABLE warnings_1995() inherits (warnings);
CREATE INDEX warnings_1995_combo_idx on 
	warnings_1995(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1995_expire_idx on warnings_1995(expire);
CREATE INDEX warnings_1995_issue_idx on warnings_1995(issue);
CREATE INDEX warnings_1995_ugc_idx on warnings_1995(ugc);
CREATE INDEX warnings_1995_wfo_idx on warnings_1995(wfo);
grant select on warnings_1995 to nobody,apache;
    

CREATE TABLE warnings_1996() inherits (warnings);
CREATE INDEX warnings_1996_combo_idx on 
	warnings_1996(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1996_expire_idx on warnings_1996(expire);
CREATE INDEX warnings_1996_issue_idx on warnings_1996(issue);
CREATE INDEX warnings_1996_ugc_idx on warnings_1996(ugc);
CREATE INDEX warnings_1996_wfo_idx on warnings_1996(wfo);
grant select on warnings_1996 to nobody,apache;
    

CREATE TABLE warnings_1997() inherits (warnings);
CREATE INDEX warnings_1997_combo_idx on 
	warnings_1997(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1997_expire_idx on warnings_1997(expire);
CREATE INDEX warnings_1997_issue_idx on warnings_1997(issue);
CREATE INDEX warnings_1997_ugc_idx on warnings_1997(ugc);
CREATE INDEX warnings_1997_wfo_idx on warnings_1997(wfo);
grant select on warnings_1997 to nobody,apache;
    

CREATE TABLE warnings_1998() inherits (warnings);
CREATE INDEX warnings_1998_combo_idx on 
	warnings_1998(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1998_expire_idx on warnings_1998(expire);
CREATE INDEX warnings_1998_issue_idx on warnings_1998(issue);
CREATE INDEX warnings_1998_ugc_idx on warnings_1998(ugc);
CREATE INDEX warnings_1998_wfo_idx on warnings_1998(wfo);
grant select on warnings_1998 to nobody,apache;
    

CREATE TABLE warnings_1999() inherits (warnings);
CREATE INDEX warnings_1999_combo_idx on 
	warnings_1999(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1999_expire_idx on warnings_1999(expire);
CREATE INDEX warnings_1999_issue_idx on warnings_1999(issue);
CREATE INDEX warnings_1999_ugc_idx on warnings_1999(ugc);
CREATE INDEX warnings_1999_wfo_idx on warnings_1999(wfo);
grant select on warnings_1999 to nobody,apache;
    

CREATE TABLE warnings_2000() inherits (warnings);
CREATE INDEX warnings_2000_combo_idx on 
	warnings_2000(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2000_expire_idx on warnings_2000(expire);
CREATE INDEX warnings_2000_issue_idx on warnings_2000(issue);
CREATE INDEX warnings_2000_ugc_idx on warnings_2000(ugc);
CREATE INDEX warnings_2000_wfo_idx on warnings_2000(wfo);
grant select on warnings_2000 to nobody,apache;
    

CREATE TABLE warnings_2001() inherits (warnings);
CREATE INDEX warnings_2001_combo_idx on 
	warnings_2001(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2001_expire_idx on warnings_2001(expire);
CREATE INDEX warnings_2001_issue_idx on warnings_2001(issue);
CREATE INDEX warnings_2001_ugc_idx on warnings_2001(ugc);
CREATE INDEX warnings_2001_wfo_idx on warnings_2001(wfo);
grant select on warnings_2001 to nobody,apache;
    

CREATE TABLE warnings_2002() inherits (warnings);
CREATE INDEX warnings_2002_combo_idx on 
	warnings_2002(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2002_expire_idx on warnings_2002(expire);
CREATE INDEX warnings_2002_issue_idx on warnings_2002(issue);
CREATE INDEX warnings_2002_ugc_idx on warnings_2002(ugc);
CREATE INDEX warnings_2002_wfo_idx on warnings_2002(wfo);
grant select on warnings_2002 to nobody,apache;
    

CREATE TABLE warnings_2003() inherits (warnings);
CREATE INDEX warnings_2003_combo_idx on 
	warnings_2003(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2003_expire_idx on warnings_2003(expire);
CREATE INDEX warnings_2003_issue_idx on warnings_2003(issue);
CREATE INDEX warnings_2003_ugc_idx on warnings_2003(ugc);
CREATE INDEX warnings_2003_wfo_idx on warnings_2003(wfo);
grant select on warnings_2003 to nobody,apache;
    

CREATE TABLE warnings_2004() inherits (warnings);
CREATE INDEX warnings_2004_combo_idx on 
	warnings_2004(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2004_expire_idx on warnings_2004(expire);
CREATE INDEX warnings_2004_issue_idx on warnings_2004(issue);
CREATE INDEX warnings_2004_ugc_idx on warnings_2004(ugc);
CREATE INDEX warnings_2004_wfo_idx on warnings_2004(wfo);
grant select on warnings_2004 to nobody,apache;
    

CREATE TABLE warnings_2005() inherits (warnings);
CREATE INDEX warnings_2005_combo_idx on 
	warnings_2005(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2005_expire_idx on warnings_2005(expire);
CREATE INDEX warnings_2005_issue_idx on warnings_2005(issue);
CREATE INDEX warnings_2005_ugc_idx on warnings_2005(ugc);
CREATE INDEX warnings_2005_wfo_idx on warnings_2005(wfo);
grant select on warnings_2005 to nobody,apache;
    

CREATE TABLE warnings_2006() inherits (warnings);
CREATE INDEX warnings_2006_combo_idx on 
	warnings_2006(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2006_expire_idx on warnings_2006(expire);
CREATE INDEX warnings_2006_issue_idx on warnings_2006(issue);
CREATE INDEX warnings_2006_ugc_idx on warnings_2006(ugc);
CREATE INDEX warnings_2006_wfo_idx on warnings_2006(wfo);
grant select on warnings_2006 to nobody,apache;
    

CREATE TABLE warnings_2007() inherits (warnings);
CREATE INDEX warnings_2007_combo_idx on 
	warnings_2007(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2007_expire_idx on warnings_2007(expire);
CREATE INDEX warnings_2007_issue_idx on warnings_2007(issue);
CREATE INDEX warnings_2007_ugc_idx on warnings_2007(ugc);
CREATE INDEX warnings_2007_wfo_idx on warnings_2007(wfo);
grant select on warnings_2007 to nobody,apache;
    

CREATE TABLE warnings_2008() inherits (warnings);
CREATE INDEX warnings_2008_combo_idx on 
	warnings_2008(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2008_expire_idx on warnings_2008(expire);
CREATE INDEX warnings_2008_issue_idx on warnings_2008(issue);
CREATE INDEX warnings_2008_ugc_idx on warnings_2008(ugc);
CREATE INDEX warnings_2008_wfo_idx on warnings_2008(wfo);
grant select on warnings_2008 to nobody,apache;
    

CREATE TABLE warnings_2009() inherits (warnings);
CREATE INDEX warnings_2009_combo_idx on 
	warnings_2009(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2009_expire_idx on warnings_2009(expire);
CREATE INDEX warnings_2009_issue_idx on warnings_2009(issue);
CREATE INDEX warnings_2009_ugc_idx on warnings_2009(ugc);
CREATE INDEX warnings_2009_wfo_idx on warnings_2009(wfo);
grant select on warnings_2009 to nobody,apache;
    

CREATE TABLE warnings_2010() inherits (warnings);
CREATE INDEX warnings_2010_combo_idx on 
	warnings_2010(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2010_expire_idx on warnings_2010(expire);
CREATE INDEX warnings_2010_issue_idx on warnings_2010(issue);
CREATE INDEX warnings_2010_ugc_idx on warnings_2010(ugc);
CREATE INDEX warnings_2010_wfo_idx on warnings_2010(wfo);
grant select on warnings_2010 to nobody,apache;
    

CREATE TABLE warnings_2011() inherits (warnings);
CREATE INDEX warnings_2011_combo_idx on 
	warnings_2011(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2011_expire_idx on warnings_2011(expire);
CREATE INDEX warnings_2011_issue_idx on warnings_2011(issue);
CREATE INDEX warnings_2011_ugc_idx on warnings_2011(ugc);
CREATE INDEX warnings_2011_wfo_idx on warnings_2011(wfo);
grant select on warnings_2011 to nobody,apache;
    

CREATE TABLE warnings_2012() inherits (warnings);
CREATE INDEX warnings_2012_combo_idx on 
	warnings_2012(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2012_expire_idx on warnings_2012(expire);
CREATE INDEX warnings_2012_issue_idx on warnings_2012(issue);
CREATE INDEX warnings_2012_ugc_idx on warnings_2012(ugc);
CREATE INDEX warnings_2012_wfo_idx on warnings_2012(wfo);
grant select on warnings_2012 to nobody,apache;
    

CREATE TABLE warnings_2013() inherits (warnings);
CREATE INDEX warnings_2013_combo_idx on 
	warnings_2013(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2013_expire_idx on warnings_2013(expire);
CREATE INDEX warnings_2013_issue_idx on warnings_2013(issue);
CREATE INDEX warnings_2013_ugc_idx on warnings_2013(ugc);
CREATE INDEX warnings_2013_wfo_idx on warnings_2013(wfo);
grant select on warnings_2013 to nobody,apache;


CREATE TABLE warnings_2014() inherits (warnings);
CREATE INDEX warnings_2014_combo_idx on 
	warnings_2014(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2014_expire_idx on warnings_2014(expire);
CREATE INDEX warnings_2014_issue_idx on warnings_2014(issue);
CREATE INDEX warnings_2014_ugc_idx on warnings_2014(ugc);
CREATE INDEX warnings_2014_wfo_idx on warnings_2014(wfo);
grant select on warnings_2014 to nobody,apache;

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
  floodtag_dam varchar(64)
) WITH OIDS;
select addgeometrycolumn('','sbw','geom',4326,'MULTIPOLYGON',2);
select addGeometryColumn('sbw', 'tml_geom', 4326, 'POINT', 2);
select addGeometryColumn('sbw', 'tml_geom_line', 4326, 'LINESTRING', 2);

grant select on sbw to apache,nobody;

CREATE table sbw_2002() inherits (sbw);
create index sbw_2002_idx on sbw_2002(wfo,eventid,significance,phenomena);
create index sbw_2002_expire_idx on sbw_2002(expire);
create index sbw_2002_issue_idx on sbw_2002(issue);
create index sbw_2002_wfo_idx on sbw_2002(wfo);
grant select on sbw_2002 to apache,nobody;
    

CREATE table sbw_2003() inherits (sbw);
create index sbw_2003_idx on sbw_2003(wfo,eventid,significance,phenomena);
create index sbw_2003_expire_idx on sbw_2003(expire);
create index sbw_2003_issue_idx on sbw_2003(issue);
create index sbw_2003_wfo_idx on sbw_2003(wfo);
grant select on sbw_2003 to apache,nobody;
    

CREATE table sbw_2004() inherits (sbw);
create index sbw_2004_idx on sbw_2004(wfo,eventid,significance,phenomena);
create index sbw_2004_expire_idx on sbw_2004(expire);
create index sbw_2004_issue_idx on sbw_2004(issue);
create index sbw_2004_wfo_idx on sbw_2004(wfo);
grant select on sbw_2004 to apache,nobody;
    

CREATE table sbw_2005() inherits (sbw);
create index sbw_2005_idx on sbw_2005(wfo,eventid,significance,phenomena);
create index sbw_2005_expire_idx on sbw_2005(expire);
create index sbw_2005_issue_idx on sbw_2005(issue);
create index sbw_2005_wfo_idx on sbw_2005(wfo);
grant select on sbw_2005 to apache,nobody;
    

CREATE table sbw_2006() inherits (sbw);
create index sbw_2006_idx on sbw_2006(wfo,eventid,significance,phenomena);
create index sbw_2006_expire_idx on sbw_2006(expire);
create index sbw_2006_issue_idx on sbw_2006(issue);
create index sbw_2006_wfo_idx on sbw_2006(wfo);
grant select on sbw_2006 to apache,nobody;
    

CREATE table sbw_2007() inherits (sbw);
create index sbw_2007_idx on sbw_2007(wfo,eventid,significance,phenomena);
create index sbw_2007_expire_idx on sbw_2007(expire);
create index sbw_2007_issue_idx on sbw_2007(issue);
create index sbw_2007_wfo_idx on sbw_2007(wfo);
grant select on sbw_2007 to apache,nobody;
    

CREATE table sbw_2008() inherits (sbw);
create index sbw_2008_idx on sbw_2008(wfo,eventid,significance,phenomena);
create index sbw_2008_expire_idx on sbw_2008(expire);
create index sbw_2008_issue_idx on sbw_2008(issue);
create index sbw_2008_wfo_idx on sbw_2008(wfo);
grant select on sbw_2008 to apache,nobody;
    

CREATE table sbw_2009() inherits (sbw);
create index sbw_2009_idx on sbw_2009(wfo,eventid,significance,phenomena);
create index sbw_2009_expire_idx on sbw_2009(expire);
create index sbw_2009_issue_idx on sbw_2009(issue);
create index sbw_2009_wfo_idx on sbw_2009(wfo);
grant select on sbw_2009 to apache,nobody;
    

CREATE table sbw_2010() inherits (sbw);
create index sbw_2010_idx on sbw_2010(wfo,eventid,significance,phenomena);
create index sbw_2010_expire_idx on sbw_2010(expire);
create index sbw_2010_issue_idx on sbw_2010(issue);
create index sbw_2010_wfo_idx on sbw_2010(wfo);
grant select on sbw_2010 to apache,nobody;
    

CREATE table sbw_2011() inherits (sbw);
create index sbw_2011_idx on sbw_2011(wfo,eventid,significance,phenomena);
create index sbw_2011_expire_idx on sbw_2011(expire);
create index sbw_2011_issue_idx on sbw_2011(issue);
create index sbw_2011_wfo_idx on sbw_2011(wfo);
grant select on sbw_2011 to apache,nobody;
    

CREATE table sbw_2012() inherits (sbw);
create index sbw_2012_idx on sbw_2012(wfo,eventid,significance,phenomena);
create index sbw_2012_expire_idx on sbw_2012(expire);
create index sbw_2012_issue_idx on sbw_2012(issue);
create index sbw_2012_wfo_idx on sbw_2012(wfo);
grant select on sbw_2012 to apache,nobody;
    

CREATE table sbw_2013() inherits (sbw);
create index sbw_2013_idx on sbw_2013(wfo,eventid,significance,phenomena);
create index sbw_2013_expire_idx on sbw_2013(expire);
create index sbw_2013_issue_idx on sbw_2013(issue);
create index sbw_2013_wfo_idx on sbw_2013(wfo);
grant select on sbw_2013 to apache,nobody;


CREATE table sbw_2014() inherits (sbw);
create index sbw_2014_idx on sbw_2014(wfo,eventid,significance,phenomena);
create index sbw_2014_expire_idx on sbw_2014(expire);
create index sbw_2014_issue_idx on sbw_2014(issue);
create index sbw_2014_wfo_idx on sbw_2014(wfo);
grant select on sbw_2014 to apache,nobody;


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
    typetext character varying(40)
) WITH OIDS;
select addgeometrycolumn('','lsrs','geom',4326,'POINT',2);
grant select on lsrs to apache,nobody;

create table lsrs_1986( 
  CONSTRAINT __lsrs_1986_check 
  CHECK(valid >= '1986-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_1986_valid_idx on lsrs_1986(valid);
CREATE INDEX lsrs_1986_wfo_idx on lsrs_1986(wfo);
GRANT SELECT on lsrs_1986 to nobody,apache;
    

create table lsrs_1987( 
  CONSTRAINT __lsrs_1987_check 
  CHECK(valid >= '1987-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_1987_valid_idx on lsrs_1987(valid);
CREATE INDEX lsrs_1987_wfo_idx on lsrs_1987(wfo);
GRANT SELECT on lsrs_1987 to nobody,apache;
    

create table lsrs_1988( 
  CONSTRAINT __lsrs_1988_check 
  CHECK(valid >= '1988-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_1988_valid_idx on lsrs_1988(valid);
CREATE INDEX lsrs_1988_wfo_idx on lsrs_1988(wfo);
GRANT SELECT on lsrs_1988 to nobody,apache;
    

create table lsrs_1989( 
  CONSTRAINT __lsrs_1989_check 
  CHECK(valid >= '1989-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_1989_valid_idx on lsrs_1989(valid);
CREATE INDEX lsrs_1989_wfo_idx on lsrs_1989(wfo);
GRANT SELECT on lsrs_1989 to nobody,apache;
    

create table lsrs_1990( 
  CONSTRAINT __lsrs_1990_check 
  CHECK(valid >= '1990-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_1990_valid_idx on lsrs_1990(valid);
CREATE INDEX lsrs_1990_wfo_idx on lsrs_1990(wfo);
GRANT SELECT on lsrs_1990 to nobody,apache;
    

create table lsrs_1991( 
  CONSTRAINT __lsrs_1991_check 
  CHECK(valid >= '1991-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_1991_valid_idx on lsrs_1991(valid);
CREATE INDEX lsrs_1991_wfo_idx on lsrs_1991(wfo);
GRANT SELECT on lsrs_1991 to nobody,apache;
    

create table lsrs_1992( 
  CONSTRAINT __lsrs_1992_check 
  CHECK(valid >= '1992-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_1992_valid_idx on lsrs_1992(valid);
CREATE INDEX lsrs_1992_wfo_idx on lsrs_1992(wfo);
GRANT SELECT on lsrs_1992 to nobody,apache;
    

create table lsrs_1993( 
  CONSTRAINT __lsrs_1993_check 
  CHECK(valid >= '1993-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_1993_valid_idx on lsrs_1993(valid);
CREATE INDEX lsrs_1993_wfo_idx on lsrs_1993(wfo);
GRANT SELECT on lsrs_1993 to nobody,apache;
    

create table lsrs_1994( 
  CONSTRAINT __lsrs_1994_check 
  CHECK(valid >= '1994-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_1994_valid_idx on lsrs_1994(valid);
CREATE INDEX lsrs_1994_wfo_idx on lsrs_1994(wfo);
GRANT SELECT on lsrs_1994 to nobody,apache;
    

create table lsrs_1995( 
  CONSTRAINT __lsrs_1995_check 
  CHECK(valid >= '1995-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_1995_valid_idx on lsrs_1995(valid);
CREATE INDEX lsrs_1995_wfo_idx on lsrs_1995(wfo);
GRANT SELECT on lsrs_1995 to nobody,apache;
    

create table lsrs_1996( 
  CONSTRAINT __lsrs_1996_check 
  CHECK(valid >= '1996-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_1996_valid_idx on lsrs_1996(valid);
CREATE INDEX lsrs_1996_wfo_idx on lsrs_1996(wfo);
GRANT SELECT on lsrs_1996 to nobody,apache;
    

create table lsrs_1997( 
  CONSTRAINT __lsrs_1997_check 
  CHECK(valid >= '1997-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_1997_valid_idx on lsrs_1997(valid);
CREATE INDEX lsrs_1997_wfo_idx on lsrs_1997(wfo);
GRANT SELECT on lsrs_1997 to nobody,apache;
    

create table lsrs_1998( 
  CONSTRAINT __lsrs_1998_check 
  CHECK(valid >= '1998-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_1998_valid_idx on lsrs_1998(valid);
CREATE INDEX lsrs_1998_wfo_idx on lsrs_1998(wfo);
GRANT SELECT on lsrs_1998 to nobody,apache;
    

create table lsrs_1999( 
  CONSTRAINT __lsrs_1999_check 
  CHECK(valid >= '1999-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_1999_valid_idx on lsrs_1999(valid);
CREATE INDEX lsrs_1999_wfo_idx on lsrs_1999(wfo);
GRANT SELECT on lsrs_1999 to nobody,apache;
    

create table lsrs_2000( 
  CONSTRAINT __lsrs_2000_check 
  CHECK(valid >= '2000-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2000_valid_idx on lsrs_2000(valid);
CREATE INDEX lsrs_2000_wfo_idx on lsrs_2000(wfo);
GRANT SELECT on lsrs_2000 to nobody,apache;
    

create table lsrs_2001( 
  CONSTRAINT __lsrs_2001_check 
  CHECK(valid >= '2001-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2001_valid_idx on lsrs_2001(valid);
CREATE INDEX lsrs_2001_wfo_idx on lsrs_2001(wfo);
GRANT SELECT on lsrs_2001 to nobody,apache;
    

create table lsrs_2002( 
  CONSTRAINT __lsrs_2002_check 
  CHECK(valid >= '2002-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2002_valid_idx on lsrs_2002(valid);
CREATE INDEX lsrs_2002_wfo_idx on lsrs_2002(wfo);
GRANT SELECT on lsrs_2002 to nobody,apache;
    

create table lsrs_2003( 
  CONSTRAINT __lsrs_2003_check 
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2003_valid_idx on lsrs_2003(valid);
CREATE INDEX lsrs_2003_wfo_idx on lsrs_2003(wfo);
GRANT SELECT on lsrs_2003 to nobody,apache;
    

create table lsrs_2004( 
  CONSTRAINT __lsrs_2004_check 
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2004_valid_idx on lsrs_2004(valid);
CREATE INDEX lsrs_2004_wfo_idx on lsrs_2004(wfo);
GRANT SELECT on lsrs_2004 to nobody,apache;
    

create table lsrs_2005( 
  CONSTRAINT __lsrs_2005_check 
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2005_valid_idx on lsrs_2005(valid);
CREATE INDEX lsrs_2005_wfo_idx on lsrs_2005(wfo);
GRANT SELECT on lsrs_2005 to nobody,apache;
    

create table lsrs_2006( 
  CONSTRAINT __lsrs_2006_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2006_valid_idx on lsrs_2006(valid);
CREATE INDEX lsrs_2006_wfo_idx on lsrs_2006(wfo);
GRANT SELECT on lsrs_2006 to nobody,apache;
    

create table lsrs_2007( 
  CONSTRAINT __lsrs_2007_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2007_valid_idx on lsrs_2007(valid);
CREATE INDEX lsrs_2007_wfo_idx on lsrs_2007(wfo);
GRANT SELECT on lsrs_2007 to nobody,apache;
    

create table lsrs_2008( 
  CONSTRAINT __lsrs_2008_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2008_valid_idx on lsrs_2008(valid);
CREATE INDEX lsrs_2008_wfo_idx on lsrs_2008(wfo);
GRANT SELECT on lsrs_2008 to nobody,apache;
    

create table lsrs_2009( 
  CONSTRAINT __lsrs_2009_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2009_valid_idx on lsrs_2009(valid);
CREATE INDEX lsrs_2009_wfo_idx on lsrs_2009(wfo);
GRANT SELECT on lsrs_2009 to nobody,apache;
    

create table lsrs_2010( 
  CONSTRAINT __lsrs_2010_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2010_valid_idx on lsrs_2010(valid);
CREATE INDEX lsrs_2010_wfo_idx on lsrs_2010(wfo);
GRANT SELECT on lsrs_2010 to nobody,apache;
    

create table lsrs_2011( 
  CONSTRAINT __lsrs_2011_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2011_valid_idx on lsrs_2011(valid);
CREATE INDEX lsrs_2011_wfo_idx on lsrs_2011(wfo);
GRANT SELECT on lsrs_2011 to nobody,apache;
    

create table lsrs_2012( 
  CONSTRAINT __lsrs_2012_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2012_valid_idx on lsrs_2012(valid);
CREATE INDEX lsrs_2012_wfo_idx on lsrs_2012(wfo);
GRANT SELECT on lsrs_2012 to nobody,apache;
    

create table lsrs_2013( 
  CONSTRAINT __lsrs_2013_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2013_valid_idx on lsrs_2013(valid);
CREATE INDEX lsrs_2013_wfo_idx on lsrs_2013(wfo);
GRANT SELECT on lsrs_2013 to nobody,apache;


create table lsrs_2014( 
  CONSTRAINT __lsrs_2014_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2014_valid_idx on lsrs_2014(valid);
CREATE INDEX lsrs_2014_wfo_idx on lsrs_2014(wfo);
GRANT SELECT on lsrs_2014 to nobody,apache;



---
--- HVTEC Table
---
CREATE TABLE hvtec_nwsli (
    nwsli character(5),
    river_name character varying(128),
    proximity character varying(16),
    name character varying(128),
    state character(2)
);

select addgeometrycolumn('','hvtec_nwsli','geom',4326,'POINT',2);
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
    fe_area character varying(2)
);

select addgeometrycolumn('','nws_ugc','geom',4326,'MULTIPOLYGON',2);
select addgeometrycolumn('','nws_ugc','centroid',4326,'POINT',2);
select addgeometrycolumn('','nws_ugc','simple_geom',4326,'MULTIPOLYGON',2);
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
    num smallint
);
select addgeometrycolumn('','watches','geom',4326,'MULTIPOLYGON',2);
grant select on watches to apache,nobody;

CREATE UNIQUE INDEX watches_idx ON watches USING btree (issued, num);

CREATE TABLE watches_current (
    sel character(5),
    issued timestamp with time zone,
    expired timestamp with time zone,
    type character(3),
    report text,
    num smallint
);
select addgeometrycolumn('','watches_current','geom',4326,'MULTIPOLYGON',2);
GRANT ALL on watches_current to mesonet,ldm;
grant select on watches_current to apache,nobody;

create table lsrs_2015( 
  CONSTRAINT __lsrs_2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2015_valid_idx on lsrs_2015(valid);
CREATE INDEX lsrs_2015_wfo_idx on lsrs_2015(wfo);
GRANT SELECT on lsrs_2015 to nobody,apache;


CREATE TABLE raob_profile_2015() inherits (raob_profile);
GRANT SELECT on raob_profile_2015 to nobody,apache;
CREATE INDEX raob_profile_2015_fid_idx 
	on raob_profile_2015(fid);

-- !!!!!!!!!!!!! WARNING !!!!!!!!!!!!
-- look what was done in 9.sql and replicate that for 2016 updates
CREATE TABLE warnings_2015() inherits (warnings);
CREATE INDEX warnings_2015_combo_idx on 
	warnings_2015(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2015_expire_idx on warnings_2015(expire);
CREATE INDEX warnings_2015_issue_idx on warnings_2015(issue);
CREATE INDEX warnings_2015_ugc_idx on warnings_2015(ugc);
CREATE INDEX warnings_2015_wfo_idx on warnings_2015(wfo);
grant select on warnings_2015 to nobody,apache;

CREATE table sbw_2015() inherits (sbw);
create index sbw_2015_idx on sbw_2015(wfo,eventid,significance,phenomena);
create index sbw_2015_expire_idx on sbw_2015(expire);
create index sbw_2015_issue_idx on sbw_2015(issue);
create index sbw_2015_wfo_idx on sbw_2015(wfo);
grant select on sbw_2015 to apache,nobody;

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

CREATE table sbw_1986() inherits (sbw);
create index sbw_1986_idx on sbw_1986(wfo,eventid,significance,phenomena);
create index sbw_1986_expire_idx on sbw_1986(expire);
create index sbw_1986_issue_idx on sbw_1986(issue);
create index sbw_1986_wfo_idx on sbw_1986(wfo);
grant select on sbw_1986 to apache,nobody;

CREATE table sbw_1987() inherits (sbw);
create index sbw_1987_idx on sbw_1987(wfo,eventid,significance,phenomena);
create index sbw_1987_expire_idx on sbw_1987(expire);
create index sbw_1987_issue_idx on sbw_1987(issue);
create index sbw_1987_wfo_idx on sbw_1987(wfo);
grant select on sbw_1987 to apache,nobody;

CREATE table sbw_1988() inherits (sbw);
create index sbw_1988_idx on sbw_1988(wfo,eventid,significance,phenomena);
create index sbw_1988_expire_idx on sbw_1988(expire);
create index sbw_1988_issue_idx on sbw_1988(issue);
create index sbw_1988_wfo_idx on sbw_1988(wfo);
grant select on sbw_1988 to apache,nobody;

CREATE table sbw_1989() inherits (sbw);
create index sbw_1989_idx on sbw_1989(wfo,eventid,significance,phenomena);
create index sbw_1989_expire_idx on sbw_1989(expire);
create index sbw_1989_issue_idx on sbw_1989(issue);
create index sbw_1989_wfo_idx on sbw_1989(wfo);
grant select on sbw_1989 to apache,nobody;

CREATE table sbw_1990() inherits (sbw);
create index sbw_1990_idx on sbw_1990(wfo,eventid,significance,phenomena);
create index sbw_1990_expire_idx on sbw_1990(expire);
create index sbw_1990_issue_idx on sbw_1990(issue);
create index sbw_1990_wfo_idx on sbw_1990(wfo);
grant select on sbw_1990 to apache,nobody;

CREATE table sbw_1991() inherits (sbw);
create index sbw_1991_idx on sbw_1991(wfo,eventid,significance,phenomena);
create index sbw_1991_expire_idx on sbw_1991(expire);
create index sbw_1991_issue_idx on sbw_1991(issue);
create index sbw_1991_wfo_idx on sbw_1991(wfo);
grant select on sbw_1991 to apache,nobody;

CREATE table sbw_1992() inherits (sbw);
create index sbw_1992_idx on sbw_1992(wfo,eventid,significance,phenomena);
create index sbw_1992_expire_idx on sbw_1992(expire);
create index sbw_1992_issue_idx on sbw_1992(issue);
create index sbw_1992_wfo_idx on sbw_1992(wfo);
grant select on sbw_1992 to apache,nobody;

CREATE table sbw_1993() inherits (sbw);
create index sbw_1993_idx on sbw_1993(wfo,eventid,significance,phenomena);
create index sbw_1993_expire_idx on sbw_1993(expire);
create index sbw_1993_issue_idx on sbw_1993(issue);
create index sbw_1993_wfo_idx on sbw_1993(wfo);
grant select on sbw_1993 to apache,nobody;

CREATE table sbw_1994() inherits (sbw);
create index sbw_1994_idx on sbw_1994(wfo,eventid,significance,phenomena);
create index sbw_1994_expire_idx on sbw_1994(expire);
create index sbw_1994_issue_idx on sbw_1994(issue);
create index sbw_1994_wfo_idx on sbw_1994(wfo);
grant select on sbw_1994 to apache,nobody;

CREATE table sbw_1995() inherits (sbw);
create index sbw_1995_idx on sbw_1995(wfo,eventid,significance,phenomena);
create index sbw_1995_expire_idx on sbw_1995(expire);
create index sbw_1995_issue_idx on sbw_1995(issue);
create index sbw_1995_wfo_idx on sbw_1995(wfo);
grant select on sbw_1995 to apache,nobody;

CREATE table sbw_1996() inherits (sbw);
create index sbw_1996_idx on sbw_1996(wfo,eventid,significance,phenomena);
create index sbw_1996_expire_idx on sbw_1996(expire);
create index sbw_1996_issue_idx on sbw_1996(issue);
create index sbw_1996_wfo_idx on sbw_1996(wfo);
grant select on sbw_1996 to apache,nobody;

CREATE table sbw_1997() inherits (sbw);
create index sbw_1997_idx on sbw_1997(wfo,eventid,significance,phenomena);
create index sbw_1997_expire_idx on sbw_1997(expire);
create index sbw_1997_issue_idx on sbw_1997(issue);
create index sbw_1997_wfo_idx on sbw_1997(wfo);
grant select on sbw_1997 to apache,nobody;

CREATE table sbw_1998() inherits (sbw);
create index sbw_1998_idx on sbw_1998(wfo,eventid,significance,phenomena);
create index sbw_1998_expire_idx on sbw_1998(expire);
create index sbw_1998_issue_idx on sbw_1998(issue);
create index sbw_1998_wfo_idx on sbw_1998(wfo);
grant select on sbw_1998 to apache,nobody;

CREATE table sbw_1999() inherits (sbw);
create index sbw_1999_idx on sbw_1999(wfo,eventid,significance,phenomena);
create index sbw_1999_expire_idx on sbw_1999(expire);
create index sbw_1999_issue_idx on sbw_1999(issue);
create index sbw_1999_wfo_idx on sbw_1999(wfo);
grant select on sbw_1999 to apache,nobody;

CREATE table sbw_2000() inherits (sbw);
create index sbw_2000_idx on sbw_2000(wfo,eventid,significance,phenomena);
create index sbw_2000_expire_idx on sbw_2000(expire);
create index sbw_2000_issue_idx on sbw_2000(issue);
create index sbw_2000_wfo_idx on sbw_2000(wfo);
grant select on sbw_2000 to apache,nobody;

CREATE table sbw_2001() inherits (sbw);
create index sbw_2001_idx on sbw_2001(wfo,eventid,significance,phenomena);
create index sbw_2001_expire_idx on sbw_2001(expire);
create index sbw_2001_issue_idx on sbw_2001(issue);
create index sbw_2001_wfo_idx on sbw_2001(wfo);
grant select on sbw_2001 to apache,nobody;

CREATE INDEX sbw_1986_gix ON sbw_1986 USING GIST (geom);
CREATE INDEX sbw_1987_gix ON sbw_1987 USING GIST (geom);
CREATE INDEX sbw_1988_gix ON sbw_1988 USING GIST (geom);
CREATE INDEX sbw_1989_gix ON sbw_1989 USING GIST (geom);
CREATE INDEX sbw_1990_gix ON sbw_1990 USING GIST (geom);
CREATE INDEX sbw_1991_gix ON sbw_1991 USING GIST (geom);
CREATE INDEX sbw_1992_gix ON sbw_1992 USING GIST (geom);
CREATE INDEX sbw_1993_gix ON sbw_1993 USING GIST (geom);
CREATE INDEX sbw_1994_gix ON sbw_1994 USING GIST (geom);
CREATE INDEX sbw_1995_gix ON sbw_1995 USING GIST (geom);
CREATE INDEX sbw_1996_gix ON sbw_1996 USING GIST (geom);
CREATE INDEX sbw_1997_gix ON sbw_1997 USING GIST (geom);
CREATE INDEX sbw_1998_gix ON sbw_1998 USING GIST (geom);
CREATE INDEX sbw_1999_gix ON sbw_1999 USING GIST (geom);
CREATE INDEX sbw_2000_gix ON sbw_2000 USING GIST (geom);
CREATE INDEX sbw_2001_gix ON sbw_2001 USING GIST (geom);
CREATE INDEX sbw_2002_gix ON sbw_2002 USING GIST (geom);
CREATE INDEX sbw_2003_gix ON sbw_2003 USING GIST (geom);
CREATE INDEX sbw_2004_gix ON sbw_2004 USING GIST (geom);
CREATE INDEX sbw_2005_gix ON sbw_2005 USING GIST (geom);
CREATE INDEX sbw_2006_gix ON sbw_2006 USING GIST (geom);
CREATE INDEX sbw_2007_gix ON sbw_2007 USING GIST (geom);
CREATE INDEX sbw_2008_gix ON sbw_2008 USING GIST (geom);
CREATE INDEX sbw_2009_gix ON sbw_2009 USING GIST (geom);
CREATE INDEX sbw_2010_gix ON sbw_2010 USING GIST (geom);
CREATE INDEX sbw_2011_gix ON sbw_2011 USING GIST (geom);
CREATE INDEX sbw_2012_gix ON sbw_2012 USING GIST (geom);
CREATE INDEX sbw_2013_gix ON sbw_2013 USING GIST (geom);
CREATE INDEX sbw_2014_gix ON sbw_2014 USING GIST (geom);
CREATE INDEX sbw_2015_gix ON sbw_2015 USING GIST (geom);

-- Add some proper constraints to keep database cleaner
alter table warnings_2015 ADD CONSTRAINT warnings_2015_gid_fkey
        FOREIGN KEY(gid) REFERENCES ugcs(gid);
alter table warnings_2015 ALTER WFO SET NOT NULL;
alter table warnings_2015 ALTER eventid SET NOT NULL;
alter table warnings_2015 ALTER status SET NOT NULL;
alter table warnings_2015 ALTER ugc SET NOT NULL;
alter table warnings_2015 ALTER phenomena SET NOT NULL;
alter table warnings_2015 ALTER significance SET NOT NULL;

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

create table lsrs_2016( 
  CONSTRAINT __lsrs_2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2016_valid_idx on lsrs_2016(valid);
CREATE INDEX lsrs_2016_wfo_idx on lsrs_2016(wfo);
GRANT SELECT on lsrs_2016 to nobody,apache;

CREATE TABLE raob_profile_2016() inherits (raob_profile);
GRANT SELECT on raob_profile_2016 to nobody,apache;
CREATE INDEX raob_profile_2016_fid_idx 
	on raob_profile_2016(fid);

-- !!!!!!!!!!!!! WARNING !!!!!!!!!!!!
-- look what was done in 9.sql and replicate that for 2017 updates
-- look at 15.sql too :(
CREATE TABLE warnings_2016() inherits (warnings);
CREATE INDEX warnings_2016_combo_idx on 
	warnings_2016(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2016_expire_idx on warnings_2016(expire);
CREATE INDEX warnings_2016_issue_idx on warnings_2016(issue);
CREATE INDEX warnings_2016_ugc_idx on warnings_2016(ugc);
CREATE INDEX warnings_2016_wfo_idx on warnings_2016(wfo);
-- Add some proper constraints to keep database cleaner
alter table warnings_2016 ADD CONSTRAINT warnings_2016_gid_fkey
        FOREIGN KEY(gid) REFERENCES ugcs(gid);
alter table warnings_2016 ALTER WFO SET NOT NULL;
alter table warnings_2016 ALTER eventid SET NOT NULL;
alter table warnings_2016 ALTER status SET NOT NULL;
alter table warnings_2016 ALTER ugc SET NOT NULL;
alter table warnings_2016 ALTER phenomena SET NOT NULL;
alter table warnings_2016 ALTER significance SET NOT NULL;
grant select on warnings_2016 to nobody,apache;

CREATE table sbw_2016() inherits (sbw);
create index sbw_2016_idx on sbw_2016(wfo,eventid,significance,phenomena);
create index sbw_2016_expire_idx on sbw_2016(expire);
create index sbw_2016_issue_idx on sbw_2016(issue);
create index sbw_2016_wfo_idx on sbw_2016(wfo);
CREATE INDEX sbw_2016_gix ON sbw_2016 USING GIST (geom);
grant select on sbw_2016 to apache,nobody;

CREATE INDEX warnings_1986_gid_idx on warnings_1986(gid);
CREATE INDEX warnings_1987_gid_idx on warnings_1987(gid);
CREATE INDEX warnings_1988_gid_idx on warnings_1988(gid);
CREATE INDEX warnings_1989_gid_idx on warnings_1989(gid);
CREATE INDEX warnings_1990_gid_idx on warnings_1990(gid);
CREATE INDEX warnings_1991_gid_idx on warnings_1991(gid);
CREATE INDEX warnings_1992_gid_idx on warnings_1992(gid);
CREATE INDEX warnings_1993_gid_idx on warnings_1993(gid);
CREATE INDEX warnings_1994_gid_idx on warnings_1994(gid);
CREATE INDEX warnings_1995_gid_idx on warnings_1995(gid);
CREATE INDEX warnings_1996_gid_idx on warnings_1996(gid);
CREATE INDEX warnings_1997_gid_idx on warnings_1997(gid);
CREATE INDEX warnings_1998_gid_idx on warnings_1998(gid);
CREATE INDEX warnings_1999_gid_idx on warnings_1999(gid);
CREATE INDEX warnings_2000_gid_idx on warnings_2000(gid);
CREATE INDEX warnings_2001_gid_idx on warnings_2001(gid);
CREATE INDEX warnings_2002_gid_idx on warnings_2002(gid);
CREATE INDEX warnings_2003_gid_idx on warnings_2003(gid);
CREATE INDEX warnings_2004_gid_idx on warnings_2004(gid);
CREATE INDEX warnings_2005_gid_idx on warnings_2005(gid);
CREATE INDEX warnings_2006_gid_idx on warnings_2006(gid);
CREATE INDEX warnings_2007_gid_idx on warnings_2007(gid);
CREATE INDEX warnings_2008_gid_idx on warnings_2008(gid);
CREATE INDEX warnings_2009_gid_idx on warnings_2009(gid);
CREATE INDEX warnings_2010_gid_idx on warnings_2010(gid);
CREATE INDEX warnings_2011_gid_idx on warnings_2011(gid);
CREATE INDEX warnings_2012_gid_idx on warnings_2012(gid);
CREATE INDEX warnings_2013_gid_idx on warnings_2013(gid);
CREATE INDEX warnings_2014_gid_idx on warnings_2014(gid);
CREATE INDEX warnings_2015_gid_idx on warnings_2015(gid);
CREATE INDEX warnings_2016_gid_idx on warnings_2016(gid);

create table lsrs_2017( 
  CONSTRAINT __lsrs_2017_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00'::timestamptz)) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2017_valid_idx on lsrs_2017(valid);
CREATE INDEX lsrs_2017_wfo_idx on lsrs_2017(wfo);
GRANT SELECT on lsrs_2017 to nobody,apache;

CREATE TABLE raob_profile_2017() inherits (raob_profile);
GRANT SELECT on raob_profile_2017 to nobody,apache;
CREATE INDEX raob_profile_2017_fid_idx 
	on raob_profile_2017(fid);

CREATE TABLE warnings_2017() inherits (warnings);
CREATE INDEX warnings_2017_combo_idx on 
	warnings_2017(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2017_expire_idx on warnings_2017(expire);
CREATE INDEX warnings_2017_issue_idx on warnings_2017(issue);
CREATE INDEX warnings_2017_ugc_idx on warnings_2017(ugc);
CREATE INDEX warnings_2017_wfo_idx on warnings_2017(wfo);
CREATE INDEX warnings_2017_gid_idx on warnings_2017(gid);
-- Add some proper constraints to keep database cleaner
alter table warnings_2017 ADD CONSTRAINT warnings_2017_gid_fkey
        FOREIGN KEY(gid) REFERENCES ugcs(gid);
alter table warnings_2017 ALTER WFO SET NOT NULL;
alter table warnings_2017 ALTER eventid SET NOT NULL;
alter table warnings_2017 ALTER status SET NOT NULL;
alter table warnings_2017 ALTER ugc SET NOT NULL;
alter table warnings_2017 ALTER phenomena SET NOT NULL;
alter table warnings_2017 ALTER significance SET NOT NULL;
grant select on warnings_2017 to nobody,apache;
GRANT ALL on warnings_2017 to mesonet,ldm;


CREATE table sbw_2017() inherits (sbw);
create index sbw_2017_idx on sbw_2017(wfo,eventid,significance,phenomena);
create index sbw_2017_expire_idx on sbw_2017(expire);
create index sbw_2017_issue_idx on sbw_2017(issue);
create index sbw_2017_wfo_idx on sbw_2017(wfo);
CREATE INDEX sbw_2017_gix ON sbw_2017 USING GIST (geom);
grant select on sbw_2017 to apache,nobody;

CREATE TABLE ffg(
  ugc char(6),
  valid timestamptz,
  hour01 real,
  hour03 real,
  hour06 real,
  hour12 real,
  hour24 real);
GRANT SELECT on ffg to nobody,apache;
GRANT ALL on ffg to ldm,mesonet;

CREATE TABLE ffg_2000(
  CONSTRAINT __ffg_2000_check 
  CHECK(valid >= '2000-01-01 00:00+00'::timestamptz
        and valid < '2001-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2000_ugc_idx on ffg_2000(ugc);
CREATE INDEX ffg_2000_valid_idx on ffg_2000(valid);
GRANT ALL on ffg_2000 to ldm,mesonet;
GRANT SELECT on ffg_2000 to nobody,apache;
    

CREATE TABLE ffg_2001(
  CONSTRAINT __ffg_2001_check 
  CHECK(valid >= '2001-01-01 00:00+00'::timestamptz
        and valid < '2002-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2001_ugc_idx on ffg_2001(ugc);
CREATE INDEX ffg_2001_valid_idx on ffg_2001(valid);
GRANT ALL on ffg_2001 to ldm,mesonet;
GRANT SELECT on ffg_2001 to nobody,apache;

CREATE TABLE ffg_2002(
  CONSTRAINT __ffg_2002_check 
  CHECK(valid >= '2002-01-01 00:00+00'::timestamptz
        and valid < '2003-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2002_ugc_idx on ffg_2002(ugc);
CREATE INDEX ffg_2002_valid_idx on ffg_2002(valid);
GRANT ALL on ffg_2002 to ldm,mesonet;
GRANT SELECT on ffg_2002 to nobody,apache;

CREATE TABLE ffg_2003(
  CONSTRAINT __ffg_2003_check 
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz
        and valid < '2004-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2003_ugc_idx on ffg_2003(ugc);
CREATE INDEX ffg_2003_valid_idx on ffg_2003(valid);
GRANT ALL on ffg_2003 to ldm,mesonet;
GRANT SELECT on ffg_2003 to nobody,apache;
    

CREATE TABLE ffg_2004(
  CONSTRAINT __ffg_2004_check 
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz
        and valid < '2005-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2004_ugc_idx on ffg_2004(ugc);
CREATE INDEX ffg_2004_valid_idx on ffg_2004(valid);
GRANT ALL on ffg_2004 to ldm,mesonet;
GRANT SELECT on ffg_2004 to nobody,apache;
    

CREATE TABLE ffg_2005(
  CONSTRAINT __ffg_2005_check 
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz
        and valid < '2006-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2005_ugc_idx on ffg_2005(ugc);
CREATE INDEX ffg_2005_valid_idx on ffg_2005(valid);
GRANT ALL on ffg_2005 to ldm,mesonet;
GRANT SELECT on ffg_2005 to nobody,apache;
    

CREATE TABLE ffg_2006(
  CONSTRAINT __ffg_2006_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz
        and valid < '2007-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2006_ugc_idx on ffg_2006(ugc);
CREATE INDEX ffg_2006_valid_idx on ffg_2006(valid);
GRANT ALL on ffg_2006 to ldm,mesonet;
GRANT SELECT on ffg_2006 to nobody,apache;
    

CREATE TABLE ffg_2007(
  CONSTRAINT __ffg_2007_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz
        and valid < '2008-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2007_ugc_idx on ffg_2007(ugc);
CREATE INDEX ffg_2007_valid_idx on ffg_2007(valid);
GRANT ALL on ffg_2007 to ldm,mesonet;
GRANT SELECT on ffg_2007 to nobody,apache;
    

CREATE TABLE ffg_2008(
  CONSTRAINT __ffg_2008_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz
        and valid < '2009-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2008_ugc_idx on ffg_2008(ugc);
CREATE INDEX ffg_2008_valid_idx on ffg_2008(valid);
GRANT ALL on ffg_2008 to ldm,mesonet;
GRANT SELECT on ffg_2008 to nobody,apache;
    

CREATE TABLE ffg_2009(
  CONSTRAINT __ffg_2009_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz
        and valid < '2010-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2009_ugc_idx on ffg_2009(ugc);
CREATE INDEX ffg_2009_valid_idx on ffg_2009(valid);
GRANT ALL on ffg_2009 to ldm,mesonet;
GRANT SELECT on ffg_2009 to nobody,apache;
    

CREATE TABLE ffg_2010(
  CONSTRAINT __ffg_2010_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz
        and valid < '2011-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2010_ugc_idx on ffg_2010(ugc);
CREATE INDEX ffg_2010_valid_idx on ffg_2010(valid);
GRANT ALL on ffg_2010 to ldm,mesonet;
GRANT SELECT on ffg_2010 to nobody,apache;
    

CREATE TABLE ffg_2011(
  CONSTRAINT __ffg_2011_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz
        and valid < '2012-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2011_ugc_idx on ffg_2011(ugc);
CREATE INDEX ffg_2011_valid_idx on ffg_2011(valid);
GRANT ALL on ffg_2011 to ldm,mesonet;
GRANT SELECT on ffg_2011 to nobody,apache;
    

CREATE TABLE ffg_2012(
  CONSTRAINT __ffg_2012_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz
        and valid < '2013-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2012_ugc_idx on ffg_2012(ugc);
CREATE INDEX ffg_2012_valid_idx on ffg_2012(valid);
GRANT ALL on ffg_2012 to ldm,mesonet;
GRANT SELECT on ffg_2012 to nobody,apache;
    

CREATE TABLE ffg_2013(
  CONSTRAINT __ffg_2013_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz
        and valid < '2014-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2013_ugc_idx on ffg_2013(ugc);
CREATE INDEX ffg_2013_valid_idx on ffg_2013(valid);
GRANT ALL on ffg_2013 to ldm,mesonet;
GRANT SELECT on ffg_2013 to nobody,apache;
    

CREATE TABLE ffg_2014(
  CONSTRAINT __ffg_2014_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz
        and valid < '2015-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2014_ugc_idx on ffg_2014(ugc);
CREATE INDEX ffg_2014_valid_idx on ffg_2014(valid);
GRANT ALL on ffg_2014 to ldm,mesonet;
GRANT SELECT on ffg_2014 to nobody,apache;
    

CREATE TABLE ffg_2015(
  CONSTRAINT __ffg_2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz
        and valid < '2016-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2015_ugc_idx on ffg_2015(ugc);
CREATE INDEX ffg_2015_valid_idx on ffg_2015(valid);
GRANT ALL on ffg_2015 to ldm,mesonet;
GRANT SELECT on ffg_2015 to nobody,apache;
    

CREATE TABLE ffg_2016(
  CONSTRAINT __ffg_2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz
        and valid < '2017-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2016_ugc_idx on ffg_2016(ugc);
CREATE INDEX ffg_2016_valid_idx on ffg_2016(valid);
GRANT ALL on ffg_2016 to ldm,mesonet;
GRANT SELECT on ffg_2016 to nobody,apache;
    

CREATE TABLE ffg_2017(
  CONSTRAINT __ffg_2017_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz
        and valid < '2018-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2017_ugc_idx on ffg_2017(ugc);
CREATE INDEX ffg_2017_valid_idx on ffg_2017(valid);
GRANT ALL on ffg_2017 to ldm,mesonet;
GRANT SELECT on ffg_2017 to nobody,apache;

-- Storage of USDM
CREATE TABLE usdm(
  valid date,
  dm smallint);
select addgeometrycolumn('', 'usdm', 'geom', 4326, 'MULTIPOLYGON', 2);
CREATE INDEX usdm_valid_idx on usdm(valid);
GRANT SELECT on usdm to nobody,apache;
GRANT ALL on usdm to mesonet,ldm;

CREATE TABLE ffg_2018(
  CONSTRAINT __ffg_2018_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2018_ugc_idx on ffg_2018(ugc);
CREATE INDEX ffg_2018_valid_idx on ffg_2018(valid);
GRANT ALL on ffg_2018 to ldm,mesonet;
GRANT SELECT on ffg_2018 to nobody,apache;

create table lsrs_2018( 
  CONSTRAINT __lsrs_2018_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz 
        and valid < '2019-01-01 00:00+00'::timestamptz)) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2018_valid_idx on lsrs_2018(valid);
CREATE INDEX lsrs_2018_wfo_idx on lsrs_2018(wfo);
GRANT SELECT on lsrs_2018 to nobody,apache;

CREATE TABLE raob_profile_2018() inherits (raob_profile);
GRANT SELECT on raob_profile_2018 to nobody,apache;
CREATE INDEX raob_profile_2018_fid_idx 
    on raob_profile_2018(fid);


CREATE TABLE warnings_2018() inherits (warnings);
CREATE INDEX warnings_2018_combo_idx on 
    warnings_2018(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2018_expire_idx on warnings_2018(expire);
CREATE INDEX warnings_2018_issue_idx on warnings_2018(issue);
CREATE INDEX warnings_2018_ugc_idx on warnings_2018(ugc);
CREATE INDEX warnings_2018_wfo_idx on warnings_2018(wfo);
CREATE INDEX warnings_2018_gid_idx on warnings_2018(gid);
-- Add some proper constraints to keep database cleaner
alter table warnings_2018 ADD CONSTRAINT warnings_2018_gid_fkey
        FOREIGN KEY(gid) REFERENCES ugcs(gid);
alter table warnings_2018 ALTER WFO SET NOT NULL;
alter table warnings_2018 ALTER eventid SET NOT NULL;
alter table warnings_2018 ALTER status SET NOT NULL;
alter table warnings_2018 ALTER ugc SET NOT NULL;
alter table warnings_2018 ALTER phenomena SET NOT NULL;
alter table warnings_2018 ALTER significance SET NOT NULL;
grant select on warnings_2018 to nobody,apache;
GRANT ALL on warnings_2018 to mesonet,ldm;


CREATE table sbw_2018() inherits (sbw);
create index sbw_2018_idx on sbw_2018(wfo,eventid,significance,phenomena);
create index sbw_2018_expire_idx on sbw_2018(expire);
create index sbw_2018_issue_idx on sbw_2018(issue);
create index sbw_2018_wfo_idx on sbw_2018(wfo);
CREATE INDEX sbw_2018_gix ON sbw_2018 USING GIST (geom);
grant select on sbw_2018 to apache,nobody;

CREATE TABLE ffg_2019(
  CONSTRAINT __ffg_2019_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2019_ugc_idx on ffg_2019(ugc);
CREATE INDEX ffg_2019_valid_idx on ffg_2019(valid);
GRANT ALL on ffg_2019 to ldm,mesonet;
GRANT SELECT on ffg_2019 to nobody,apache;

create table lsrs_2019( 
  CONSTRAINT __lsrs_2019_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz 
        and valid < '2020-01-01 00:00+00'::timestamptz)) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2019_valid_idx on lsrs_2019(valid);
CREATE INDEX lsrs_2019_wfo_idx on lsrs_2019(wfo);
GRANT SELECT on lsrs_2019 to nobody,apache;

CREATE TABLE raob_profile_2019() inherits (raob_profile);
GRANT SELECT on raob_profile_2019 to nobody,apache;
CREATE INDEX raob_profile_2019_fid_idx 
    on raob_profile_2019(fid);


CREATE TABLE warnings_2019() inherits (warnings);
CREATE INDEX warnings_2019_combo_idx on 
    warnings_2019(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2019_expire_idx on warnings_2019(expire);
CREATE INDEX warnings_2019_issue_idx on warnings_2019(issue);
CREATE INDEX warnings_2019_ugc_idx on warnings_2019(ugc);
CREATE INDEX warnings_2019_wfo_idx on warnings_2019(wfo);
CREATE INDEX warnings_2019_gid_idx on warnings_2019(gid);
-- Add some proper constraints to keep database cleaner
alter table warnings_2019 ADD CONSTRAINT warnings_2019_gid_fkey
        FOREIGN KEY(gid) REFERENCES ugcs(gid);
alter table warnings_2019 ALTER WFO SET NOT NULL;
alter table warnings_2019 ALTER eventid SET NOT NULL;
alter table warnings_2019 ALTER status SET NOT NULL;
alter table warnings_2019 ALTER ugc SET NOT NULL;
alter table warnings_2019 ALTER phenomena SET NOT NULL;
alter table warnings_2019 ALTER significance SET NOT NULL;
grant select on warnings_2019 to nobody,apache;
GRANT ALL on warnings_2019 to mesonet,ldm;


CREATE table sbw_2019() inherits (sbw);
create index sbw_2019_idx on sbw_2019(wfo,eventid,significance,phenomena);
create index sbw_2019_expire_idx on sbw_2019(expire);
create index sbw_2019_issue_idx on sbw_2019(issue);
create index sbw_2019_wfo_idx on sbw_2019(wfo);
CREATE INDEX sbw_2019_gix ON sbw_2019 USING GIST (geom);
grant select on sbw_2019 to apache,nobody;
