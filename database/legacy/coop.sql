---
--- Storage of Hayhoe downscaled data
---
CREATE TABLE hayhoe_daily(
  model varchar(32),
  scenario varchar(8),
  station varchar(6),
  day date,
  high real,
  low real,
  precip real
);
GRANT SELECT on hayhoe_daily to nobody,apache;
CREATE INDEX hayhoe_daily_station_idx on hayhoe_daily(station);

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

 CREATE TABLE alldata_ak() inherits (alldata); 
 GRANT SELECT on alldata_ak to nobody,apache;
 CREATE TABLE alldata_al() inherits (alldata); 
 GRANT SELECT on alldata_al to nobody,apache;
 CREATE TABLE alldata_ar() inherits (alldata); 
 GRANT SELECT on alldata_ar to nobody,apache;
 CREATE TABLE alldata_az() inherits (alldata); 
 GRANT SELECT on alldata_az to nobody,apache;
 CREATE TABLE alldata_ca() inherits (alldata); 
 GRANT SELECT on alldata_ca to nobody,apache;
 CREATE TABLE alldata_co() inherits (alldata); 
 GRANT SELECT on alldata_co to nobody,apache;
 CREATE TABLE alldata_ct() inherits (alldata); 
 GRANT SELECT on alldata_ct to nobody,apache;
 CREATE TABLE alldata_dc() inherits (alldata); 
 GRANT SELECT on alldata_dc to nobody,apache;
 CREATE TABLE alldata_de() inherits (alldata); 
 GRANT SELECT on alldata_de to nobody,apache;
 CREATE TABLE alldata_fl() inherits (alldata); 
 GRANT SELECT on alldata_fl to nobody,apache;
 CREATE TABLE alldata_ga() inherits (alldata); 
 GRANT SELECT on alldata_ga to nobody,apache;
 CREATE TABLE alldata_hi() inherits (alldata); 
 GRANT SELECT on alldata_hi to nobody,apache;
 CREATE TABLE alldata_ia() inherits (alldata); 
 GRANT SELECT on alldata_ia to nobody,apache,apiuser;
 CREATE TABLE alldata_id() inherits (alldata); 
 GRANT SELECT on alldata_id to nobody,apache;
 CREATE TABLE alldata_il() inherits (alldata); 
 GRANT SELECT on alldata_il to nobody,apache;
 CREATE TABLE alldata_in() inherits (alldata); 
 GRANT SELECT on alldata_in to nobody,apache;
 CREATE TABLE alldata_ks() inherits (alldata); 
 GRANT SELECT on alldata_ks to nobody,apache;
 CREATE TABLE alldata_ky() inherits (alldata); 
 GRANT SELECT on alldata_ky to nobody,apache;
 CREATE TABLE alldata_la() inherits (alldata); 
 GRANT SELECT on alldata_la to nobody,apache;
 CREATE TABLE alldata_ma() inherits (alldata); 
 GRANT SELECT on alldata_ma to nobody,apache;
 CREATE TABLE alldata_md() inherits (alldata); 
 GRANT SELECT on alldata_md to nobody,apache;
 CREATE TABLE alldata_me() inherits (alldata); 
 GRANT SELECT on alldata_me to nobody,apache;
 CREATE TABLE alldata_mi() inherits (alldata); 
 GRANT SELECT on alldata_mi to nobody,apache;
 CREATE TABLE alldata_mn() inherits (alldata); 
 GRANT SELECT on alldata_mn to nobody,apache;
 CREATE TABLE alldata_mo() inherits (alldata); 
 GRANT SELECT on alldata_mo to nobody,apache;
 CREATE TABLE alldata_ms() inherits (alldata); 
 GRANT SELECT on alldata_ms to nobody,apache;
 CREATE TABLE alldata_mt() inherits (alldata); 
 GRANT SELECT on alldata_mt to nobody,apache;
 CREATE TABLE alldata_nc() inherits (alldata); 
 GRANT SELECT on alldata_nc to nobody,apache;
 CREATE TABLE alldata_nd() inherits (alldata); 
 GRANT SELECT on alldata_nd to nobody,apache;
 CREATE TABLE alldata_ne() inherits (alldata); 
 GRANT SELECT on alldata_ne to nobody,apache;
 CREATE TABLE alldata_nh() inherits (alldata); 
 GRANT SELECT on alldata_nh to nobody,apache;
 CREATE TABLE alldata_nj() inherits (alldata); 
 GRANT SELECT on alldata_nj to nobody,apache;
 CREATE TABLE alldata_nm() inherits (alldata); 
 GRANT SELECT on alldata_nm to nobody,apache;
 CREATE TABLE alldata_nv() inherits (alldata); 
 GRANT SELECT on alldata_nv to nobody,apache;
 CREATE TABLE alldata_ny() inherits (alldata); 
 GRANT SELECT on alldata_ny to nobody,apache;
 CREATE TABLE alldata_oh() inherits (alldata); 
 GRANT SELECT on alldata_oh to nobody,apache;
 CREATE TABLE alldata_ok() inherits (alldata); 
 GRANT SELECT on alldata_ok to nobody,apache;
 CREATE TABLE alldata_or() inherits (alldata); 
 GRANT SELECT on alldata_or to nobody,apache;
 CREATE TABLE alldata_pa() inherits (alldata); 
 GRANT SELECT on alldata_pa to nobody,apache;
 CREATE TABLE alldata_ri() inherits (alldata); 
 GRANT SELECT on alldata_ri to nobody,apache;
 CREATE TABLE alldata_sc() inherits (alldata); 
 GRANT SELECT on alldata_sc to nobody,apache;
 CREATE TABLE alldata_sd() inherits (alldata); 
 GRANT SELECT on alldata_sd to nobody,apache;
 CREATE TABLE alldata_tn() inherits (alldata); 
 GRANT SELECT on alldata_tn to nobody,apache;
 CREATE TABLE alldata_tx() inherits (alldata); 
 GRANT SELECT on alldata_tx to nobody,apache;
 CREATE TABLE alldata_ut() inherits (alldata); 
 GRANT SELECT on alldata_ut to nobody,apache;
 CREATE TABLE alldata_va() inherits (alldata); 
 GRANT SELECT on alldata_va to nobody,apache;
 CREATE TABLE alldata_vt() inherits (alldata); 
 GRANT SELECT on alldata_vt to nobody,apache;
 CREATE TABLE alldata_wa() inherits (alldata); 
 GRANT SELECT on alldata_wa to nobody,apache;
 CREATE TABLE alldata_wi() inherits (alldata); 
 GRANT SELECT on alldata_wi to nobody,apache;
 CREATE TABLE alldata_wv() inherits (alldata); 
 GRANT SELECT on alldata_wv to nobody,apache;
 CREATE TABLE alldata_wy() inherits (alldata); 
 GRANT SELECT on alldata_wy to nobody,apache;


CREATE TABLE alldata_estimates(
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
GRANT select on alldata_estimates to nobody,apache;

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
GRANT SELECT on stations to nobody,apache,apiuser;

---
--- Store the climate normals
---
CREATE TABLE climate(
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
  min_range smallint,
  hdd65 real 
);
CREATE UNIQUE INDEX climate_idx on climate(station,valid);
GRANT SELECT on climate to nobody,apache;

CREATE TABLE climate51(
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
  min_range smallint,
  hdd65 real 
);
CREATE UNIQUE INDEX climate51_idx on climate51(station,valid);
CREATE INDEX climate51_station_idx on climate51(station);
CREATE INDEX climate51_valid_idx on climate51(valid);
GRANT SELECT on climate51 to nobody,apache;

CREATE TABLE climate71(
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
  min_range smallint,
  hdd65 real 
);
CREATE UNIQUE INDEX climate71_idx on climate71(station,valid);
GRANT SELECT on climate71 to nobody,apache;

CREATE TABLE ncdc_climate71(
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
  min_range smallint,
  hdd65 real 
);
CREATE UNIQUE INDEX ncdc_climate71_idx on ncdc_climate71(station,valid);
GRANT SELECT on ncdc_climate71 to nobody,apache;

CREATE TABLE ncdc_climate81(
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
  min_range smallint,
  hdd65 real 
);
CREATE UNIQUE INDEX ncdc_climate81_idx on ncdc_climate81(station,valid);
GRANT SELECT on ncdc_climate81 to nobody,apache;


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
  min_range smallint,
  hdd65 real 
);
CREATE UNIQUE INDEX climate81_idx on climate81(station,valid);
GRANT SELECT on climate81 to nobody,apache;


CREATE FUNCTION sdd86(real, real) RETURNS numeric
    LANGUAGE sql
    AS $_$select ( (CASE WHEN $1 > 86 THEN $1 - 86 ELSE 0 END) )::numeric$_$;
    
CREATE FUNCTION gdd48(real, real) RETURNS numeric
    LANGUAGE sql
    AS $_$select (( (CASE WHEN $1 > 48 THEN (case when $1 > 86 THEN 86 ELSE $1 END ) - 48 ELSE 0 END) + (CASE WHEN $2 > 48 THEN $2 - 48 ELSE 0 END) ) / 2.0)::numeric$_$;

--
-- base, max, high, low
 CREATE FUNCTION gddxx(real, real, real, real) RETURNS numeric
    LANGUAGE sql
    AS $_$select (( (CASE WHEN $3 > $1 THEN (case when $3 > $2 THEN $2 ELSE $3 END ) - $1 ELSE 0 END) + 
    (CASE WHEN $4 > $1 THEN $4 - $1 ELSE 0 END) ) / 2.0)::numeric$_$;
 
 CREATE OR REPLACE FUNCTION hdd65(real, real) RETURNS numeric
 	LANGUAGE sql
 	AS $_$select (case when (65 - (( $1 + $2 )/2.)) > 0 then (65. - ( $1 + $2 )/2.) else 0 end)::numeric$_$;
 	

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