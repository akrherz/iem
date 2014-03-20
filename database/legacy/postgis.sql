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


CREATE AGGREGATE sumtxt(text) (
    SFUNC = textcat,
    STYPE = text,
    INITCOND = ''
);


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
CREATE TABLE raob_profile_1990() inherits (raob_profile);
CREATE TABLE raob_profile_1991() inherits (raob_profile);
CREATE TABLE raob_profile_1992() inherits (raob_profile);
CREATE TABLE raob_profile_1993() inherits (raob_profile);
CREATE TABLE raob_profile_1994() inherits (raob_profile);
CREATE TABLE raob_profile_1995() inherits (raob_profile);
CREATE TABLE raob_profile_1996() inherits (raob_profile);
CREATE TABLE raob_profile_1997() inherits (raob_profile);
CREATE TABLE raob_profile_1998() inherits (raob_profile);
CREATE TABLE raob_profile_1999() inherits (raob_profile);
CREATE TABLE raob_profile_2000() inherits (raob_profile);
CREATE TABLE raob_profile_2001() inherits (raob_profile);
CREATE TABLE raob_profile_2002() inherits (raob_profile);
CREATE TABLE raob_profile_2003() inherits (raob_profile);
CREATE TABLE raob_profile_2004() inherits (raob_profile);
CREATE TABLE raob_profile_2005() inherits (raob_profile);
CREATE TABLE raob_profile_2006() inherits (raob_profile);
CREATE TABLE raob_profile_2007() inherits (raob_profile);
CREATE TABLE raob_profile_2008() inherits (raob_profile);
CREATE TABLE raob_profile_2009() inherits (raob_profile);
CREATE TABLE raob_profile_2010() inherits (raob_profile);
CREATE TABLE raob_profile_2011() inherits (raob_profile);
CREATE TABLE raob_profile_2012() inherits (raob_profile);
CREATE TABLE raob_profile_2013() inherits (raob_profile);
CREATE TABLE raob_profile_2014() inherits (raob_profile);


CREATE INDEX raob_profile_1990_fid_idx on raob_profile_1990(fid);
CREATE INDEX raob_profile_1991_fid_idx on raob_profile_1991(fid);
CREATE INDEX raob_profile_1992_fid_idx on raob_profile_1992(fid);
CREATE INDEX raob_profile_1993_fid_idx on raob_profile_1993(fid);
CREATE INDEX raob_profile_1994_fid_idx on raob_profile_1994(fid);
CREATE INDEX raob_profile_1995_fid_idx on raob_profile_1995(fid);
CREATE INDEX raob_profile_1996_fid_idx on raob_profile_1996(fid);
CREATE INDEX raob_profile_1997_fid_idx on raob_profile_1997(fid);
CREATE INDEX raob_profile_1998_fid_idx on raob_profile_1998(fid);
CREATE INDEX raob_profile_1999_fid_idx on raob_profile_1999(fid);
CREATE INDEX raob_profile_2000_fid_idx on raob_profile_2000(fid);
CREATE INDEX raob_profile_2001_fid_idx on raob_profile_2001(fid);
CREATE INDEX raob_profile_2002_fid_idx on raob_profile_2002(fid);
CREATE INDEX raob_profile_2003_fid_idx on raob_profile_2003(fid);
CREATE INDEX raob_profile_2004_fid_idx on raob_profile_2004(fid);
CREATE INDEX raob_profile_2005_fid_idx on raob_profile_2005(fid);
CREATE INDEX raob_profile_2006_fid_idx on raob_profile_2006(fid);
CREATE INDEX raob_profile_2007_fid_idx on raob_profile_2007(fid);
CREATE INDEX raob_profile_2008_fid_idx on raob_profile_2008(fid);
CREATE INDEX raob_profile_2009_fid_idx on raob_profile_2009(fid);
CREATE INDEX raob_profile_2010_fid_idx on raob_profile_2010(fid);
CREATE INDEX raob_profile_2011_fid_idx on raob_profile_2011(fid);
CREATE INDEX raob_profile_2012_fid_idx on raob_profile_2012(fid);
CREATE INDEX raob_profile_2013_fid_idx on raob_profile_2013(fid);
CREATE INDEX raob_profile_2014_fid_idx on raob_profile_2014(fid);

GRANT SELECT on raob_profile to nobody,apache;
GRANT SELECT on raob_profile_2013 to nobody,apache;
GRANT SELECT on raob_profile_2014 to nobody,apache;

CREATE AGGREGATE array_accum (anyelement)
(
    sfunc = array_append,
    stype = anyarray,
    initcond = '{}'
);
--- array_to_string(array_accum(column),',')

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
CREATE TABLE snowfall_pns (
    source varchar(6),
    snow real,
    valid timestamp with time zone
);
select addgeometrycolumn('','snowfall_pns','geom',4326,'POINT',2);

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
    id serial,
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

CREATE table warnings_2010() inherits (warnings);

create index warnings_2010_idx 
   on warnings_2010(wfo,eventid,significance,phenomena);

grant select on warnings_2010 to apache;

CREATE table warnings_2011() inherits (warnings);

create index warnings_2011_idx 
   on warnings_2011(wfo,eventid,significance,phenomena);

grant select on warnings_2011 to apache;

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
  tml_sknt smallint
) WITH OIDS;
select addgeometrycolumn('','sbw','geom',4326,'MULTIPOLYGON',2);
select addGeometryColumn('sbw', 'tml_geom', 4326, 'POINT', 2);
select addGeometryColumn('sbw', 'tml_geom_line', 4326, 'LINESTRING', 2);

grant select on sbw to apache;

CREATE table sbw_2010() inherits (sbw);
create index sbw_2010_idx on sbw_2010(wfo,eventid,significance,phenomena);
grant select on sbw_2010 to apache;

CREATE table sbw_2011() inherits (sbw);
create index sbw_2011_idx on sbw_2011(wfo,eventid,significance,phenomena);
grant select on sbw_2011 to apache,nobody;

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

grant select on lsrs to apache;

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
grant select on nws_ugc to apache;

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
SELECT AddGeometryColumn('sigmets_current', 'geom', 4326, 'MULTIPOLYGON', 2);
GRANT SELECT on sigmets_current to nobody,apache;

CREATE TABLE sigmets_archive(
	sigmet_type char(1),
	label varchar(16),
	issue timestamp with time zone,
	expire timestamp with time zone,
	raw text
);
SELECT AddGeometryColumn('sigmets_archive', 'geom', 4326, 'MULTIPOLYGON', 2);
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

CREATE TABLE roads_2012_log(
  segid int REFERENCES roads_base(segid),
  valid timestamp with time zone,
  cond_code smallint REFERENCES roads_conditions(code),
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar);
GRANT SELECT on roads_2012_log to nobody,apache;

CREATE TABLE roads_current(
  segid int REFERENCES roads_base(segid),
  valid timestamp with time zone,
  cond_code smallint REFERENCES roads_conditions(code),
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar);
GRANT SELECT on roads_current to nobody,apache;

---
--- SPC Convective Outlooks (created: 22 Oct 2010)
---
DROP TABLE spc_outlooks;
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

CREATE TABLE nexrad_attributes_2014() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2014 to nobody,apache;
CREATE INDEX nexrad_attributes_2014_nexrad_idx 
	on nexrad_attributes_2014(nexrad);
CREATE INDEX nexrad_attributes_2014_valid_idx 
	on nexrad_attributes_2014(valid);
alter table nexrad_attributes_2014 add constraint 
	__nexrad_attributes_2014__constraint CHECK 
	(valid >= '2014-01-01 00:00+00' and valid < '2015-01-01 00:00+00');

--- nexrad_attributes_2004
CREATE TABLE nexrad_attributes_2004() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2004 to nobody,apache;
CREATE INDEX nexrad_attributes_2004_nexrad_idx 
	on nexrad_attributes_2004(nexrad);
CREATE INDEX nexrad_attributes_2004_valid_idx 
	on nexrad_attributes_2004(valid);
alter table nexrad_attributes_2004 add constraint 
	__nexrad_attributes_2014__constraint CHECK 
	(valid >= '2004-01-01 00:00+00' and valid < '2005-01-01 00:00+00');

--- nexrad_attributes_2003
CREATE TABLE nexrad_attributes_2003() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2003 to nobody,apache;
CREATE INDEX nexrad_attributes_2003_nexrad_idx 
	on nexrad_attributes_2003(nexrad);
CREATE INDEX nexrad_attributes_2003_valid_idx 
	on nexrad_attributes_2003(valid);
alter table nexrad_attributes_2003 add constraint 
	__nexrad_attributes_2013__constraint CHECK 
	(valid >= '2003-01-01 00:00+00' and valid < '2004-01-01 00:00+00');

--- nexrad_attributes_2002
CREATE TABLE nexrad_attributes_2002() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2002 to nobody,apache;
CREATE INDEX nexrad_attributes_2002_nexrad_idx 
	on nexrad_attributes_2002(nexrad);
CREATE INDEX nexrad_attributes_2002_valid_idx 
	on nexrad_attributes_2002(valid);
alter table nexrad_attributes_2002 add constraint 
	__nexrad_attributes_2002__constraint CHECK 
	(valid >= '2002-01-01 00:00+00' and valid < '2003-01-01 00:00+00');

--- nexrad_attributes_2001
CREATE TABLE nexrad_attributes_2001() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2001 to nobody,apache;
CREATE INDEX nexrad_attributes_2001_nexrad_idx 
	on nexrad_attributes_2001(nexrad);
CREATE INDEX nexrad_attributes_2001_valid_idx 
	on nexrad_attributes_2001(valid);
alter table nexrad_attributes_2001 add constraint 
	__nexrad_attributes_2001__constraint CHECK 
	(valid >= '2001-01-01 00:00+00' and valid < '2002-01-01 00:00+00');

--- nexrad_attributes_2000
CREATE TABLE nexrad_attributes_2000() inherits (nexrad_attributes_log);
GRANT SELECT on nexrad_attributes_2000 to nobody,apache;
CREATE INDEX nexrad_attributes_2000_nexrad_idx 
	on nexrad_attributes_2000(nexrad);
CREATE INDEX nexrad_attributes_2000_valid_idx 
	on nexrad_attributes_2000(valid);
alter table nexrad_attributes_2000 add constraint 
	__nexrad_attributes_2000__constraint CHECK 
	(valid >= '2000-01-01 00:00+00' and valid < '2001-01-01 00:00+00');


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

grant select on watches to apache;

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

grant select on watches to apache;
