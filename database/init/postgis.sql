CREATE EXTENSION postgis;
---
--- TABLES THAT ARE LOADED VIA shp2pgsql
---   + cities
---   + climate_div
---   + counties
---   + cwa
---   + iacounties
---   + iowatorn
---   + placepoly
---   + states
---   + tz
---   + uscounties
---   + warnings_import

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
        iemid SERIAL UNIQUE,
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
        ncdc varchar(11)
);
CREATE UNIQUE index stations_idx on stations(id, network);
create index stations_iemid_idx on stations(iemid);
SELECT AddGeometryColumn('stations', 'geom', 4326, 'POINT', 2);
GRANT SELECT on stations to apache,nobody;
grant all on stations_iemid_seq to nobody,apache;


---
--- road conditions archive
---
CREATE TABLE roads_2004_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint
);
GRANT SELECT on roads_2004_log to nobody,apache;

CREATE TABLE roads_2005_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint
);
GRANT SELECT on roads_2005_log to nobody,apache;

CREATE TABLE roads_2006_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint
);
GRANT SELECT on roads_2006_log to nobody,apache;

CREATE TABLE roads_2007_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint,
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar
);
GRANT SELECT on roads_2007_log to nobody,apache;

CREATE TABLE roads_2008_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint,
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar
);
GRANT SELECT on roads_2008_log to nobody,apache;

CREATE TABLE roads_2009_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint,
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar
);
GRANT SELECT on roads_2009_log to nobody,apache;

CREATE TABLE roads_2010_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint,
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar
);
GRANT SELECT on roads_2010_log to nobody,apache;

CREATE TABLE roads_2011_log(
  segid smallint,
  valid timestamptz,
  cond_code smallint,
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar
);
GRANT SELECT on roads_2011_log to nobody,apache;



CREATE TABLE roads_2014_log(
  segid int,
  valid timestamptz,
  cond_code smallint,
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar);
GRANT SELECT on roads_2014_log to nobody,apache;

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
	end_ts timestamptz
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
CREATE OR REPLACE FUNCTION get_gid(text, timestamptz)
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

CREATE TABLE idot_snowplow_2013_2014(
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
	road_temp_code smallint
);
SELECT AddGeometryColumn('idot_snowplow_2013_2014', 'geom', 4326, 'POINT', 2);
CREATE INDEX idot_snowplow_2013_2014_label_idx on idot_snowplow_2013_2014(label);
CREATE INDEX idot_snowplow_2013_2014_valid_idx 
	on idot_snowplow_2013_2014(valid);
GRANT SELECT on idot_snowplow_2013_2014 to nobody,apache;

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
    release_time timestamptz -- Time of Release
);
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
GRANT select on vtec_missing_events to nobody,apache;

---
--- Text Products
---
CREATE TABLE text_products (
    reads smallint DEFAULT 0,
    product text,
    product_id character varying(32)
);
select addgeometrycolumn('','text_products','geom',4326,'MULTIPOLYGON',2);

grant select on text_products to apache;

create index text_products_idx 
  on text_products(product_id);

---
--- riverpro
---
CREATE TABLE riverpro (
    nwsli character varying(5),
    stage_text text,
    flood_text text,
    forecast_text text,
    severity character(1)
);

grant select on riverpro to apache;

CREATE UNIQUE INDEX riverpro_nwsli_idx ON riverpro USING btree (nwsli);

CREATE RULE replace_riverpro AS ON INSERT TO riverpro WHERE (EXISTS (SELECT 1 FROM riverpro WHERE ((riverpro.nwsli)::text = (new.nwsli)::text))) DO INSTEAD UPDATE riverpro SET stage_text = new.stage_text, flood_text = new.flood_text, forecast_text = new.forecast_text, severity = new.severity WHERE ((riverpro.nwsli)::text = (new.nwsli)::text);



---
--- VTEC Table
---
CREATE TABLE warnings (
    issue timestamp with time zone,
    expire timestamp with time zone,
    updated timestamp with time zone,
    type character(3),
    gtype character(1),
    wfo character(3),
    eventid smallint,
    status character(3),
    fips integer,
    fcster character varying(24),
    report text,
    svs text,
    ugc character varying(6),
    phenomena character(2),
    significance character(1),
    hvtec_nwsli character(5),
    gid int references ugcs(gid),
    init_expire timestamptz,
    product_issue timestamptz
) WITH OIDS;
select addgeometrycolumn('','warnings','geom',4326,'MULTIPOLYGON',2);

grant select on warnings to apache;

CREATE TABLE warnings_1986() inherits (warnings);
CREATE INDEX warnings_1986_combo_idx on 
	warnings_1986(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1986_expire_idx on warnings_1986(expire);
CREATE INDEX warnings_1986_gtype_idx on warnings_1986(gtype);
CREATE INDEX warnings_1986_issue_idx on warnings_1986(issue);
CREATE INDEX warnings_1986_ugc_idx on warnings_1986(ugc);
CREATE INDEX warnings_1986_wfo_idx on warnings_1986(wfo);
grant select on warnings_1986 to nobody,apache;
    

CREATE TABLE warnings_1987() inherits (warnings);
CREATE INDEX warnings_1987_combo_idx on 
	warnings_1987(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1987_expire_idx on warnings_1987(expire);
CREATE INDEX warnings_1987_gtype_idx on warnings_1987(gtype);
CREATE INDEX warnings_1987_issue_idx on warnings_1987(issue);
CREATE INDEX warnings_1987_ugc_idx on warnings_1987(ugc);
CREATE INDEX warnings_1987_wfo_idx on warnings_1987(wfo);
grant select on warnings_1987 to nobody,apache;
    

CREATE TABLE warnings_1988() inherits (warnings);
CREATE INDEX warnings_1988_combo_idx on 
	warnings_1988(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1988_expire_idx on warnings_1988(expire);
CREATE INDEX warnings_1988_gtype_idx on warnings_1988(gtype);
CREATE INDEX warnings_1988_issue_idx on warnings_1988(issue);
CREATE INDEX warnings_1988_ugc_idx on warnings_1988(ugc);
CREATE INDEX warnings_1988_wfo_idx on warnings_1988(wfo);
grant select on warnings_1988 to nobody,apache;
    

CREATE TABLE warnings_1989() inherits (warnings);
CREATE INDEX warnings_1989_combo_idx on 
	warnings_1989(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1989_expire_idx on warnings_1989(expire);
CREATE INDEX warnings_1989_gtype_idx on warnings_1989(gtype);
CREATE INDEX warnings_1989_issue_idx on warnings_1989(issue);
CREATE INDEX warnings_1989_ugc_idx on warnings_1989(ugc);
CREATE INDEX warnings_1989_wfo_idx on warnings_1989(wfo);
grant select on warnings_1989 to nobody,apache;
    

CREATE TABLE warnings_1990() inherits (warnings);
CREATE INDEX warnings_1990_combo_idx on 
	warnings_1990(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1990_expire_idx on warnings_1990(expire);
CREATE INDEX warnings_1990_gtype_idx on warnings_1990(gtype);
CREATE INDEX warnings_1990_issue_idx on warnings_1990(issue);
CREATE INDEX warnings_1990_ugc_idx on warnings_1990(ugc);
CREATE INDEX warnings_1990_wfo_idx on warnings_1990(wfo);
grant select on warnings_1990 to nobody,apache;
    

CREATE TABLE warnings_1991() inherits (warnings);
CREATE INDEX warnings_1991_combo_idx on 
	warnings_1991(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1991_expire_idx on warnings_1991(expire);
CREATE INDEX warnings_1991_gtype_idx on warnings_1991(gtype);
CREATE INDEX warnings_1991_issue_idx on warnings_1991(issue);
CREATE INDEX warnings_1991_ugc_idx on warnings_1991(ugc);
CREATE INDEX warnings_1991_wfo_idx on warnings_1991(wfo);
grant select on warnings_1991 to nobody,apache;
    

CREATE TABLE warnings_1992() inherits (warnings);
CREATE INDEX warnings_1992_combo_idx on 
	warnings_1992(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1992_expire_idx on warnings_1992(expire);
CREATE INDEX warnings_1992_gtype_idx on warnings_1992(gtype);
CREATE INDEX warnings_1992_issue_idx on warnings_1992(issue);
CREATE INDEX warnings_1992_ugc_idx on warnings_1992(ugc);
CREATE INDEX warnings_1992_wfo_idx on warnings_1992(wfo);
grant select on warnings_1992 to nobody,apache;
    

CREATE TABLE warnings_1993() inherits (warnings);
CREATE INDEX warnings_1993_combo_idx on 
	warnings_1993(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1993_expire_idx on warnings_1993(expire);
CREATE INDEX warnings_1993_gtype_idx on warnings_1993(gtype);
CREATE INDEX warnings_1993_issue_idx on warnings_1993(issue);
CREATE INDEX warnings_1993_ugc_idx on warnings_1993(ugc);
CREATE INDEX warnings_1993_wfo_idx on warnings_1993(wfo);
grant select on warnings_1993 to nobody,apache;
    

CREATE TABLE warnings_1994() inherits (warnings);
CREATE INDEX warnings_1994_combo_idx on 
	warnings_1994(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1994_expire_idx on warnings_1994(expire);
CREATE INDEX warnings_1994_gtype_idx on warnings_1994(gtype);
CREATE INDEX warnings_1994_issue_idx on warnings_1994(issue);
CREATE INDEX warnings_1994_ugc_idx on warnings_1994(ugc);
CREATE INDEX warnings_1994_wfo_idx on warnings_1994(wfo);
grant select on warnings_1994 to nobody,apache;
    

CREATE TABLE warnings_1995() inherits (warnings);
CREATE INDEX warnings_1995_combo_idx on 
	warnings_1995(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1995_expire_idx on warnings_1995(expire);
CREATE INDEX warnings_1995_gtype_idx on warnings_1995(gtype);
CREATE INDEX warnings_1995_issue_idx on warnings_1995(issue);
CREATE INDEX warnings_1995_ugc_idx on warnings_1995(ugc);
CREATE INDEX warnings_1995_wfo_idx on warnings_1995(wfo);
grant select on warnings_1995 to nobody,apache;
    

CREATE TABLE warnings_1996() inherits (warnings);
CREATE INDEX warnings_1996_combo_idx on 
	warnings_1996(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1996_expire_idx on warnings_1996(expire);
CREATE INDEX warnings_1996_gtype_idx on warnings_1996(gtype);
CREATE INDEX warnings_1996_issue_idx on warnings_1996(issue);
CREATE INDEX warnings_1996_ugc_idx on warnings_1996(ugc);
CREATE INDEX warnings_1996_wfo_idx on warnings_1996(wfo);
grant select on warnings_1996 to nobody,apache;
    

CREATE TABLE warnings_1997() inherits (warnings);
CREATE INDEX warnings_1997_combo_idx on 
	warnings_1997(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1997_expire_idx on warnings_1997(expire);
CREATE INDEX warnings_1997_gtype_idx on warnings_1997(gtype);
CREATE INDEX warnings_1997_issue_idx on warnings_1997(issue);
CREATE INDEX warnings_1997_ugc_idx on warnings_1997(ugc);
CREATE INDEX warnings_1997_wfo_idx on warnings_1997(wfo);
grant select on warnings_1997 to nobody,apache;
    

CREATE TABLE warnings_1998() inherits (warnings);
CREATE INDEX warnings_1998_combo_idx on 
	warnings_1998(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1998_expire_idx on warnings_1998(expire);
CREATE INDEX warnings_1998_gtype_idx on warnings_1998(gtype);
CREATE INDEX warnings_1998_issue_idx on warnings_1998(issue);
CREATE INDEX warnings_1998_ugc_idx on warnings_1998(ugc);
CREATE INDEX warnings_1998_wfo_idx on warnings_1998(wfo);
grant select on warnings_1998 to nobody,apache;
    

CREATE TABLE warnings_1999() inherits (warnings);
CREATE INDEX warnings_1999_combo_idx on 
	warnings_1999(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_1999_expire_idx on warnings_1999(expire);
CREATE INDEX warnings_1999_gtype_idx on warnings_1999(gtype);
CREATE INDEX warnings_1999_issue_idx on warnings_1999(issue);
CREATE INDEX warnings_1999_ugc_idx on warnings_1999(ugc);
CREATE INDEX warnings_1999_wfo_idx on warnings_1999(wfo);
grant select on warnings_1999 to nobody,apache;
    

CREATE TABLE warnings_2000() inherits (warnings);
CREATE INDEX warnings_2000_combo_idx on 
	warnings_2000(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2000_expire_idx on warnings_2000(expire);
CREATE INDEX warnings_2000_gtype_idx on warnings_2000(gtype);
CREATE INDEX warnings_2000_issue_idx on warnings_2000(issue);
CREATE INDEX warnings_2000_ugc_idx on warnings_2000(ugc);
CREATE INDEX warnings_2000_wfo_idx on warnings_2000(wfo);
grant select on warnings_2000 to nobody,apache;
    

CREATE TABLE warnings_2001() inherits (warnings);
CREATE INDEX warnings_2001_combo_idx on 
	warnings_2001(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2001_expire_idx on warnings_2001(expire);
CREATE INDEX warnings_2001_gtype_idx on warnings_2001(gtype);
CREATE INDEX warnings_2001_issue_idx on warnings_2001(issue);
CREATE INDEX warnings_2001_ugc_idx on warnings_2001(ugc);
CREATE INDEX warnings_2001_wfo_idx on warnings_2001(wfo);
grant select on warnings_2001 to nobody,apache;
    

CREATE TABLE warnings_2002() inherits (warnings);
CREATE INDEX warnings_2002_combo_idx on 
	warnings_2002(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2002_expire_idx on warnings_2002(expire);
CREATE INDEX warnings_2002_gtype_idx on warnings_2002(gtype);
CREATE INDEX warnings_2002_issue_idx on warnings_2002(issue);
CREATE INDEX warnings_2002_ugc_idx on warnings_2002(ugc);
CREATE INDEX warnings_2002_wfo_idx on warnings_2002(wfo);
grant select on warnings_2002 to nobody,apache;
    

CREATE TABLE warnings_2003() inherits (warnings);
CREATE INDEX warnings_2003_combo_idx on 
	warnings_2003(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2003_expire_idx on warnings_2003(expire);
CREATE INDEX warnings_2003_gtype_idx on warnings_2003(gtype);
CREATE INDEX warnings_2003_issue_idx on warnings_2003(issue);
CREATE INDEX warnings_2003_ugc_idx on warnings_2003(ugc);
CREATE INDEX warnings_2003_wfo_idx on warnings_2003(wfo);
grant select on warnings_2003 to nobody,apache;
    

CREATE TABLE warnings_2004() inherits (warnings);
CREATE INDEX warnings_2004_combo_idx on 
	warnings_2004(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2004_expire_idx on warnings_2004(expire);
CREATE INDEX warnings_2004_gtype_idx on warnings_2004(gtype);
CREATE INDEX warnings_2004_issue_idx on warnings_2004(issue);
CREATE INDEX warnings_2004_ugc_idx on warnings_2004(ugc);
CREATE INDEX warnings_2004_wfo_idx on warnings_2004(wfo);
grant select on warnings_2004 to nobody,apache;
    

CREATE TABLE warnings_2005() inherits (warnings);
CREATE INDEX warnings_2005_combo_idx on 
	warnings_2005(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2005_expire_idx on warnings_2005(expire);
CREATE INDEX warnings_2005_gtype_idx on warnings_2005(gtype);
CREATE INDEX warnings_2005_issue_idx on warnings_2005(issue);
CREATE INDEX warnings_2005_ugc_idx on warnings_2005(ugc);
CREATE INDEX warnings_2005_wfo_idx on warnings_2005(wfo);
grant select on warnings_2005 to nobody,apache;
    

CREATE TABLE warnings_2006() inherits (warnings);
CREATE INDEX warnings_2006_combo_idx on 
	warnings_2006(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2006_expire_idx on warnings_2006(expire);
CREATE INDEX warnings_2006_gtype_idx on warnings_2006(gtype);
CREATE INDEX warnings_2006_issue_idx on warnings_2006(issue);
CREATE INDEX warnings_2006_ugc_idx on warnings_2006(ugc);
CREATE INDEX warnings_2006_wfo_idx on warnings_2006(wfo);
grant select on warnings_2006 to nobody,apache;
    

CREATE TABLE warnings_2007() inherits (warnings);
CREATE INDEX warnings_2007_combo_idx on 
	warnings_2007(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2007_expire_idx on warnings_2007(expire);
CREATE INDEX warnings_2007_gtype_idx on warnings_2007(gtype);
CREATE INDEX warnings_2007_issue_idx on warnings_2007(issue);
CREATE INDEX warnings_2007_ugc_idx on warnings_2007(ugc);
CREATE INDEX warnings_2007_wfo_idx on warnings_2007(wfo);
grant select on warnings_2007 to nobody,apache;
    

CREATE TABLE warnings_2008() inherits (warnings);
CREATE INDEX warnings_2008_combo_idx on 
	warnings_2008(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2008_expire_idx on warnings_2008(expire);
CREATE INDEX warnings_2008_gtype_idx on warnings_2008(gtype);
CREATE INDEX warnings_2008_issue_idx on warnings_2008(issue);
CREATE INDEX warnings_2008_ugc_idx on warnings_2008(ugc);
CREATE INDEX warnings_2008_wfo_idx on warnings_2008(wfo);
grant select on warnings_2008 to nobody,apache;
    

CREATE TABLE warnings_2009() inherits (warnings);
CREATE INDEX warnings_2009_combo_idx on 
	warnings_2009(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2009_expire_idx on warnings_2009(expire);
CREATE INDEX warnings_2009_gtype_idx on warnings_2009(gtype);
CREATE INDEX warnings_2009_issue_idx on warnings_2009(issue);
CREATE INDEX warnings_2009_ugc_idx on warnings_2009(ugc);
CREATE INDEX warnings_2009_wfo_idx on warnings_2009(wfo);
grant select on warnings_2009 to nobody,apache;
    

CREATE TABLE warnings_2010() inherits (warnings);
CREATE INDEX warnings_2010_combo_idx on 
	warnings_2010(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2010_expire_idx on warnings_2010(expire);
CREATE INDEX warnings_2010_gtype_idx on warnings_2010(gtype);
CREATE INDEX warnings_2010_issue_idx on warnings_2010(issue);
CREATE INDEX warnings_2010_ugc_idx on warnings_2010(ugc);
CREATE INDEX warnings_2010_wfo_idx on warnings_2010(wfo);
grant select on warnings_2010 to nobody,apache;
    

CREATE TABLE warnings_2011() inherits (warnings);
CREATE INDEX warnings_2011_combo_idx on 
	warnings_2011(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2011_expire_idx on warnings_2011(expire);
CREATE INDEX warnings_2011_gtype_idx on warnings_2011(gtype);
CREATE INDEX warnings_2011_issue_idx on warnings_2011(issue);
CREATE INDEX warnings_2011_ugc_idx on warnings_2011(ugc);
CREATE INDEX warnings_2011_wfo_idx on warnings_2011(wfo);
grant select on warnings_2011 to nobody,apache;
    

CREATE TABLE warnings_2012() inherits (warnings);
CREATE INDEX warnings_2012_combo_idx on 
	warnings_2012(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2012_expire_idx on warnings_2012(expire);
CREATE INDEX warnings_2012_gtype_idx on warnings_2012(gtype);
CREATE INDEX warnings_2012_issue_idx on warnings_2012(issue);
CREATE INDEX warnings_2012_ugc_idx on warnings_2012(ugc);
CREATE INDEX warnings_2012_wfo_idx on warnings_2012(wfo);
grant select on warnings_2012 to nobody,apache;
    

CREATE TABLE warnings_2013() inherits (warnings);
CREATE INDEX warnings_2013_combo_idx on 
	warnings_2013(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2013_expire_idx on warnings_2013(expire);
CREATE INDEX warnings_2013_gtype_idx on warnings_2013(gtype);
CREATE INDEX warnings_2013_issue_idx on warnings_2013(issue);
CREATE INDEX warnings_2013_ugc_idx on warnings_2013(ugc);
CREATE INDEX warnings_2013_wfo_idx on warnings_2013(wfo);
grant select on warnings_2013 to nobody,apache;


CREATE TABLE warnings_2014() inherits (warnings);
CREATE INDEX warnings_2014_combo_idx on 
	warnings_2014(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2014_expire_idx on warnings_2014(expire);
CREATE INDEX warnings_2014_gtype_idx on warnings_2014(gtype);
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
  tml_valid timestamp with time zone,
  tml_direction smallint,
  tml_sknt smallint,
  updated timestamptz
) WITH OIDS;
select addgeometrycolumn('','sbw','geom',4326,'MULTIPOLYGON',2);
select addGeometryColumn('sbw', 'tml_geom', 4326, 'POINT', 2);
select addGeometryColumn('sbw', 'tml_geom_line', 4326, 'LINESTRING', 2);

grant select on sbw to apache;

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
grant select on hvtec_nwsli to apache;

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


CREATE table roads_base_2005(
	segid int,
	major varchar(10),
	minor varchar(128),
	us1 smallint,
	st1 smallint,
	int1 smallint,
	type smallint
);
SELECT AddGeometryColumn('roads_base_2005', 'geom', 26915, 'MULTILINESTRING', 2);

CREATE table roads_base_2006(
	segid int,
	major varchar(10),
	minor varchar(128),
	us1 smallint,
	st1 smallint,
	int1 smallint,
	type smallint,
	wfo char(3)
);
SELECT AddGeometryColumn('roads_base_2006', 'geom', 26915, 'MULTILINESTRING', 2);

CREATE table roads_base_2009(
	segid int,
	major varchar(10),
	minor varchar(128),
	us1 smallint,
	st1 smallint,
	int1 smallint,
	type smallint,
	wfo char(3),
	tempval numeric
);
SELECT AddGeometryColumn('roads_base_2009', 'geom', 26915, 'MULTILINESTRING', 2);

CREATE table roads_base_2010(
	segid int,
	major varchar(10),
	minor varchar(128),
	us1 smallint,
	st1 smallint,
	int1 smallint,
	type smallint,
	wfo char(3),
	tempval numeric
);
SELECT AddGeometryColumn('roads_base_2010', 'geom', 26915, 'MULTILINESTRING', 2);

CREATE table roads_base_2011(
	segid int,
	major varchar(10),
	minor varchar(128),
	us1 smallint,
	st1 smallint,
	int1 smallint,
	type smallint,
	wfo char(3),
	tempval numeric
);
SELECT AddGeometryColumn('roads_base_2011', 'geom', 26915, 'MULTILINESTRING', 2);

CREATE table roads_base_2013(
	segid int,
	major varchar(10),
	minor varchar(128),
	us1 smallint,
	st1 smallint,
	int1 smallint,
	type smallint,
	wfo char(3),
	tempval numeric,
	longname varchar(256)
);
SELECT AddGeometryColumn('roads_base_2013', 'geom', 26915, 'MULTILINESTRING', 2);



---
---
---
CREATE table roads_base(
	segid SERIAL unique,
	major varchar(10),
	minor varchar(128),
	us1 smallint,
	st1 smallint,
	int1 smallint,
	type smallint,
	wfo char(3),
	tempval numeric,
	longname varchar(256));

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



CREATE view roads_view as 
SELECT b.segid,
    b.major,
    b.minor,
    b.us1,
    b.st1,
    b.int1,
    b.type,
    b.geom::geometry(MultiLineString,26915) AS geom,
    b.longname,
    c.valid,
    c.towing_prohibited,
    c.cond_code,
    d.label
   FROM roads_base b,
    roads_current c,
    roads_conditions d
  WHERE c.segid = b.segid AND c.cond_code = d.code AND (b.segid <> ALL (ARRAY[2404, 2990]));

CREATE TABLE roads_2012_log(
  segid int REFERENCES roads_base(segid),
  valid timestamptz,
  cond_code smallint REFERENCES roads_conditions(code),
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar);
GRANT SELECT on roads_2012_log to nobody,apache;

CREATE TABLE roads_2013_log(
  segid int REFERENCES roads_base(segid),
  valid timestamptz,
  cond_code smallint REFERENCES roads_conditions(code),
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar);
GRANT SELECT on roads_2013_log to nobody,apache;






---
--- SPC Convective Outlooks (created: 22 Oct 2010)
---
CREATE TABLE spc_outlooks (
  issue timestamp with time zone,
  valid timestamp with time zone,
  expire timestamp with time zone,
  threshold varchar(4),
  category varchar(64),
  day smallint,
  outlook_type char(1)
);
SELECT addGeometryColumn('', 'spc_outlooks', 'geom', 4326, 'MULTIPOLYGON', 2);
GRANT SELECT on spc_outlooks to apache,nobody;
CREATE index spc_outlooks_valid_idx on spc_outlooks(valid);

---
--- NEXRAD Attributes
---
CREATE TABLE nexrad_attributes(
	nexrad character(3),   
 storm_id  character(2),     
 azimuth  smallint,
 range    smallint,
 tvs        character varying(10),
 meso       character varying(10),
 posh smallint,
 poh         smallint,
 max_size    real,
 vil      smallint,
 max_dbz       smallint,
 max_dbz_height real,
 top         real,
 drct      smallint,
 sknt      smallint,
 valid    timestamp with time zone
 );
SELECT addGeometryColumn('', 'nexrad_attributes', 'geom', 4326, 'POINT', 2);
GRANT SELECT on nexrad_attributes to apache,nobody;

---
--- NEXRAD Attributes
---
CREATE TABLE nexrad_attributes_log(
	nexrad character(3),   
 storm_id  character(2),     
 azimuth  smallint,
 range    smallint,
 tvs        character varying(10),
 meso       character varying(10),
 posh smallint,
 poh         smallint,
 max_size    real,
 vil      smallint,
 max_dbz       smallint,
 max_dbz_height real,
 top         real,
 drct      smallint,
 sknt      smallint,
 valid    timestamp with time zone
 );
SELECT addGeometryColumn('', 'nexrad_attributes_log', 'geom', 4326, 'POINT', 2);
GRANT SELECT on nexrad_attributes to apache,nobody;

CREATE TABLE nexrad_attributes_2000() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2000 to nobody,apache;
CREATE INDEX nexrad_attributes_2000_nexrad_idx 
	on nexrad_attributes_2000(nexrad);
CREATE INDEX nexrad_attributes_2000_valid_idx 
	on nexrad_attributes_2000(valid);
alter table nexrad_attributes_2000 add constraint 
	__nexrad_attributes_2000__constraint CHECK 
	(valid >= '2000-01-01 00:00+00' and valid < '2001-01-01 00:00+00');
    

CREATE TABLE nexrad_attributes_2001() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2001 to nobody,apache;
CREATE INDEX nexrad_attributes_2001_nexrad_idx 
	on nexrad_attributes_2001(nexrad);
CREATE INDEX nexrad_attributes_2001_valid_idx 
	on nexrad_attributes_2001(valid);
alter table nexrad_attributes_2001 add constraint 
	__nexrad_attributes_2001__constraint CHECK 
	(valid >= '2001-01-01 00:00+00' and valid < '2002-01-01 00:00+00');
    

CREATE TABLE nexrad_attributes_2002() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2002 to nobody,apache;
CREATE INDEX nexrad_attributes_2002_nexrad_idx 
	on nexrad_attributes_2002(nexrad);
CREATE INDEX nexrad_attributes_2002_valid_idx 
	on nexrad_attributes_2002(valid);
alter table nexrad_attributes_2002 add constraint 
	__nexrad_attributes_2002__constraint CHECK 
	(valid >= '2002-01-01 00:00+00' and valid < '2003-01-01 00:00+00');
    

CREATE TABLE nexrad_attributes_2003() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2003 to nobody,apache;
CREATE INDEX nexrad_attributes_2003_nexrad_idx 
	on nexrad_attributes_2003(nexrad);
CREATE INDEX nexrad_attributes_2003_valid_idx 
	on nexrad_attributes_2003(valid);
alter table nexrad_attributes_2003 add constraint 
	__nexrad_attributes_2003__constraint CHECK 
	(valid >= '2003-01-01 00:00+00' and valid < '2004-01-01 00:00+00');
    

CREATE TABLE nexrad_attributes_2004() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2004 to nobody,apache;
CREATE INDEX nexrad_attributes_2004_nexrad_idx 
	on nexrad_attributes_2004(nexrad);
CREATE INDEX nexrad_attributes_2004_valid_idx 
	on nexrad_attributes_2004(valid);
alter table nexrad_attributes_2004 add constraint 
	__nexrad_attributes_2004__constraint CHECK 
	(valid >= '2004-01-01 00:00+00' and valid < '2005-01-01 00:00+00');
    

CREATE TABLE nexrad_attributes_2005() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2005 to nobody,apache;
CREATE INDEX nexrad_attributes_2005_nexrad_idx 
	on nexrad_attributes_2005(nexrad);
CREATE INDEX nexrad_attributes_2005_valid_idx 
	on nexrad_attributes_2005(valid);
alter table nexrad_attributes_2005 add constraint 
	__nexrad_attributes_2005__constraint CHECK 
	(valid >= '2005-01-01 00:00+00' and valid < '2006-01-01 00:00+00');
    

CREATE TABLE nexrad_attributes_2006() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2006 to nobody,apache;
CREATE INDEX nexrad_attributes_2006_nexrad_idx 
	on nexrad_attributes_2006(nexrad);
CREATE INDEX nexrad_attributes_2006_valid_idx 
	on nexrad_attributes_2006(valid);
alter table nexrad_attributes_2006 add constraint 
	__nexrad_attributes_2006__constraint CHECK 
	(valid >= '2006-01-01 00:00+00' and valid < '2007-01-01 00:00+00');
    

CREATE TABLE nexrad_attributes_2007() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2007 to nobody,apache;
CREATE INDEX nexrad_attributes_2007_nexrad_idx 
	on nexrad_attributes_2007(nexrad);
CREATE INDEX nexrad_attributes_2007_valid_idx 
	on nexrad_attributes_2007(valid);
alter table nexrad_attributes_2007 add constraint 
	__nexrad_attributes_2007__constraint CHECK 
	(valid >= '2007-01-01 00:00+00' and valid < '2008-01-01 00:00+00');
    

CREATE TABLE nexrad_attributes_2008() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2008 to nobody,apache;
CREATE INDEX nexrad_attributes_2008_nexrad_idx 
	on nexrad_attributes_2008(nexrad);
CREATE INDEX nexrad_attributes_2008_valid_idx 
	on nexrad_attributes_2008(valid);
alter table nexrad_attributes_2008 add constraint 
	__nexrad_attributes_2008__constraint CHECK 
	(valid >= '2008-01-01 00:00+00' and valid < '2009-01-01 00:00+00');
    

CREATE TABLE nexrad_attributes_2009() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2009 to nobody,apache;
CREATE INDEX nexrad_attributes_2009_nexrad_idx 
	on nexrad_attributes_2009(nexrad);
CREATE INDEX nexrad_attributes_2009_valid_idx 
	on nexrad_attributes_2009(valid);
alter table nexrad_attributes_2009 add constraint 
	__nexrad_attributes_2009__constraint CHECK 
	(valid >= '2009-01-01 00:00+00' and valid < '2010-01-01 00:00+00');
    

CREATE TABLE nexrad_attributes_2010() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2010 to nobody,apache;
CREATE INDEX nexrad_attributes_2010_nexrad_idx 
	on nexrad_attributes_2010(nexrad);
CREATE INDEX nexrad_attributes_2010_valid_idx 
	on nexrad_attributes_2010(valid);
alter table nexrad_attributes_2010 add constraint 
	__nexrad_attributes_2010__constraint CHECK 
	(valid >= '2010-01-01 00:00+00' and valid < '2011-01-01 00:00+00');
    

CREATE TABLE nexrad_attributes_2011() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2011 to nobody,apache;
CREATE INDEX nexrad_attributes_2011_nexrad_idx 
	on nexrad_attributes_2011(nexrad);
CREATE INDEX nexrad_attributes_2011_valid_idx 
	on nexrad_attributes_2011(valid);
alter table nexrad_attributes_2011 add constraint 
	__nexrad_attributes_2011__constraint CHECK 
	(valid >= '2011-01-01 00:00+00' and valid < '2012-01-01 00:00+00');
    

CREATE TABLE nexrad_attributes_2012() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2012 to nobody,apache;
CREATE INDEX nexrad_attributes_2012_nexrad_idx 
	on nexrad_attributes_2012(nexrad);
CREATE INDEX nexrad_attributes_2012_valid_idx 
	on nexrad_attributes_2012(valid);
alter table nexrad_attributes_2012 add constraint 
	__nexrad_attributes_2012__constraint CHECK 
	(valid >= '2012-01-01 00:00+00' and valid < '2013-01-01 00:00+00');
    

CREATE TABLE nexrad_attributes_2013() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2013 to nobody,apache;
CREATE INDEX nexrad_attributes_2013_nexrad_idx 
	on nexrad_attributes_2013(nexrad);
CREATE INDEX nexrad_attributes_2013_valid_idx 
	on nexrad_attributes_2013(valid);
alter table nexrad_attributes_2013 add constraint 
	__nexrad_attributes_2013__constraint CHECK 
	(valid >= '2013-01-01 00:00+00' and valid < '2014-01-01 00:00+00');

CREATE TABLE nexrad_attributes_2014() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2014 to nobody,apache;
CREATE INDEX nexrad_attributes_2014_nexrad_idx 
	on nexrad_attributes_2014(nexrad);
CREATE INDEX nexrad_attributes_2014_valid_idx 
	on nexrad_attributes_2014(valid);
alter table nexrad_attributes_2014 add constraint 
	__nexrad_attributes_2014__constraint CHECK 
	(valid >= '2014-01-01 00:00+00' and valid < '2015-01-01 00:00+00');

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
grant select on watches to apache,nobody;
