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

  