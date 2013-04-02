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
    hvtec_nwsli character(5)
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
grant select on sbw_2011 to apache;


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

CREATE table lsrs_2010() inherits (lsrs);
grant select on lsrs_2010 to apache;
CREATE INDEX lsrs_2010_bogus_idx ON lsrs USING btree (oid);
CREATE INDEX lsrs_2010_valid_idx ON lsrs USING btree (valid);
CREATE INDEX lsrs_2010_wfo_idx ON lsrs USING btree (wfo);

CREATE table lsrs_2011() inherits (lsrs);
grant select on lsrs_2011 to apache;
CREATE INDEX lsrs_2011_bogus_idx ON lsrs USING btree (oid);
CREATE INDEX lsrs_2011_valid_idx ON lsrs USING btree (valid);
CREATE INDEX lsrs_2011_wfo_idx ON lsrs USING btree (wfo);



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
--- Local Storm Reports
---
CREATE TABLE lsrs(
 valid timestamp with time zone,
 type char(1),
 magnitude real,
 city varchar(32),
 county varchar(32),
 state char(2),
 source varchar(32),
 remark text,
 wfo char(3),
 typetext varchar(40)
);
SELECT AddGeometryColumn('lsrs', 'geom', 4326, 'POINT', 2);
GRANT SELECT on lsrs to nobody,apache;

CREATE TABLE lsrs_2011() inherits (lsrs);
GRANT SELECT on lsrs_2011 to nobody,apache;

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
	tempval numeric);

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
  category varchar(26),
  day smallint,
  outlook_type char(1)
);
SELECT addGeometryColumn('', 'spc_outlooks', 'geom', 4326, 'POLYGON', 2);
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

CREATE TABLE watches (
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
