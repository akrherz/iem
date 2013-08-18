--- $ createdb coop
--- $ psql -f /usr/pgsql-9.0/share/contrib/postgis-1.5/postgis.sql coop
--- $ psql -f /usr/pgsql-9.0/share/contrib/postgis-1.5/spatial_ref_sys.sql coop

---
--- Quickstats table
---
CREATE TABLE quickstats(
SOURCE_DESC  varchar(60),
SECTOR_DESC	 varchar(60),
GROUP_DESC	 varchar(80),
COMMODITY_DESC varchar(80),
CLASS_DESC varchar(180),
PRODN_PRACTICE_DESC varchar(180),
UTIL_PRACTICE_DESC varchar(180),
STATISTICCAT_DESC varchar(80),
UNIT_DESC varchar(60),
SHORT_DESC varchar(512),
DOMAIN_DESC varchar(256),
DOMAINCAT_DESC varchar(512),
AGG_LEVEL_DESC varchar(40),
STATE_ANSI varchar(2),
STATE_FIPS_CODE varchar(2),
STATE_ALPHA varchar(2),
STATE_NAME varchar(30),
ASD_CODE varchar(2),
ASD_DESC varchar(60),
COUNTY_ANSI varchar(3),
COUNTY_CODE varchar(3),
COUNTY_NAME varchar(30),
REGION_DESC varchar(80),
ZIP_5 varchar(5),
WATERSHED_CODE varchar(8),
WATERSHED_DESC varchar(120),
CONGR_DISTRICT_CODE varchar(2),
COUNTRY_CODE varchar(4),
COUNTRY_NAME varchar(60),
LOCATION_DESC varchar(120),
YEAR varchar(4),
FREQ_DESC varchar(30),
BEGIN_CODE varchar(2),
END_CODE varchar(2),
REFERENCE_PERIOD_DESC varchar(40),
WEEK_ENDING varchar(10),
LOAD_TIME varchar(19),
VALUE varchar(24)
);

---
--- Datastorage tables
---
CREATE TABLE alldata(
  station char(6),
  day date,
  high int,
  low int,
  precip real,
  snow real,
  sday char(4),
  year int,
  month smallint,
  snowd real,
  estimated boolean,
  narr_srad real,
  merra_srad real,
  merra_srad_cs real,
  hrrr_srad real
  );
GRANT select on alldata to nobody,apache;

CREATE TABLE alldata_ia() inherits (alldata);
CREATE TABLE alldata_il() inherits (alldata);
CREATE TABLE alldata_wi() inherits (alldata);
CREATE TABLE alldata_mn() inherits (alldata);
CREATE TABLE alldata_nd() inherits (alldata);
CREATE TABLE alldata_sd() inherits (alldata);
CREATE TABLE alldata_ne() inherits (alldata);
CREATE TABLE alldata_ks() inherits (alldata);
CREATE TABLE alldata_ky() inherits (alldata);
CREATE TABLE alldata_in() inherits (alldata);
CREATE TABLE alldata_oh() inherits (alldata);
CREATE TABLE alldata_mi() inherits (alldata);
CREATE TABLE alldata_mo() inherits (alldata);

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
 CREATE FUNCTION gddxx(real, real, real, real) RETURNS numeric
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
  gdd52 smallint,
  avg_high smallint,
  avg_low smallint,
  rain real,
  hdd real,
  cdd real,
  rain_days smallint,
  snow_days smallint,
  hdd60 real,
  cdd60 real
);
grant select on r_rmonthly to nobody;
create unique index r_monthly_idx
 on r_monthly(stationid, monthdate);