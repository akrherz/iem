--- $ createdb coop
--- $ psql -f /usr/pgsql-9.0/share/contrib/postgis-1.5/postgis.sql coop
--- $ psql -f /usr/pgsql-9.0/share/contrib/postgis-1.5/spatial_ref_sys.sql coop

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
	wfo char(3),
	archive_begin timestamp with time zone,
	archive_end timestamp with time zone,
	tzname varchar(32),
	modified timestamp with time zone,
	iemid int PRIMARY KEY
	);
SELECT AddGeometryColumn('stations', 'geom', 4326, 'POINT', 2);
GRANT SELECT on stations to nobody,apache;

---
--- Store the climate normals
---
CREATE TABLE climate81(
  station varchar(6),
  valid date,
  high real,
  low real,
  precip real,
  snow real,
  max_high real,
  max_low real,
  min_high real,
  min_low real,
  max_precip real,
  years int,
  gdd50 real,
  sdd86 real,
  max_high_yr   int,
  max_low_yr    int,
  min_high_yr   int,
  min_low_yr    int,
  max_precip_yr int,
  max_range     smallint,
  min_range smallint 
);
CREATE UNIQUE INDEX climate81_idx on climate81(station,valid);
GRANT SELECT on climate81 to nobody,apache;

CREATE FUNCTION gdd48(real, real) RETURNS numeric
    LANGUAGE sql
    AS $_$select (( (CASE WHEN $1 > 48 THEN (case when $1 > 86 THEN 86 ELSE $1 END ) - 48 ELSE 0 END) + (CASE WHEN $2 > 48 THEN $2 - 48 ELSE 0 END) ) / 2.0)::numeric$_$;

--
-- base, max, high, low
 CREATE FUNCTION gddXX(real, real, real, real) RETURNS numeric
    LANGUAGE sql
    AS $_$select (( (CASE WHEN $3 > $1 THEN (case when $3 > $2 THEN $2 ELSE $3 END ) - $1 ELSE 0 END) + 
    (CASE WHEN $4 > $1 THEN $4 - $1 ELSE 0 END) ) / 2.0)::numeric$_$;
 
 CREATE FUNCTION hdd65(real, real) RETURNS numeric
 	LANGUAGE sql
 	AS $_$select (case when (65 - (( $1 + $2 )/2.)) > 0 then ( $1 + $2 )/2. else 0 end)::numeric$_$;
 	

DROP table r_precipevents;
CREATE table r_precipevents(
  stationid char(6),
  climoweek smallint,
  maxval real,
  meanval real,
  cat1e smallint,
  cat2e smallint,
  cat3e smallint,
  cat4e smallint,
  cat5e smallint,
  missing smallint 
);
grant select on r_precipevents to nobody;
create unique index r_precipevents_idx 
 on r_precipevents(stationid, climoweek);

DROP table r_monthly;
CREATE table r_monthly(
  stationid char(6),
  monthdate date,
  gdd40 smallint,
  gdd48 smallint,
  gdd50 smallint,
  gdd52 smallint
);
grant select on r_rmonthly to nobody;
create unique index r_monthly_idx
 on r_monthly(stationid, monthdate);