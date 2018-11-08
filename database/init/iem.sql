CREATE EXTENSION postgis;

-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (15, now());

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
--- Some skycoverage metadata
---
CREATE TABLE skycoverage(
  code char(3),
  value smallint);
GRANT SELECT on skycoverage to nobody,apache;
INSERT into skycoverage values('CLR', 0);
INSERT into skycoverage values('FEW', 25);
INSERT into skycoverage values('SCT', 50);
INSERT into skycoverage values('BKN', 75);
INSERT into skycoverage values('OVC', 100);

---
--- Events table
---
CREATE TABLE events(
  station varchar(10),
  network varchar(10),
  valid timestamptz,
  event varchar(10),
  magnitude real,
  iemid int REFERENCES stations(iemid)
);
GRANT SELECT on events to nobody,apache;

---
--- Current QC data
---
CREATE TABLE current_qc(
  station varchar(10),
  valid timestamp without time zone,
  network varchar(10),
  tmpf real,
  tmpf_qc_av real,
  tmpf_qc_sc real,
  dwpf real,
  dwpf_qc_av real,
  dwpf_qc_sc real,  
  alti real,
  alti_qc_av real,
  alti_qc_sc real,
  iemid int REFERENCES stations(iemid)
 );
CREATE UNIQUE INDEX current_qc_idx on current_qc(station, network);
GRANT SELECT on current_qc to nobody,apache;

---
--- Copy of the climate51 table that is in the coop database
---
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

---
--- Storage of information we parse from CLI products
---
CREATE TABLE cli_data(
  station char(4),
  product varchar(64),
  valid date,
  high int,
  high_normal int,
  high_record int,
  high_record_years int[],
  high_time varchar(7),
  low int,
  low_normal int,
  low_record int,
  low_record_years int[],
  low_time varchar(7),
  precip float,
  precip_month float,
  precip_jan1 float,
  precip_jan1_normal float,
  precip_jul1 float,
  precip_dec1 float,
  precip_dec1_normal float,
  precip_normal float,
  precip_record float,
  precip_record_years int[],
  precip_month_normal real,
  snow float,
  snow_month float,
  snow_jun1 float,
  snow_jul1 float,
  snow_dec1 float,
  snow_record_years int[],
  snow_record float,
  snow_jun1_normal float,
  snow_jul1_normal float,
  snow_dec1_normal float,
  snow_month_normal float,
  precip_jun1 real,
  precip_jun1_normal real
);
CREATE UNIQUE index cli_data_idx on cli_data(station,valid);
GRANT SELECT on cli_data to nobody,apache;

---
--- Offline metadata
---
CREATE TABLE offline(
	station varchar(20),
	network varchar(10),
	trackerid int,
	valid timestamptz);
GRANT SELECT on offline to nobody,apache;


 create table current_shef(
   station varchar(10),
   valid timestamp with time zone,
   physical_code char(2),
   duration char(1),
   source char(2),
   extremum char(1),
   probability char(1),
   value real,
   depth smallint
   );
 create index current_shef_station_idx on current_shef(station);
 GRANT SELECT on current_shef to nobody;
 GRANT SELECT on current_shef to apache;
 
CREATE OR REPLACE RULE replace_current_shef AS ON 
    INSERT TO current_shef WHERE (EXISTS 
        (SELECT 1 FROM current_shef WHERE
        station = new.station and physical_code = new.physical_code and
        duration = new.duration and source = new.source and 
        extremum = new.extremum and ((new.depth is null and depth is null) or 
        depth = new.depth))) DO INSTEAD 
        UPDATE current_shef SET value = new.value, valid = new.valid 
        WHERE station = new.station and physical_code = new.physical_code and
        duration = new.duration and source = new.source and 
        extremum = new.extremum and valid < new.valid and 
        ((new.depth is null and depth is null) or depth = new.depth);


CREATE TABLE current_tmp(
    iemid int REFERENCES stations(iemid),
    tmpf real,
    dwpf real,
    drct real,
    sknt real,
    indoor_tmpf real,
    tsf0 real,
    tsf1 real,
    tsf2 real,
    tsf3 real,
    rwis_subf real,
    scond0 character varying,
    scond1 character varying,
    scond2 character varying,
    scond3 character varying,
    valid timestamp with time zone DEFAULT '1980-01-01 00:00:00-06'::timestamp with time zone,
    pday real,
    c1smv real,
    c2smv real,
    c3smv real,
    c4smv real,
    c5smv real,
    c1tmpf real,
    c2tmpf real,
    c3tmpf real,
    c4tmpf real,
    c5tmpf real,
    pres real,
    relh real,
    srad real,
    vsby real,
    phour real DEFAULT (-99),
    gust real,
    raw character varying(256),
    alti real,
    mslp real,
    qc_tmpf character(1),
    qc_dwpf character(1),
    rstage real,
    ozone real,
    co2 real,
    pmonth real,
    skyc1 character(3),
    skyc2 character(3),
    skyc3 character(3),
    skyl1 integer,
    skyl2 integer,
    skyl3 integer,
    skyc4 character(3),
    skyl4 integer,
    pcounter real,
    discharge real,
    p03i real,
    p06i real,
    p24i real,
    max_tmpf_6hr real,
    min_tmpf_6hr real,
    max_tmpf_24hr real,
    min_tmpf_24hr real,
    wxcodes varchar(12)[],
    battery real,
    water_tmpf real,
    feel real
);

CREATE TABLE current (
    iemid int REFERENCES stations(iemid),
    tmpf real,
    dwpf real,
    drct real,
    sknt real,
    indoor_tmpf real,
    tsf0 real,
    tsf1 real,
    tsf2 real,
    tsf3 real,
    rwis_subf real,
    scond0 character varying,
    scond1 character varying,
    scond2 character varying,
    scond3 character varying,
    valid timestamp with time zone DEFAULT '1980-01-01 00:00:00-06'::timestamp with time zone,
    pday real,
    c1smv real,
    c2smv real,
    c3smv real,
    c4smv real,
    c5smv real,
    c1tmpf real,
    c2tmpf real,
    c3tmpf real,
    c4tmpf real,
    c5tmpf real,
    pres real,
    relh real,
    srad real,
    vsby real,
    phour real DEFAULT (-99),
    gust real,
    raw character varying(256),
    alti real,
    mslp real,
    qc_tmpf character(1),
    qc_dwpf character(1),
    rstage real,
    ozone real,
    co2 real,
    pmonth real,
    skyc1 character(3),
    skyc2 character(3),
    skyc3 character(3),
    skyl1 integer,
    skyl2 integer,
    skyl3 integer,
    skyc4 character(3),
    skyl4 integer,
    pcounter real,
    discharge real,
    p03i real,
    p06i real,
    p24i real,
    max_tmpf_6hr real,
    min_tmpf_6hr real,
    max_tmpf_24hr real,
    min_tmpf_24hr real,
    wxcodes varchar(12)[],
    battery real,
    water_tmpf real,
    feel real
);
CREATE UNIQUE index current_iemid_idx on current(iemid);
GRANT SELECT on current to apache,nobody;

CREATE TABLE current_log (
    iemid int REFERENCES stations(iemid),
    tmpf real,
    dwpf real,
    drct real,
    sknt real,
    indoor_tmpf real,
    tsf0 real,
    tsf1 real,
    tsf2 real,
    tsf3 real,
    rwis_subf real,
    scond0 character varying,
    scond1 character varying,
    scond2 character varying,
    scond3 character varying,
    valid timestamp with time zone DEFAULT '1980-01-01 00:00:00-06'::timestamp with time zone,
    pday real,
    c1smv real,
    c2smv real,
    c3smv real,
    c4smv real,
    c5smv real,
    c1tmpf real,
    c2tmpf real,
    c3tmpf real,
    c4tmpf real,
    c5tmpf real,
    pres real,
    relh real,
    srad real,
    vsby real,
    phour real DEFAULT (-99),
    gust real,
    raw character varying(256),
    alti real,
    mslp real,
    qc_tmpf character(1),
    qc_dwpf character(1),
    rstage real,
    ozone real,
    co2 real,
    pmonth real,
    skyc1 character(3),
    skyc2 character(3),
    skyc3 character(3),
    skyl1 integer,
    skyl2 integer,
    skyl3 integer,
    skyc4 character(3),
    skyl4 integer,
    pcounter real,
    discharge real,
    p03i real,
    p06i real,
    p24i real,
    max_tmpf_6hr real,
    min_tmpf_6hr real,
    max_tmpf_24hr real,
    min_tmpf_24hr real,
    wxcodes varchar(12)[],
    battery real,
    water_tmpf real,
    feel real
);
ALTER TABLE current_log SET WITH oids;

CREATE OR REPLACE FUNCTION current_update_log() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
  BEGIN
   IF (NEW.valid != OLD.valid) THEN
     INSERT into current_log SELECT * from current WHERE iemid = NEW.iemid;
   END IF;
   RETURN NEW;
  END
 $$;

CREATE TRIGGER current_update_tigger AFTER UPDATE ON current 
FOR EACH ROW EXECUTE PROCEDURE current_update_log();


CREATE TABLE summary (
	iemid int REFERENCES stations(iemid),
    max_tmpf real,
    min_tmpf real,
    day date,
    max_sknt real,
    max_gust real,
    max_sknt_ts timestamp with time zone,
    max_gust_ts timestamp with time zone,
    max_dwpf real,
    min_dwpf real,
    pday real,
    pmonth real,
    snow real,
    snowd real,
    max_tmpf_qc character(1),
    min_tmpf_qc character(1),
    pday_qc character(1),
    snow_qc character(1),
    snoww real,
    max_drct real,
    max_srad smallint,
    coop_tmpf real,
    coop_valid timestamp with time zone,
    et_inch real,
    srad_mj real,
    avg_sknt real,
    vector_avg_drct real,
    avg_rh real,
    min_rh real,
    max_rh real,
    max_water_tmpf real,
    min_water_tmpf real,
    max_feel real,
    avg_feel real,
    min_feel real
);
GRANT SELECT on summary to nobody,apache;

---
--- Hourly precip
---
CREATE TABLE hourly(
  station varchar(20),
  network varchar(10),
  valid timestamptz,
  phour real,
  iemid int references stations(iemid)
);
GRANT SELECT on hourly to apache,nobody;

---
---
create table hourly_1941( 
  CONSTRAINT __hourly_1941_check 
  CHECK(valid >= '1941-01-01 00:00+00'::timestamptz 
        and valid < '1942-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1941_idx on hourly_1941(station, network, valid);
CREATE INDEX hourly_1941_valid_idx on hourly_1941(valid);
GRANT SELECT on hourly_1941 to nobody,apache;
    

create table hourly_1942( 
  CONSTRAINT __hourly_1942_check 
  CHECK(valid >= '1942-01-01 00:00+00'::timestamptz 
        and valid < '1943-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1942_idx on hourly_1942(station, network, valid);
CREATE INDEX hourly_1942_valid_idx on hourly_1942(valid);
GRANT SELECT on hourly_1942 to nobody,apache;
    

create table hourly_1943( 
  CONSTRAINT __hourly_1943_check 
  CHECK(valid >= '1943-01-01 00:00+00'::timestamptz 
        and valid < '1944-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1943_idx on hourly_1943(station, network, valid);
CREATE INDEX hourly_1943_valid_idx on hourly_1943(valid);
GRANT SELECT on hourly_1943 to nobody,apache;
    

create table hourly_1944( 
  CONSTRAINT __hourly_1944_check 
  CHECK(valid >= '1944-01-01 00:00+00'::timestamptz 
        and valid < '1945-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1944_idx on hourly_1944(station, network, valid);
CREATE INDEX hourly_1944_valid_idx on hourly_1944(valid);
GRANT SELECT on hourly_1944 to nobody,apache;
    

create table hourly_1945( 
  CONSTRAINT __hourly_1945_check 
  CHECK(valid >= '1945-01-01 00:00+00'::timestamptz 
        and valid < '1946-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1945_idx on hourly_1945(station, network, valid);
CREATE INDEX hourly_1945_valid_idx on hourly_1945(valid);
GRANT SELECT on hourly_1945 to nobody,apache;
    

create table hourly_1946( 
  CONSTRAINT __hourly_1946_check 
  CHECK(valid >= '1946-01-01 00:00+00'::timestamptz 
        and valid < '1947-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1946_idx on hourly_1946(station, network, valid);
CREATE INDEX hourly_1946_valid_idx on hourly_1946(valid);
GRANT SELECT on hourly_1946 to nobody,apache;
    

create table hourly_1947( 
  CONSTRAINT __hourly_1947_check 
  CHECK(valid >= '1947-01-01 00:00+00'::timestamptz 
        and valid < '1948-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1947_idx on hourly_1947(station, network, valid);
CREATE INDEX hourly_1947_valid_idx on hourly_1947(valid);
GRANT SELECT on hourly_1947 to nobody,apache;
    

create table hourly_1948( 
  CONSTRAINT __hourly_1948_check 
  CHECK(valid >= '1948-01-01 00:00+00'::timestamptz 
        and valid < '1949-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1948_idx on hourly_1948(station, network, valid);
CREATE INDEX hourly_1948_valid_idx on hourly_1948(valid);
GRANT SELECT on hourly_1948 to nobody,apache;
    

create table hourly_1949( 
  CONSTRAINT __hourly_1949_check 
  CHECK(valid >= '1949-01-01 00:00+00'::timestamptz 
        and valid < '1950-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1949_idx on hourly_1949(station, network, valid);
CREATE INDEX hourly_1949_valid_idx on hourly_1949(valid);
GRANT SELECT on hourly_1949 to nobody,apache;
    

create table hourly_1950( 
  CONSTRAINT __hourly_1950_check 
  CHECK(valid >= '1950-01-01 00:00+00'::timestamptz 
        and valid < '1951-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1950_idx on hourly_1950(station, network, valid);
CREATE INDEX hourly_1950_valid_idx on hourly_1950(valid);
GRANT SELECT on hourly_1950 to nobody,apache;
    

create table hourly_1951( 
  CONSTRAINT __hourly_1951_check 
  CHECK(valid >= '1951-01-01 00:00+00'::timestamptz 
        and valid < '1952-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1951_idx on hourly_1951(station, network, valid);
CREATE INDEX hourly_1951_valid_idx on hourly_1951(valid);
GRANT SELECT on hourly_1951 to nobody,apache;
    

create table hourly_1952( 
  CONSTRAINT __hourly_1952_check 
  CHECK(valid >= '1952-01-01 00:00+00'::timestamptz 
        and valid < '1953-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1952_idx on hourly_1952(station, network, valid);
CREATE INDEX hourly_1952_valid_idx on hourly_1952(valid);
GRANT SELECT on hourly_1952 to nobody,apache;
    

create table hourly_1953( 
  CONSTRAINT __hourly_1953_check 
  CHECK(valid >= '1953-01-01 00:00+00'::timestamptz 
        and valid < '1954-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1953_idx on hourly_1953(station, network, valid);
CREATE INDEX hourly_1953_valid_idx on hourly_1953(valid);
GRANT SELECT on hourly_1953 to nobody,apache;
    

create table hourly_1954( 
  CONSTRAINT __hourly_1954_check 
  CHECK(valid >= '1954-01-01 00:00+00'::timestamptz 
        and valid < '1955-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1954_idx on hourly_1954(station, network, valid);
CREATE INDEX hourly_1954_valid_idx on hourly_1954(valid);
GRANT SELECT on hourly_1954 to nobody,apache;
    

create table hourly_1955( 
  CONSTRAINT __hourly_1955_check 
  CHECK(valid >= '1955-01-01 00:00+00'::timestamptz 
        and valid < '1956-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1955_idx on hourly_1955(station, network, valid);
CREATE INDEX hourly_1955_valid_idx on hourly_1955(valid);
GRANT SELECT on hourly_1955 to nobody,apache;
    

create table hourly_1956( 
  CONSTRAINT __hourly_1956_check 
  CHECK(valid >= '1956-01-01 00:00+00'::timestamptz 
        and valid < '1957-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1956_idx on hourly_1956(station, network, valid);
CREATE INDEX hourly_1956_valid_idx on hourly_1956(valid);
GRANT SELECT on hourly_1956 to nobody,apache;
    

create table hourly_1957( 
  CONSTRAINT __hourly_1957_check 
  CHECK(valid >= '1957-01-01 00:00+00'::timestamptz 
        and valid < '1958-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1957_idx on hourly_1957(station, network, valid);
CREATE INDEX hourly_1957_valid_idx on hourly_1957(valid);
GRANT SELECT on hourly_1957 to nobody,apache;
    

create table hourly_1958( 
  CONSTRAINT __hourly_1958_check 
  CHECK(valid >= '1958-01-01 00:00+00'::timestamptz 
        and valid < '1959-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1958_idx on hourly_1958(station, network, valid);
CREATE INDEX hourly_1958_valid_idx on hourly_1958(valid);
GRANT SELECT on hourly_1958 to nobody,apache;
    

create table hourly_1959( 
  CONSTRAINT __hourly_1959_check 
  CHECK(valid >= '1959-01-01 00:00+00'::timestamptz 
        and valid < '1960-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1959_idx on hourly_1959(station, network, valid);
CREATE INDEX hourly_1959_valid_idx on hourly_1959(valid);
GRANT SELECT on hourly_1959 to nobody,apache;
    

create table hourly_1960( 
  CONSTRAINT __hourly_1960_check 
  CHECK(valid >= '1960-01-01 00:00+00'::timestamptz 
        and valid < '1961-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1960_idx on hourly_1960(station, network, valid);
CREATE INDEX hourly_1960_valid_idx on hourly_1960(valid);
GRANT SELECT on hourly_1960 to nobody,apache;
    

create table hourly_1961( 
  CONSTRAINT __hourly_1961_check 
  CHECK(valid >= '1961-01-01 00:00+00'::timestamptz 
        and valid < '1962-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1961_idx on hourly_1961(station, network, valid);
CREATE INDEX hourly_1961_valid_idx on hourly_1961(valid);
GRANT SELECT on hourly_1961 to nobody,apache;
    

create table hourly_1962( 
  CONSTRAINT __hourly_1962_check 
  CHECK(valid >= '1962-01-01 00:00+00'::timestamptz 
        and valid < '1963-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1962_idx on hourly_1962(station, network, valid);
CREATE INDEX hourly_1962_valid_idx on hourly_1962(valid);
GRANT SELECT on hourly_1962 to nobody,apache;
    

create table hourly_1963( 
  CONSTRAINT __hourly_1963_check 
  CHECK(valid >= '1963-01-01 00:00+00'::timestamptz 
        and valid < '1964-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1963_idx on hourly_1963(station, network, valid);
CREATE INDEX hourly_1963_valid_idx on hourly_1963(valid);
GRANT SELECT on hourly_1963 to nobody,apache;
    

create table hourly_1964( 
  CONSTRAINT __hourly_1964_check 
  CHECK(valid >= '1964-01-01 00:00+00'::timestamptz 
        and valid < '1965-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1964_idx on hourly_1964(station, network, valid);
CREATE INDEX hourly_1964_valid_idx on hourly_1964(valid);
GRANT SELECT on hourly_1964 to nobody,apache;
    

create table hourly_1965( 
  CONSTRAINT __hourly_1965_check 
  CHECK(valid >= '1965-01-01 00:00+00'::timestamptz 
        and valid < '1966-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1965_idx on hourly_1965(station, network, valid);
CREATE INDEX hourly_1965_valid_idx on hourly_1965(valid);
GRANT SELECT on hourly_1965 to nobody,apache;
    

create table hourly_1966( 
  CONSTRAINT __hourly_1966_check 
  CHECK(valid >= '1966-01-01 00:00+00'::timestamptz 
        and valid < '1967-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1966_idx on hourly_1966(station, network, valid);
CREATE INDEX hourly_1966_valid_idx on hourly_1966(valid);
GRANT SELECT on hourly_1966 to nobody,apache;
    

create table hourly_1967( 
  CONSTRAINT __hourly_1967_check 
  CHECK(valid >= '1967-01-01 00:00+00'::timestamptz 
        and valid < '1968-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1967_idx on hourly_1967(station, network, valid);
CREATE INDEX hourly_1967_valid_idx on hourly_1967(valid);
GRANT SELECT on hourly_1967 to nobody,apache;
    

create table hourly_1968( 
  CONSTRAINT __hourly_1968_check 
  CHECK(valid >= '1968-01-01 00:00+00'::timestamptz 
        and valid < '1969-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1968_idx on hourly_1968(station, network, valid);
CREATE INDEX hourly_1968_valid_idx on hourly_1968(valid);
GRANT SELECT on hourly_1968 to nobody,apache;
    

create table hourly_1969( 
  CONSTRAINT __hourly_1969_check 
  CHECK(valid >= '1969-01-01 00:00+00'::timestamptz 
        and valid < '1970-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1969_idx on hourly_1969(station, network, valid);
CREATE INDEX hourly_1969_valid_idx on hourly_1969(valid);
GRANT SELECT on hourly_1969 to nobody,apache;
    

create table hourly_1970( 
  CONSTRAINT __hourly_1970_check 
  CHECK(valid >= '1970-01-01 00:00+00'::timestamptz 
        and valid < '1971-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1970_idx on hourly_1970(station, network, valid);
CREATE INDEX hourly_1970_valid_idx on hourly_1970(valid);
GRANT SELECT on hourly_1970 to nobody,apache;
    

create table hourly_1971( 
  CONSTRAINT __hourly_1971_check 
  CHECK(valid >= '1971-01-01 00:00+00'::timestamptz 
        and valid < '1972-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1971_idx on hourly_1971(station, network, valid);
CREATE INDEX hourly_1971_valid_idx on hourly_1971(valid);
GRANT SELECT on hourly_1971 to nobody,apache;
    

create table hourly_1972( 
  CONSTRAINT __hourly_1972_check 
  CHECK(valid >= '1972-01-01 00:00+00'::timestamptz 
        and valid < '1973-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1972_idx on hourly_1972(station, network, valid);
CREATE INDEX hourly_1972_valid_idx on hourly_1972(valid);
GRANT SELECT on hourly_1972 to nobody,apache;
    

create table hourly_1973( 
  CONSTRAINT __hourly_1973_check 
  CHECK(valid >= '1973-01-01 00:00+00'::timestamptz 
        and valid < '1974-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1973_idx on hourly_1973(station, network, valid);
CREATE INDEX hourly_1973_valid_idx on hourly_1973(valid);
GRANT SELECT on hourly_1973 to nobody,apache;
    

create table hourly_1974( 
  CONSTRAINT __hourly_1974_check 
  CHECK(valid >= '1974-01-01 00:00+00'::timestamptz 
        and valid < '1975-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1974_idx on hourly_1974(station, network, valid);
CREATE INDEX hourly_1974_valid_idx on hourly_1974(valid);
GRANT SELECT on hourly_1974 to nobody,apache;
    

create table hourly_1975( 
  CONSTRAINT __hourly_1975_check 
  CHECK(valid >= '1975-01-01 00:00+00'::timestamptz 
        and valid < '1976-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1975_idx on hourly_1975(station, network, valid);
CREATE INDEX hourly_1975_valid_idx on hourly_1975(valid);
GRANT SELECT on hourly_1975 to nobody,apache;
    

create table hourly_1976( 
  CONSTRAINT __hourly_1976_check 
  CHECK(valid >= '1976-01-01 00:00+00'::timestamptz 
        and valid < '1977-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1976_idx on hourly_1976(station, network, valid);
CREATE INDEX hourly_1976_valid_idx on hourly_1976(valid);
GRANT SELECT on hourly_1976 to nobody,apache;
    

create table hourly_1977( 
  CONSTRAINT __hourly_1977_check 
  CHECK(valid >= '1977-01-01 00:00+00'::timestamptz 
        and valid < '1978-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1977_idx on hourly_1977(station, network, valid);
CREATE INDEX hourly_1977_valid_idx on hourly_1977(valid);
GRANT SELECT on hourly_1977 to nobody,apache;
    

create table hourly_1978( 
  CONSTRAINT __hourly_1978_check 
  CHECK(valid >= '1978-01-01 00:00+00'::timestamptz 
        and valid < '1979-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1978_idx on hourly_1978(station, network, valid);
CREATE INDEX hourly_1978_valid_idx on hourly_1978(valid);
GRANT SELECT on hourly_1978 to nobody,apache;
    

create table hourly_1979( 
  CONSTRAINT __hourly_1979_check 
  CHECK(valid >= '1979-01-01 00:00+00'::timestamptz 
        and valid < '1980-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1979_idx on hourly_1979(station, network, valid);
CREATE INDEX hourly_1979_valid_idx on hourly_1979(valid);
GRANT SELECT on hourly_1979 to nobody,apache;
    

create table hourly_1980( 
  CONSTRAINT __hourly_1980_check 
  CHECK(valid >= '1980-01-01 00:00+00'::timestamptz 
        and valid < '1981-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1980_idx on hourly_1980(station, network, valid);
CREATE INDEX hourly_1980_valid_idx on hourly_1980(valid);
GRANT SELECT on hourly_1980 to nobody,apache;
    

create table hourly_1981( 
  CONSTRAINT __hourly_1981_check 
  CHECK(valid >= '1981-01-01 00:00+00'::timestamptz 
        and valid < '1982-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1981_idx on hourly_1981(station, network, valid);
CREATE INDEX hourly_1981_valid_idx on hourly_1981(valid);
GRANT SELECT on hourly_1981 to nobody,apache;
    

create table hourly_1982( 
  CONSTRAINT __hourly_1982_check 
  CHECK(valid >= '1982-01-01 00:00+00'::timestamptz 
        and valid < '1983-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1982_idx on hourly_1982(station, network, valid);
CREATE INDEX hourly_1982_valid_idx on hourly_1982(valid);
GRANT SELECT on hourly_1982 to nobody,apache;
    

create table hourly_1983( 
  CONSTRAINT __hourly_1983_check 
  CHECK(valid >= '1983-01-01 00:00+00'::timestamptz 
        and valid < '1984-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1983_idx on hourly_1983(station, network, valid);
CREATE INDEX hourly_1983_valid_idx on hourly_1983(valid);
GRANT SELECT on hourly_1983 to nobody,apache;
    

create table hourly_1984( 
  CONSTRAINT __hourly_1984_check 
  CHECK(valid >= '1984-01-01 00:00+00'::timestamptz 
        and valid < '1985-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1984_idx on hourly_1984(station, network, valid);
CREATE INDEX hourly_1984_valid_idx on hourly_1984(valid);
GRANT SELECT on hourly_1984 to nobody,apache;
    

create table hourly_1985( 
  CONSTRAINT __hourly_1985_check 
  CHECK(valid >= '1985-01-01 00:00+00'::timestamptz 
        and valid < '1986-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1985_idx on hourly_1985(station, network, valid);
CREATE INDEX hourly_1985_valid_idx on hourly_1985(valid);
GRANT SELECT on hourly_1985 to nobody,apache;
    

create table hourly_1986( 
  CONSTRAINT __hourly_1986_check 
  CHECK(valid >= '1986-01-01 00:00+00'::timestamptz 
        and valid < '1987-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1986_idx on hourly_1986(station, network, valid);
CREATE INDEX hourly_1986_valid_idx on hourly_1986(valid);
GRANT SELECT on hourly_1986 to nobody,apache;
    

create table hourly_1987( 
  CONSTRAINT __hourly_1987_check 
  CHECK(valid >= '1987-01-01 00:00+00'::timestamptz 
        and valid < '1988-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1987_idx on hourly_1987(station, network, valid);
CREATE INDEX hourly_1987_valid_idx on hourly_1987(valid);
GRANT SELECT on hourly_1987 to nobody,apache;
    

create table hourly_1988( 
  CONSTRAINT __hourly_1988_check 
  CHECK(valid >= '1988-01-01 00:00+00'::timestamptz 
        and valid < '1989-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1988_idx on hourly_1988(station, network, valid);
CREATE INDEX hourly_1988_valid_idx on hourly_1988(valid);
GRANT SELECT on hourly_1988 to nobody,apache;
    

create table hourly_1989( 
  CONSTRAINT __hourly_1989_check 
  CHECK(valid >= '1989-01-01 00:00+00'::timestamptz 
        and valid < '1990-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1989_idx on hourly_1989(station, network, valid);
CREATE INDEX hourly_1989_valid_idx on hourly_1989(valid);
GRANT SELECT on hourly_1989 to nobody,apache;
    

create table hourly_1990( 
  CONSTRAINT __hourly_1990_check 
  CHECK(valid >= '1990-01-01 00:00+00'::timestamptz 
        and valid < '1991-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1990_idx on hourly_1990(station, network, valid);
CREATE INDEX hourly_1990_valid_idx on hourly_1990(valid);
GRANT SELECT on hourly_1990 to nobody,apache;
    

create table hourly_1991( 
  CONSTRAINT __hourly_1991_check 
  CHECK(valid >= '1991-01-01 00:00+00'::timestamptz 
        and valid < '1992-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1991_idx on hourly_1991(station, network, valid);
CREATE INDEX hourly_1991_valid_idx on hourly_1991(valid);
GRANT SELECT on hourly_1991 to nobody,apache;
    

create table hourly_1992( 
  CONSTRAINT __hourly_1992_check 
  CHECK(valid >= '1992-01-01 00:00+00'::timestamptz 
        and valid < '1993-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1992_idx on hourly_1992(station, network, valid);
CREATE INDEX hourly_1992_valid_idx on hourly_1992(valid);
GRANT SELECT on hourly_1992 to nobody,apache;
    

create table hourly_1993( 
  CONSTRAINT __hourly_1993_check 
  CHECK(valid >= '1993-01-01 00:00+00'::timestamptz 
        and valid < '1994-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1993_idx on hourly_1993(station, network, valid);
CREATE INDEX hourly_1993_valid_idx on hourly_1993(valid);
GRANT SELECT on hourly_1993 to nobody,apache;
    

create table hourly_1994( 
  CONSTRAINT __hourly_1994_check 
  CHECK(valid >= '1994-01-01 00:00+00'::timestamptz 
        and valid < '1995-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1994_idx on hourly_1994(station, network, valid);
CREATE INDEX hourly_1994_valid_idx on hourly_1994(valid);
GRANT SELECT on hourly_1994 to nobody,apache;
    

create table hourly_1995( 
  CONSTRAINT __hourly_1995_check 
  CHECK(valid >= '1995-01-01 00:00+00'::timestamptz 
        and valid < '1996-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1995_idx on hourly_1995(station, network, valid);
CREATE INDEX hourly_1995_valid_idx on hourly_1995(valid);
GRANT SELECT on hourly_1995 to nobody,apache;
    

create table hourly_1996( 
  CONSTRAINT __hourly_1996_check 
  CHECK(valid >= '1996-01-01 00:00+00'::timestamptz 
        and valid < '1997-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1996_idx on hourly_1996(station, network, valid);
CREATE INDEX hourly_1996_valid_idx on hourly_1996(valid);
GRANT SELECT on hourly_1996 to nobody,apache;
    

create table hourly_1997( 
  CONSTRAINT __hourly_1997_check 
  CHECK(valid >= '1997-01-01 00:00+00'::timestamptz 
        and valid < '1998-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1997_idx on hourly_1997(station, network, valid);
CREATE INDEX hourly_1997_valid_idx on hourly_1997(valid);
GRANT SELECT on hourly_1997 to nobody,apache;
    

create table hourly_1998( 
  CONSTRAINT __hourly_1998_check 
  CHECK(valid >= '1998-01-01 00:00+00'::timestamptz 
        and valid < '1999-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1998_idx on hourly_1998(station, network, valid);
CREATE INDEX hourly_1998_valid_idx on hourly_1998(valid);
GRANT SELECT on hourly_1998 to nobody,apache;
    

create table hourly_1999( 
  CONSTRAINT __hourly_1999_check 
  CHECK(valid >= '1999-01-01 00:00+00'::timestamptz 
        and valid < '2000-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_1999_idx on hourly_1999(station, network, valid);
CREATE INDEX hourly_1999_valid_idx on hourly_1999(valid);
GRANT SELECT on hourly_1999 to nobody,apache;
    

create table hourly_2000( 
  CONSTRAINT __hourly_2000_check 
  CHECK(valid >= '2000-01-01 00:00+00'::timestamptz 
        and valid < '2001-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2000_idx on hourly_2000(station, network, valid);
CREATE INDEX hourly_2000_valid_idx on hourly_2000(valid);
GRANT SELECT on hourly_2000 to nobody,apache;
    

create table hourly_2001( 
  CONSTRAINT __hourly_2001_check 
  CHECK(valid >= '2001-01-01 00:00+00'::timestamptz 
        and valid < '2002-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2001_idx on hourly_2001(station, network, valid);
CREATE INDEX hourly_2001_valid_idx on hourly_2001(valid);
GRANT SELECT on hourly_2001 to nobody,apache;
    

create table hourly_2002( 
  CONSTRAINT __hourly_2002_check 
  CHECK(valid >= '2002-01-01 00:00+00'::timestamptz 
        and valid < '2003-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2002_idx on hourly_2002(station, network, valid);
CREATE INDEX hourly_2002_valid_idx on hourly_2002(valid);
GRANT SELECT on hourly_2002 to nobody,apache;
    

create table hourly_2003( 
  CONSTRAINT __hourly_2003_check 
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz 
        and valid < '2004-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2003_idx on hourly_2003(station, network, valid);
CREATE INDEX hourly_2003_valid_idx on hourly_2003(valid);
GRANT SELECT on hourly_2003 to nobody,apache;
    

create table hourly_2004( 
  CONSTRAINT __hourly_2004_check 
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz 
        and valid < '2005-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2004_idx on hourly_2004(station, network, valid);
CREATE INDEX hourly_2004_valid_idx on hourly_2004(valid);
GRANT SELECT on hourly_2004 to nobody,apache;
    

create table hourly_2005( 
  CONSTRAINT __hourly_2005_check 
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz 
        and valid < '2006-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2005_idx on hourly_2005(station, network, valid);
CREATE INDEX hourly_2005_valid_idx on hourly_2005(valid);
GRANT SELECT on hourly_2005 to nobody,apache;
    

create table hourly_2006( 
  CONSTRAINT __hourly_2006_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz 
        and valid < '2007-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2006_idx on hourly_2006(station, network, valid);
CREATE INDEX hourly_2006_valid_idx on hourly_2006(valid);
GRANT SELECT on hourly_2006 to nobody,apache;
    

create table hourly_2007( 
  CONSTRAINT __hourly_2007_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz 
        and valid < '2008-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2007_idx on hourly_2007(station, network, valid);
CREATE INDEX hourly_2007_valid_idx on hourly_2007(valid);
GRANT SELECT on hourly_2007 to nobody,apache;
    

create table hourly_2008( 
  CONSTRAINT __hourly_2008_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2008_idx on hourly_2008(station, network, valid);
CREATE INDEX hourly_2008_valid_idx on hourly_2008(valid);
GRANT SELECT on hourly_2008 to nobody,apache;
    

create table hourly_2009( 
  CONSTRAINT __hourly_2009_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2009_idx on hourly_2009(station, network, valid);
CREATE INDEX hourly_2009_valid_idx on hourly_2009(valid);
GRANT SELECT on hourly_2009 to nobody,apache;
    

create table hourly_2010( 
  CONSTRAINT __hourly_2010_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2010_idx on hourly_2010(station, network, valid);
CREATE INDEX hourly_2010_valid_idx on hourly_2010(valid);
GRANT SELECT on hourly_2010 to nobody,apache;
    

create table hourly_2011( 
  CONSTRAINT __hourly_2011_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2011_idx on hourly_2011(station, network, valid);
CREATE INDEX hourly_2011_valid_idx on hourly_2011(valid);
GRANT SELECT on hourly_2011 to nobody,apache;
    

create table hourly_2012( 
  CONSTRAINT __hourly_2012_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2012_idx on hourly_2012(station, network, valid);
CREATE INDEX hourly_2012_valid_idx on hourly_2012(valid);
GRANT SELECT on hourly_2012 to nobody,apache;
    

create table hourly_2013( 
  CONSTRAINT __hourly_2013_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2013_idx on hourly_2013(station, network, valid);
CREATE INDEX hourly_2013_valid_idx on hourly_2013(valid);
GRANT SELECT on hourly_2013 to nobody,apache;

create table hourly_2014( 
  CONSTRAINT __hourly_2014_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2014_idx on hourly_2014(station, network, valid);
CREATE INDEX hourly_2014_valid_idx on hourly_2014(valid);
GRANT SELECT on hourly_2014 to nobody,apache;
CREATE RULE replace_hourly_2014 as 
    ON INSERT TO hourly_2014
   WHERE (EXISTS ( SELECT 1
           FROM hourly_2014
          WHERE hourly_2014.station::text = new.station::text 
          AND hourly_2014.network::text = new.network::text 
          AND hourly_2014.valid = new.valid)) DO INSTEAD  
         UPDATE hourly_2014 SET phour = new.phour
  WHERE hourly_2014.station::text = new.station::text AND 
  hourly_2014.network::text = new.network::text AND 
  hourly_2014.valid = new.valid;

CREATE RULE replace_hourly_2013 as 
    ON INSERT TO hourly_2013
   WHERE (EXISTS ( SELECT 1
           FROM hourly_2013
          WHERE hourly_2013.station::text = new.station::text 
          AND hourly_2013.network::text = new.network::text 
          AND hourly_2013.valid = new.valid)) DO INSTEAD  
         UPDATE hourly_2013 SET phour = new.phour
  WHERE hourly_2013.station::text = new.station::text AND 
  hourly_2013.network::text = new.network::text AND 
  hourly_2013.valid = new.valid;
---
---
create table summary_1941( 
  CONSTRAINT __summary_1941_check 
  CHECK(day >= '1941-01-01'::date 
        and day < '1942-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1941_day_idx on summary_1941(day);
CREATE INDEX summary_1941_iemid_day_idx on summary_1941(iemid, day);
GRANT SELECT on summary_1941 to nobody,apache;
    

create table summary_1942( 
  CONSTRAINT __summary_1942_check 
  CHECK(day >= '1942-01-01'::date 
        and day < '1943-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1942_day_idx on summary_1942(day);
CREATE INDEX summary_1942_iemid_day_idx on summary_1942(iemid, day);
GRANT SELECT on summary_1942 to nobody,apache;
    

create table summary_1943( 
  CONSTRAINT __summary_1943_check 
  CHECK(day >= '1943-01-01'::date 
        and day < '1944-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1943_day_idx on summary_1943(day);
CREATE INDEX summary_1943_iemid_day_idx on summary_1943(iemid, day);
GRANT SELECT on summary_1943 to nobody,apache;
    

create table summary_1944( 
  CONSTRAINT __summary_1944_check 
  CHECK(day >= '1944-01-01'::date 
        and day < '1945-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1944_day_idx on summary_1944(day);
CREATE INDEX summary_1944_iemid_day_idx on summary_1944(iemid, day);
GRANT SELECT on summary_1944 to nobody,apache;
    

create table summary_1945( 
  CONSTRAINT __summary_1945_check 
  CHECK(day >= '1945-01-01'::date 
        and day < '1946-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1945_day_idx on summary_1945(day);
CREATE INDEX summary_1945_iemid_day_idx on summary_1945(iemid, day);
GRANT SELECT on summary_1945 to nobody,apache;
    

create table summary_1946( 
  CONSTRAINT __summary_1946_check 
  CHECK(day >= '1946-01-01'::date 
        and day < '1947-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1946_day_idx on summary_1946(day);
CREATE INDEX summary_1946_iemid_day_idx on summary_1946(iemid, day);
GRANT SELECT on summary_1946 to nobody,apache;
    

create table summary_1947( 
  CONSTRAINT __summary_1947_check 
  CHECK(day >= '1947-01-01'::date 
        and day < '1948-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1947_day_idx on summary_1947(day);
CREATE INDEX summary_1947_iemid_day_idx on summary_1947(iemid, day);
GRANT SELECT on summary_1947 to nobody,apache;
    

create table summary_1948( 
  CONSTRAINT __summary_1948_check 
  CHECK(day >= '1948-01-01'::date 
        and day < '1949-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1948_day_idx on summary_1948(day);
CREATE INDEX summary_1948_iemid_day_idx on summary_1948(iemid, day);
GRANT SELECT on summary_1948 to nobody,apache;
    

create table summary_1949( 
  CONSTRAINT __summary_1949_check 
  CHECK(day >= '1949-01-01'::date 
        and day < '1950-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1949_day_idx on summary_1949(day);
CREATE INDEX summary_1949_iemid_day_idx on summary_1949(iemid, day);
GRANT SELECT on summary_1949 to nobody,apache;
    

create table summary_1950( 
  CONSTRAINT __summary_1950_check 
  CHECK(day >= '1950-01-01'::date 
        and day < '1951-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1950_day_idx on summary_1950(day);
CREATE INDEX summary_1950_iemid_day_idx on summary_1950(iemid, day);
GRANT SELECT on summary_1950 to nobody,apache;
    

create table summary_1951( 
  CONSTRAINT __summary_1951_check 
  CHECK(day >= '1951-01-01'::date 
        and day < '1952-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1951_day_idx on summary_1951(day);
CREATE INDEX summary_1951_iemid_day_idx on summary_1951(iemid, day);
GRANT SELECT on summary_1951 to nobody,apache;
    

create table summary_1952( 
  CONSTRAINT __summary_1952_check 
  CHECK(day >= '1952-01-01'::date 
        and day < '1953-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1952_day_idx on summary_1952(day);
CREATE INDEX summary_1952_iemid_day_idx on summary_1952(iemid, day);
GRANT SELECT on summary_1952 to nobody,apache;
    

create table summary_1953( 
  CONSTRAINT __summary_1953_check 
  CHECK(day >= '1953-01-01'::date 
        and day < '1954-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1953_day_idx on summary_1953(day);
CREATE INDEX summary_1953_iemid_day_idx on summary_1953(iemid, day);
GRANT SELECT on summary_1953 to nobody,apache;
    

create table summary_1954( 
  CONSTRAINT __summary_1954_check 
  CHECK(day >= '1954-01-01'::date 
        and day < '1955-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1954_day_idx on summary_1954(day);
CREATE INDEX summary_1954_iemid_day_idx on summary_1954(iemid, day);
GRANT SELECT on summary_1954 to nobody,apache;
    

create table summary_1955( 
  CONSTRAINT __summary_1955_check 
  CHECK(day >= '1955-01-01'::date 
        and day < '1956-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1955_day_idx on summary_1955(day);
CREATE INDEX summary_1955_iemid_day_idx on summary_1955(iemid, day);
GRANT SELECT on summary_1955 to nobody,apache;
    

create table summary_1956( 
  CONSTRAINT __summary_1956_check 
  CHECK(day >= '1956-01-01'::date 
        and day < '1957-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1956_day_idx on summary_1956(day);
CREATE INDEX summary_1956_iemid_day_idx on summary_1956(iemid, day);
GRANT SELECT on summary_1956 to nobody,apache;
    

create table summary_1957( 
  CONSTRAINT __summary_1957_check 
  CHECK(day >= '1957-01-01'::date 
        and day < '1958-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1957_day_idx on summary_1957(day);
CREATE INDEX summary_1957_iemid_day_idx on summary_1957(iemid, day);
GRANT SELECT on summary_1957 to nobody,apache;
    

create table summary_1958( 
  CONSTRAINT __summary_1958_check 
  CHECK(day >= '1958-01-01'::date 
        and day < '1959-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1958_day_idx on summary_1958(day);
CREATE INDEX summary_1958_iemid_day_idx on summary_1958(iemid, day);
GRANT SELECT on summary_1958 to nobody,apache;
    

create table summary_1959( 
  CONSTRAINT __summary_1959_check 
  CHECK(day >= '1959-01-01'::date 
        and day < '1960-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1959_day_idx on summary_1959(day);
CREATE INDEX summary_1959_iemid_day_idx on summary_1959(iemid, day);
GRANT SELECT on summary_1959 to nobody,apache;
    

create table summary_1960( 
  CONSTRAINT __summary_1960_check 
  CHECK(day >= '1960-01-01'::date 
        and day < '1961-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1960_day_idx on summary_1960(day);
CREATE INDEX summary_1960_iemid_day_idx on summary_1960(iemid, day);
GRANT SELECT on summary_1960 to nobody,apache;
    

create table summary_1961( 
  CONSTRAINT __summary_1961_check 
  CHECK(day >= '1961-01-01'::date 
        and day < '1962-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1961_day_idx on summary_1961(day);
CREATE INDEX summary_1961_iemid_day_idx on summary_1961(iemid, day);
GRANT SELECT on summary_1961 to nobody,apache;
    

create table summary_1962( 
  CONSTRAINT __summary_1962_check 
  CHECK(day >= '1962-01-01'::date 
        and day < '1963-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1962_day_idx on summary_1962(day);
CREATE INDEX summary_1962_iemid_day_idx on summary_1962(iemid, day);
GRANT SELECT on summary_1962 to nobody,apache;
    

create table summary_1963( 
  CONSTRAINT __summary_1963_check 
  CHECK(day >= '1963-01-01'::date 
        and day < '1964-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1963_day_idx on summary_1963(day);
CREATE INDEX summary_1963_iemid_day_idx on summary_1963(iemid, day);
GRANT SELECT on summary_1963 to nobody,apache;
    

create table summary_1964( 
  CONSTRAINT __summary_1964_check 
  CHECK(day >= '1964-01-01'::date 
        and day < '1965-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1964_day_idx on summary_1964(day);
CREATE INDEX summary_1964_iemid_day_idx on summary_1964(iemid, day);
GRANT SELECT on summary_1964 to nobody,apache;
    

create table summary_1965( 
  CONSTRAINT __summary_1965_check 
  CHECK(day >= '1965-01-01'::date 
        and day < '1966-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1965_day_idx on summary_1965(day);
CREATE INDEX summary_1965_iemid_day_idx on summary_1965(iemid, day);
GRANT SELECT on summary_1965 to nobody,apache;
    

create table summary_1966( 
  CONSTRAINT __summary_1966_check 
  CHECK(day >= '1966-01-01'::date 
        and day < '1967-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1966_day_idx on summary_1966(day);
CREATE INDEX summary_1966_iemid_day_idx on summary_1966(iemid, day);
GRANT SELECT on summary_1966 to nobody,apache;
    

create table summary_1967( 
  CONSTRAINT __summary_1967_check 
  CHECK(day >= '1967-01-01'::date 
        and day < '1968-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1967_day_idx on summary_1967(day);
CREATE INDEX summary_1967_iemid_day_idx on summary_1967(iemid, day);
GRANT SELECT on summary_1967 to nobody,apache;
    

create table summary_1968( 
  CONSTRAINT __summary_1968_check 
  CHECK(day >= '1968-01-01'::date 
        and day < '1969-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1968_day_idx on summary_1968(day);
CREATE INDEX summary_1968_iemid_day_idx on summary_1968(iemid, day);
GRANT SELECT on summary_1968 to nobody,apache;
    

create table summary_1969( 
  CONSTRAINT __summary_1969_check 
  CHECK(day >= '1969-01-01'::date 
        and day < '1970-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1969_day_idx on summary_1969(day);
CREATE INDEX summary_1969_iemid_day_idx on summary_1969(iemid, day);
GRANT SELECT on summary_1969 to nobody,apache;
    

create table summary_1970( 
  CONSTRAINT __summary_1970_check 
  CHECK(day >= '1970-01-01'::date 
        and day < '1971-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1970_day_idx on summary_1970(day);
CREATE INDEX summary_1970_iemid_day_idx on summary_1970(iemid, day);
GRANT SELECT on summary_1970 to nobody,apache;
    

create table summary_1971( 
  CONSTRAINT __summary_1971_check 
  CHECK(day >= '1971-01-01'::date 
        and day < '1972-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1971_day_idx on summary_1971(day);
CREATE INDEX summary_1971_iemid_day_idx on summary_1971(iemid, day);
GRANT SELECT on summary_1971 to nobody,apache;
    

create table summary_1972( 
  CONSTRAINT __summary_1972_check 
  CHECK(day >= '1972-01-01'::date 
        and day < '1973-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1972_day_idx on summary_1972(day);
CREATE INDEX summary_1972_iemid_day_idx on summary_1972(iemid, day);
GRANT SELECT on summary_1972 to nobody,apache;
    

create table summary_1973( 
  CONSTRAINT __summary_1973_check 
  CHECK(day >= '1973-01-01'::date 
        and day < '1974-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1973_day_idx on summary_1973(day);
CREATE INDEX summary_1973_iemid_day_idx on summary_1973(iemid, day);
GRANT SELECT on summary_1973 to nobody,apache;
    

create table summary_1974( 
  CONSTRAINT __summary_1974_check 
  CHECK(day >= '1974-01-01'::date 
        and day < '1975-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1974_day_idx on summary_1974(day);
CREATE INDEX summary_1974_iemid_day_idx on summary_1974(iemid, day);
GRANT SELECT on summary_1974 to nobody,apache;
    

create table summary_1975( 
  CONSTRAINT __summary_1975_check 
  CHECK(day >= '1975-01-01'::date 
        and day < '1976-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1975_day_idx on summary_1975(day);
CREATE INDEX summary_1975_iemid_day_idx on summary_1975(iemid, day);
GRANT SELECT on summary_1975 to nobody,apache;
    

create table summary_1976( 
  CONSTRAINT __summary_1976_check 
  CHECK(day >= '1976-01-01'::date 
        and day < '1977-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1976_day_idx on summary_1976(day);
CREATE INDEX summary_1976_iemid_day_idx on summary_1976(iemid, day);
GRANT SELECT on summary_1976 to nobody,apache;
    

create table summary_1977( 
  CONSTRAINT __summary_1977_check 
  CHECK(day >= '1977-01-01'::date 
        and day < '1978-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1977_day_idx on summary_1977(day);
CREATE INDEX summary_1977_iemid_day_idx on summary_1977(iemid, day);
GRANT SELECT on summary_1977 to nobody,apache;
    

create table summary_1978( 
  CONSTRAINT __summary_1978_check 
  CHECK(day >= '1978-01-01'::date 
        and day < '1979-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1978_day_idx on summary_1978(day);
CREATE INDEX summary_1978_iemid_day_idx on summary_1978(iemid, day);
GRANT SELECT on summary_1978 to nobody,apache;
    

create table summary_1979( 
  CONSTRAINT __summary_1979_check 
  CHECK(day >= '1979-01-01'::date 
        and day < '1980-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1979_day_idx on summary_1979(day);
CREATE INDEX summary_1979_iemid_day_idx on summary_1979(iemid, day);
GRANT SELECT on summary_1979 to nobody,apache;
    

create table summary_1980( 
  CONSTRAINT __summary_1980_check 
  CHECK(day >= '1980-01-01'::date 
        and day < '1981-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1980_day_idx on summary_1980(day);
CREATE INDEX summary_1980_iemid_day_idx on summary_1980(iemid, day);
GRANT SELECT on summary_1980 to nobody,apache;
    

create table summary_1981( 
  CONSTRAINT __summary_1981_check 
  CHECK(day >= '1981-01-01'::date 
        and day < '1982-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1981_day_idx on summary_1981(day);
CREATE INDEX summary_1981_iemid_day_idx on summary_1981(iemid, day);
GRANT SELECT on summary_1981 to nobody,apache;
    

create table summary_1982( 
  CONSTRAINT __summary_1982_check 
  CHECK(day >= '1982-01-01'::date 
        and day < '1983-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1982_day_idx on summary_1982(day);
CREATE INDEX summary_1982_iemid_day_idx on summary_1982(iemid, day);
GRANT SELECT on summary_1982 to nobody,apache;
    

create table summary_1983( 
  CONSTRAINT __summary_1983_check 
  CHECK(day >= '1983-01-01'::date 
        and day < '1984-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1983_day_idx on summary_1983(day);
CREATE INDEX summary_1983_iemid_day_idx on summary_1983(iemid, day);
GRANT SELECT on summary_1983 to nobody,apache;
    

create table summary_1984( 
  CONSTRAINT __summary_1984_check 
  CHECK(day >= '1984-01-01'::date 
        and day < '1985-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1984_day_idx on summary_1984(day);
CREATE INDEX summary_1984_iemid_day_idx on summary_1984(iemid, day);
GRANT SELECT on summary_1984 to nobody,apache;
    

create table summary_1985( 
  CONSTRAINT __summary_1985_check 
  CHECK(day >= '1985-01-01'::date 
        and day < '1986-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1985_day_idx on summary_1985(day);
CREATE INDEX summary_1985_iemid_day_idx on summary_1985(iemid, day);
GRANT SELECT on summary_1985 to nobody,apache;
    

create table summary_1986( 
  CONSTRAINT __summary_1986_check 
  CHECK(day >= '1986-01-01'::date 
        and day < '1987-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1986_day_idx on summary_1986(day);
CREATE INDEX summary_1986_iemid_day_idx on summary_1986(iemid, day);
GRANT SELECT on summary_1986 to nobody,apache;
    

create table summary_1987( 
  CONSTRAINT __summary_1987_check 
  CHECK(day >= '1987-01-01'::date 
        and day < '1988-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1987_day_idx on summary_1987(day);
CREATE INDEX summary_1987_iemid_day_idx on summary_1987(iemid, day);
GRANT SELECT on summary_1987 to nobody,apache;
    

create table summary_1988( 
  CONSTRAINT __summary_1988_check 
  CHECK(day >= '1988-01-01'::date 
        and day < '1989-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1988_day_idx on summary_1988(day);
CREATE INDEX summary_1988_iemid_day_idx on summary_1988(iemid, day);
GRANT SELECT on summary_1988 to nobody,apache;
    

create table summary_1989( 
  CONSTRAINT __summary_1989_check 
  CHECK(day >= '1989-01-01'::date 
        and day < '1990-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1989_day_idx on summary_1989(day);
CREATE INDEX summary_1989_iemid_day_idx on summary_1989(iemid, day);
GRANT SELECT on summary_1989 to nobody,apache;
    

create table summary_1990( 
  CONSTRAINT __summary_1990_check 
  CHECK(day >= '1990-01-01'::date 
        and day < '1991-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1990_day_idx on summary_1990(day);
CREATE INDEX summary_1990_iemid_day_idx on summary_1990(iemid, day);
GRANT SELECT on summary_1990 to nobody,apache;
    

create table summary_1991( 
  CONSTRAINT __summary_1991_check 
  CHECK(day >= '1991-01-01'::date 
        and day < '1992-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1991_day_idx on summary_1991(day);
CREATE INDEX summary_1991_iemid_day_idx on summary_1991(iemid, day);
GRANT SELECT on summary_1991 to nobody,apache;
    

create table summary_1992( 
  CONSTRAINT __summary_1992_check 
  CHECK(day >= '1992-01-01'::date 
        and day < '1993-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1992_day_idx on summary_1992(day);
CREATE INDEX summary_1992_iemid_day_idx on summary_1992(iemid, day);
GRANT SELECT on summary_1992 to nobody,apache;
    

create table summary_1993( 
  CONSTRAINT __summary_1993_check 
  CHECK(day >= '1993-01-01'::date 
        and day < '1994-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1993_day_idx on summary_1993(day);
CREATE INDEX summary_1993_iemid_day_idx on summary_1993(iemid, day);
GRANT SELECT on summary_1993 to nobody,apache;
    

create table summary_1994( 
  CONSTRAINT __summary_1994_check 
  CHECK(day >= '1994-01-01'::date 
        and day < '1995-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1994_day_idx on summary_1994(day);
CREATE INDEX summary_1994_iemid_day_idx on summary_1994(iemid, day);
GRANT SELECT on summary_1994 to nobody,apache;
    

create table summary_1995( 
  CONSTRAINT __summary_1995_check 
  CHECK(day >= '1995-01-01'::date 
        and day < '1996-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1995_day_idx on summary_1995(day);
CREATE INDEX summary_1995_iemid_day_idx on summary_1995(iemid, day);
GRANT SELECT on summary_1995 to nobody,apache;
    

create table summary_1996( 
  CONSTRAINT __summary_1996_check 
  CHECK(day >= '1996-01-01'::date 
        and day < '1997-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1996_day_idx on summary_1996(day);
CREATE INDEX summary_1996_iemid_day_idx on summary_1996(iemid, day);
GRANT SELECT on summary_1996 to nobody,apache;
    

create table summary_1997( 
  CONSTRAINT __summary_1997_check 
  CHECK(day >= '1997-01-01'::date 
        and day < '1998-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1997_day_idx on summary_1997(day);
CREATE INDEX summary_1997_iemid_day_idx on summary_1997(iemid, day);
GRANT SELECT on summary_1997 to nobody,apache;
    

create table summary_1998( 
  CONSTRAINT __summary_1998_check 
  CHECK(day >= '1998-01-01'::date 
        and day < '1999-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1998_day_idx on summary_1998(day);
CREATE INDEX summary_1998_iemid_day_idx on summary_1998(iemid, day);
GRANT SELECT on summary_1998 to nobody,apache;
    

create table summary_1999( 
  CONSTRAINT __summary_1999_check 
  CHECK(day >= '1999-01-01'::date 
        and day < '2000-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_1999_day_idx on summary_1999(day);
CREATE INDEX summary_1999_iemid_day_idx on summary_1999(iemid, day);
GRANT SELECT on summary_1999 to nobody,apache;
    

create table summary_2000( 
  CONSTRAINT __summary_2000_check 
  CHECK(day >= '2000-01-01'::date 
        and day < '2001-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2000_day_idx on summary_2000(day);
CREATE INDEX summary_2000_iemid_day_idx on summary_2000(iemid, day);
GRANT SELECT on summary_2000 to nobody,apache;
    

create table summary_2001( 
  CONSTRAINT __summary_2001_check 
  CHECK(day >= '2001-01-01'::date 
        and day < '2002-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2001_day_idx on summary_2001(day);
CREATE INDEX summary_2001_iemid_day_idx on summary_2001(iemid, day);
GRANT SELECT on summary_2001 to nobody,apache;
    

create table summary_2002( 
  CONSTRAINT __summary_2002_check 
  CHECK(day >= '2002-01-01'::date 
        and day < '2003-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2002_day_idx on summary_2002(day);
CREATE INDEX summary_2002_iemid_day_idx on summary_2002(iemid, day);
GRANT SELECT on summary_2002 to nobody,apache;
    

create table summary_2003( 
  CONSTRAINT __summary_2003_check 
  CHECK(day >= '2003-01-01'::date 
        and day < '2004-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2003_day_idx on summary_2003(day);
CREATE INDEX summary_2003_iemid_day_idx on summary_2003(iemid, day);
GRANT SELECT on summary_2003 to nobody,apache;
    

create table summary_2004( 
  CONSTRAINT __summary_2004_check 
  CHECK(day >= '2004-01-01'::date 
        and day < '2005-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2004_day_idx on summary_2004(day);
CREATE INDEX summary_2004_iemid_day_idx on summary_2004(iemid, day);
GRANT SELECT on summary_2004 to nobody,apache;
    

create table summary_2005( 
  CONSTRAINT __summary_2005_check 
  CHECK(day >= '2005-01-01'::date 
        and day < '2006-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2005_day_idx on summary_2005(day);
CREATE INDEX summary_2005_iemid_day_idx on summary_2005(iemid, day);
GRANT SELECT on summary_2005 to nobody,apache;
    

create table summary_2006( 
  CONSTRAINT __summary_2006_check 
  CHECK(day >= '2006-01-01'::date 
        and day < '2007-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2006_day_idx on summary_2006(day);
CREATE INDEX summary_2006_iemid_day_idx on summary_2006(iemid, day);
GRANT SELECT on summary_2006 to nobody,apache;
    

create table summary_2007( 
  CONSTRAINT __summary_2007_check 
  CHECK(day >= '2007-01-01'::date 
        and day < '2008-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2007_day_idx on summary_2007(day);
CREATE INDEX summary_2007_iemid_day_idx on summary_2007(iemid, day);
GRANT SELECT on summary_2007 to nobody,apache;
    

create table summary_2008( 
  CONSTRAINT __summary_2008_check 
  CHECK(day >= '2008-01-01'::date 
        and day < '2009-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2008_day_idx on summary_2008(day);
CREATE INDEX summary_2008_iemid_day_idx on summary_2008(iemid, day);
GRANT SELECT on summary_2008 to nobody,apache;
    

create table summary_2009( 
  CONSTRAINT __summary_2009_check 
  CHECK(day >= '2009-01-01'::date 
        and day < '2010-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2009_day_idx on summary_2009(day);
CREATE INDEX summary_2009_iemid_day_idx on summary_2009(iemid, day);
GRANT SELECT on summary_2009 to nobody,apache;
    

create table summary_2010( 
  CONSTRAINT __summary_2010_check 
  CHECK(day >= '2010-01-01'::date 
        and day < '2011-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2010_day_idx on summary_2010(day);
CREATE INDEX summary_2010_iemid_day_idx on summary_2010(iemid, day);
GRANT SELECT on summary_2010 to nobody,apache;
    

create table summary_2011( 
  CONSTRAINT __summary_2011_check 
  CHECK(day >= '2011-01-01'::date 
        and day < '2012-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2011_day_idx on summary_2011(day);
CREATE INDEX summary_2011_iemid_day_idx on summary_2011(iemid, day);
GRANT SELECT on summary_2011 to nobody,apache;
    

create table summary_2012( 
  CONSTRAINT __summary_2012_check 
  CHECK(day >= '2012-01-01'::date 
        and day < '2013-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2012_day_idx on summary_2012(day);
CREATE INDEX summary_2012_iemid_day_idx on summary_2012(iemid, day);
GRANT SELECT on summary_2012 to nobody,apache;
    

create table summary_2013( 
  CONSTRAINT __summary_2013_check 
  CHECK(day >= '2013-01-01'::date 
        and day < '2014-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2013_day_idx on summary_2013(day);
CREATE INDEX summary_2013_iemid_day_idx on summary_2013(iemid, day);
GRANT SELECT on summary_2013 to nobody,apache;


create table summary_2014( 
  CONSTRAINT __summary_2014_check 
  CHECK(day >= '2014-01-01'::date 
        and day < '2015-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2014_day_idx on summary_2014(day);
CREATE INDEX summary_2014_iemid_day_idx on summary_2014(iemid, day);
GRANT SELECT on summary_2014 to nobody,apache;
alter table summary_2014 alter max_tmpf set default -99;
alter table summary_2014 alter min_tmpf set default 99;
alter table summary_2014 alter max_sknt set default 0;
alter table summary_2014 alter max_gust set default 0;
alter table summary_2014 alter max_dwpf set default -99;
alter table summary_2014 alter min_dwpf set default 99;
alter table summary_2014 alter pday set default -99;
alter table summary_2014 alter pmonth set default -99;
alter table summary_2014 alter snoww set default -99;
alter table summary_2014 alter max_drct set default -99;
alter table summary_2014 add foreign key(iemid) references stations(iemid);

CREATE TABLE rwis_locations(
  id smallint UNIQUE,
  nwsli char(5)
);
grant select on rwis_locations to nobody,apache;

--
-- RWIS Deep Soil Probe Data
--
CREATE TABLE rwis_soil_data(
  location_id smallint references rwis_locations(id),
  sensor_id smallint,
  valid timestamp with time zone,
  temp real,
  moisture real
);
CREATE TABLE rwis_soil_data_log(
  location_id smallint references rwis_locations(id),
  sensor_id smallint,
  valid timestamp with time zone,
  temp real,
  moisture real
);

GRANT select on rwis_soil_data to apache,nobody;

CREATE FUNCTION rwis_soil_update_log() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
  BEGIN
   IF (NEW.valid != OLD.valid) THEN
     INSERT into rwis_soil_data_log 
        SELECT * from rwis_soil_data WHERE sensor_id = NEW.sensor_id
        and location_id = NEW.location_id;
   END IF;
   RETURN NEW;
  END
 $$;

CREATE TRIGGER rwis_soil_update_tigger
    AFTER UPDATE ON rwis_soil_data
    FOR EACH ROW
    EXECUTE PROCEDURE rwis_soil_update_log();

--
-- RWIS Traffic Data Storage
-- 
CREATE TABLE rwis_traffic_sensors(
  id SERIAL UNIQUE,
  location_id smallint references rwis_locations(id),
  lane_id smallint,
  name varchar(64)
);

CREATE OR REPLACE view rwis_traffic_meta AS 
  SELECT l.id as location_id, l.nwsli as nwsli, s.id as sensor_id,
  s.lane_id as lane_id
  FROM rwis_locations l, rwis_traffic_sensors s WHERE
  l.id = s.location_id;


CREATE TABLE rwis_traffic_data(
  sensor_id int references rwis_traffic_sensors(id),
  valid timestamp with time zone,
  avg_speed real,
  avg_headway real,
  normal_vol real,
  long_vol real,
  occupancy real
);

CREATE TABLE rwis_traffic_data_log(
  sensor_id int references rwis_traffic_sensors(id),
  valid timestamp with time zone,
  avg_speed real,
  avg_headway real,
  normal_vol real,
  long_vol real,
  occupancy real
);

CREATE FUNCTION rwis_traffic_update_log() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
  BEGIN
   IF (NEW.valid != OLD.valid) THEN
     INSERT into rwis_traffic_data_log 
        SELECT * from rwis_traffic_data WHERE sensor_id = NEW.sensor_id;
   END IF;
   RETURN NEW;
  END
 $$;

CREATE TRIGGER rwis_traffic_update_tigger
    AFTER UPDATE ON rwis_traffic_data
    FOR EACH ROW
    EXECUTE PROCEDURE rwis_traffic_update_log();


CREATE VIEW rwis_traffic AS 
  SELECT * from 
  rwis_traffic_sensors s, rwis_traffic_data d
  WHERE d.sensor_id = s.id;

GRANT SELECT on rwis_traffic_data to apache,nobody;
GRANT SELECT on rwis_traffic_data_log to apache,nobody;
GRANT SELECT on rwis_traffic_sensors to apache,nobody;
GRANT SELECT on rwis_traffic to apache,nobody;

INSERT into rwis_locations values (58, 'RPFI4');
INSERT into rwis_locations values (30, 'RMCI4');
INSERT into rwis_locations values (54, 'RSYI4');
INSERT into rwis_locations values (42, 'RSPI4');
INSERT into rwis_locations values (48, 'RWBI4');
INSERT into rwis_locations values (22, 'RGRI4');
INSERT into rwis_locations values (45, 'RURI4');
INSERT into rwis_locations values (43, 'RSLI4');
INSERT into rwis_locations values (60, 'RDNI4');
INSERT into rwis_locations values (61, 'RQCI4');
INSERT into rwis_locations values (57, 'RTMI4');
INSERT into rwis_locations values (49, 'RHAI4');
INSERT into rwis_locations values (52, 'RCRI4');
INSERT into rwis_locations values (53, 'RCFI4');
INSERT into rwis_locations values (02, 'RTNI4');
INSERT into rwis_locations values (03, 'RTOI4');
INSERT into rwis_locations values (00, 'RDAI4');
INSERT into rwis_locations values (01, 'RALI4');
INSERT into rwis_locations values (06, 'RAVI4');
INSERT into rwis_locations values (07, 'RBUI4');
INSERT into rwis_locations values (04, 'RAMI4');
INSERT into rwis_locations values (05, 'RAKI4');
INSERT into rwis_locations values (46, 'RWLI4');
INSERT into rwis_locations values (47, 'RWII4');
INSERT into rwis_locations values (08, 'RCAI4');
INSERT into rwis_locations values (09, 'RCDI4');
INSERT into rwis_locations values (28, 'RMQI4');
INSERT into rwis_locations values (29, 'RMTI4');
INSERT into rwis_locations values (40, 'RSGI4');
INSERT into rwis_locations values (41, 'RSCI4');
INSERT into rwis_locations values (59, 'RCTI4');
INSERT into rwis_locations values (51, 'RIGI4');
INSERT into rwis_locations values (24, 'RIOI4');
INSERT into rwis_locations values (56, 'RDYI4');
INSERT into rwis_locations values (25, 'RJFI4');
INSERT into rwis_locations values (39, 'RSDI4');
INSERT into rwis_locations values (26, 'RLEI4');
INSERT into rwis_locations values (27, 'RMNI4');
INSERT into rwis_locations values (20, 'RDBI4');
INSERT into rwis_locations values (38, 'RROI4');
INSERT into rwis_locations values (21, 'RFDI4');
INSERT into rwis_locations values (11, 'RCNI4');
INSERT into rwis_locations values (10, 'RCII4');
INSERT into rwis_locations values (13, 'RCEI4');
INSERT into rwis_locations values (12, 'RCBI4');
INSERT into rwis_locations values (15, 'RDCI4');
INSERT into rwis_locations values (14, 'RDVI4');
INSERT into rwis_locations values (17, 'RDMI4');
INSERT into rwis_locations values (16, 'RDSI4');
INSERT into rwis_locations values (19, 'RDWI4');
INSERT into rwis_locations values (18, 'RDEI4');
INSERT into rwis_locations values (31, 'RMVI4');
INSERT into rwis_locations values (23, 'RIAI4');
INSERT into rwis_locations values (37, 'RPLI4');
INSERT into rwis_locations values (36, 'ROTI4');
INSERT into rwis_locations values (35, 'ROSI4');
INSERT into rwis_locations values (34, 'RONI4');
INSERT into rwis_locations values (33, 'RNHI4');
INSERT into rwis_locations values (55, 'RBFI4');
INSERT into rwis_locations values (32, 'RMPI4');
INSERT into rwis_locations values (44, 'RTPI4');
INSERT into rwis_locations values (50, 'RSBI4');


CREATE FUNCTION dzvalid(timestamp with time zone) RETURNS date
    LANGUAGE sql IMMUTABLE
    AS $_$SET TIME ZONE 'GMT'; select date($1)$_$;

CREATE FUNCTION getskyc(character varying) RETURNS smallint
    LANGUAGE sql
    AS $_$select value from skycoverage where code = $1$_$;


CREATE FUNCTION local_date(timestamp with time zone) RETURNS date
    LANGUAGE sql IMMUTABLE
    AS $_$select date($1)$_$;

CREATE FUNCTION mdate(timestamp with time zone) RETURNS date
    LANGUAGE sql IMMUTABLE
    AS $_$select date($1)$_$;

CREATE FUNCTION zero_record(text) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
  BEGIN
    UPDATE current SET tmpf = NULL, dwpf = NULL, drct = NULL,
     sknt = NULL  WHERE station = $1;
    RETURN true;
  END;
$_$;

create table hourly_2015( 
  CONSTRAINT __hourly_2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2015_idx on hourly_2015(station, network, valid);
CREATE INDEX hourly_2015_valid_idx on hourly_2015(valid);
GRANT SELECT on hourly_2015 to nobody,apache;
CREATE RULE replace_hourly_2015 as 
    ON INSERT TO hourly_2015
   WHERE (EXISTS ( SELECT 1
           FROM hourly_2015
          WHERE hourly_2015.station::text = new.station::text 
          AND hourly_2015.network::text = new.network::text 
          AND hourly_2015.valid = new.valid)) DO INSTEAD  
         UPDATE hourly_2015 SET phour = new.phour
  WHERE hourly_2015.station::text = new.station::text AND 
  hourly_2015.network::text = new.network::text AND 
  hourly_2015.valid = new.valid;

create table summary_2015( 
  CONSTRAINT __summary_2015_check 
  CHECK(day >= '2015-01-01'::date 
        and day < '2016-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2015_day_idx on summary_2015(day);
CREATE INDEX summary_2015_iemid_day_idx on summary_2015(iemid, day);
GRANT SELECT on summary_2015 to nobody,apache;
alter table summary_2015 alter max_tmpf set default -99;
alter table summary_2015 alter min_tmpf set default 99;
alter table summary_2015 alter max_sknt set default 0;
alter table summary_2015 alter max_gust set default 0;
alter table summary_2015 alter max_dwpf set default -99;
alter table summary_2015 alter min_dwpf set default 99;
alter table summary_2015 alter pday set default -99;
alter table summary_2015 alter pmonth set default -99;
alter table summary_2015 alter snoww set default -99;
alter table summary_2015 alter max_drct set default -99;
alter table summary_2015 
  add foreign key(iemid)
  references stations(iemid) ON DELETE CASCADE;

  --
-- Set cascading deletes when an entry is removed from the stations table
--
ALTER TABLE current
  DROP CONSTRAINT current_iemid_fkey,
  ADD CONSTRAINT current_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE current_log
  DROP CONSTRAINT current_log_iemid_fkey,
  ADD CONSTRAINT current_log_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE current_qc
  DROP CONSTRAINT current_qc_iemid_fkey,
  ADD CONSTRAINT current_qc_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE current_tmp
  DROP CONSTRAINT current_tmp_iemid_fkey,
  ADD CONSTRAINT current_tmp_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE events
  DROP CONSTRAINT events_iemid_fkey,
  ADD CONSTRAINT events_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE hourly
  DROP CONSTRAINT hourly_iemid_fkey,
  ADD CONSTRAINT hourly_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE summary_2014
  DROP CONSTRAINT summary_2014_iemid_fkey,
  ADD CONSTRAINT summary_2014_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE summary_2015
  DROP CONSTRAINT summary_2015_iemid_fkey,
  ADD CONSTRAINT summary_2015_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE summary
  DROP CONSTRAINT summary_iemid_fkey,
  ADD CONSTRAINT summary_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE summary_1941
  ADD CONSTRAINT summary_1941_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1942
  ADD CONSTRAINT summary_1942_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1943
  ADD CONSTRAINT summary_1943_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1944
  ADD CONSTRAINT summary_1944_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1945
  ADD CONSTRAINT summary_1945_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1946
  ADD CONSTRAINT summary_1946_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1947
  ADD CONSTRAINT summary_1947_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1948
  ADD CONSTRAINT summary_1948_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1949
  ADD CONSTRAINT summary_1949_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1950
  ADD CONSTRAINT summary_1950_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1951
  ADD CONSTRAINT summary_1951_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1952
  ADD CONSTRAINT summary_1952_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1953
  ADD CONSTRAINT summary_1953_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1954
  ADD CONSTRAINT summary_1954_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1955
  ADD CONSTRAINT summary_1955_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1956
  ADD CONSTRAINT summary_1956_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1957
  ADD CONSTRAINT summary_1957_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1958
  ADD CONSTRAINT summary_1958_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1959
  ADD CONSTRAINT summary_1959_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1960
  ADD CONSTRAINT summary_1960_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1961
  ADD CONSTRAINT summary_1961_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1962
  ADD CONSTRAINT summary_1962_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1963
  ADD CONSTRAINT summary_1963_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1964
  ADD CONSTRAINT summary_1964_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1965
  ADD CONSTRAINT summary_1965_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1966
  ADD CONSTRAINT summary_1966_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1967
  ADD CONSTRAINT summary_1967_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1968
  ADD CONSTRAINT summary_1968_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1969
  ADD CONSTRAINT summary_1969_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1970
  ADD CONSTRAINT summary_1970_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1971
  ADD CONSTRAINT summary_1971_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1972
  ADD CONSTRAINT summary_1972_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1973
  ADD CONSTRAINT summary_1973_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1974
  ADD CONSTRAINT summary_1974_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1975
  ADD CONSTRAINT summary_1975_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1976
  ADD CONSTRAINT summary_1976_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1977
  ADD CONSTRAINT summary_1977_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1978
  ADD CONSTRAINT summary_1978_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1979
  ADD CONSTRAINT summary_1979_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1980
  ADD CONSTRAINT summary_1980_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1981
  ADD CONSTRAINT summary_1981_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1982
  ADD CONSTRAINT summary_1982_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1983
  ADD CONSTRAINT summary_1983_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1984
  ADD CONSTRAINT summary_1984_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1985
  ADD CONSTRAINT summary_1985_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1986
  ADD CONSTRAINT summary_1986_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1987
  ADD CONSTRAINT summary_1987_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1988
  ADD CONSTRAINT summary_1988_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1989
  ADD CONSTRAINT summary_1989_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1990
  ADD CONSTRAINT summary_1990_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1991
  ADD CONSTRAINT summary_1991_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1992
  ADD CONSTRAINT summary_1992_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1993
  ADD CONSTRAINT summary_1993_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1994
  ADD CONSTRAINT summary_1994_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

-- Create the 2016 tables while we are messing around here
create table hourly_2016( 
  CONSTRAINT __hourly_2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2016_idx on hourly_2016(station, network, valid);
CREATE INDEX hourly_2016_valid_idx on hourly_2016(valid);
GRANT SELECT on hourly_2016 to nobody,apache;
CREATE RULE replace_hourly_2016 as 
    ON INSERT TO hourly_2016
   WHERE (EXISTS ( SELECT 1
           FROM hourly_2016
          WHERE hourly_2016.station::text = new.station::text 
          AND hourly_2016.network::text = new.network::text 
          AND hourly_2016.valid = new.valid)) DO INSTEAD  
         UPDATE hourly_2016 SET phour = new.phour
  WHERE hourly_2016.station::text = new.station::text AND 
  hourly_2016.network::text = new.network::text AND 
  hourly_2016.valid = new.valid;

create table summary_2016( 
  CONSTRAINT __summary_2016_check 
  CHECK(day >= '2016-01-01'::date 
        and day < '2017-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2016_day_idx on summary_2016(day);
CREATE UNIQUE INDEX summary_2016_iemid_day_idx on summary_2016(iemid, day);
GRANT SELECT on summary_2016 to nobody,apache;
alter table summary_2016 
  add foreign key(iemid)
  references stations(iemid) ON DELETE CASCADE;

DO $$
DECLARE
  rec record;
BEGIN
FOR rec in SELECT generate_series(1928, 1940) as year LOOP
EXECUTE format('create table summary_'|| rec.year || '(
  CONSTRAINT __summary_'|| rec.year || '_check
  CHECK(day >= %L::date
        and day <= %L::date))
  INHERITS (summary)', rec.year || '-01-01', rec.year || '-12-31');
EXECUTE 'CREATE INDEX summary_'|| rec.year || '_day_idx on summary_'|| rec.year || '(day)';
EXECUTE 'CREATE UNIQUE INDEX summary_'|| rec.year || '_iemid_day_idx on summary_'|| rec.year || '(iemid, day)';
EXECUTE 'GRANT SELECT on summary_'|| rec.year || ' to nobody,apache';
EXECUTE 'alter table summary_'|| rec.year || '
  add foreign key(iemid)
  references stations(iemid) ON DELETE CASCADE';
END LOOP;
END$$;

-- Create the 2017 tables while we are messing around here
create table hourly_2017(
  CONSTRAINT __hourly_2017_check
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz
        and valid < '2018-01-01 00:00+00'::timestamptz))
  INHERITS (hourly);
CREATE INDEX hourly_2017_idx on hourly_2017(station, network, valid);
CREATE INDEX hourly_2017_valid_idx on hourly_2017(valid);
GRANT SELECT on hourly_2017 to nobody,apache;
CREATE RULE replace_hourly_2017 as
    ON INSERT TO hourly_2017
   WHERE (EXISTS ( SELECT 1
           FROM hourly_2017
          WHERE hourly_2017.station::text = new.station::text
          AND hourly_2017.network::text = new.network::text
          AND hourly_2017.valid = new.valid)) DO INSTEAD
         UPDATE hourly_2017 SET phour = new.phour
  WHERE hourly_2017.station::text = new.station::text AND
  hourly_2017.network::text = new.network::text AND
  hourly_2017.valid = new.valid;

create table summary_2017(
  CONSTRAINT __summary_2017_check
  CHECK(day >= '2017-01-01'::date
        and day < '2018-01-01'::date))
  INHERITS (summary);
CREATE INDEX summary_2017_day_idx on summary_2017(day);
CREATE UNIQUE INDEX summary_2017_iemid_day_idx on summary_2017(iemid, day);
GRANT SELECT on summary_2017 to nobody,apache;
alter table summary_2017
  add foreign key(iemid)
  references stations(iemid) ON DELETE CASCADE;

-- Create the 2018 tables while we are messing around here
create table hourly_2018(
  CONSTRAINT __hourly_2018_check
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (hourly);
CREATE INDEX hourly_2018_idx on hourly_2018(station, network, valid);
CREATE INDEX hourly_2018_valid_idx on hourly_2018(valid);
GRANT SELECT on hourly_2018 to nobody,apache;
CREATE RULE replace_hourly_2018 as
    ON INSERT TO hourly_2018
   WHERE (EXISTS ( SELECT 1
           FROM hourly_2018
          WHERE hourly_2018.station::text = new.station::text
          AND hourly_2018.network::text = new.network::text
          AND hourly_2018.valid = new.valid)) DO INSTEAD
         UPDATE hourly_2018 SET phour = new.phour
  WHERE hourly_2018.station::text = new.station::text AND
  hourly_2018.network::text = new.network::text AND
  hourly_2018.valid = new.valid;

create table summary_2018(
  CONSTRAINT __summary_2018_check
  CHECK(day >= '2018-01-01'::date
        and day < '2019-01-01'::date))
  INHERITS (summary);
CREATE INDEX summary_2018_day_idx on summary_2018(day);
CREATE UNIQUE INDEX summary_2018_iemid_day_idx on summary_2018(iemid, day);
GRANT SELECT on summary_2018 to nobody,apache;
alter table summary_2018
  add foreign key(iemid)
  references stations(iemid) ON DELETE CASCADE;

-- Create the 2019 tables while we are messing around here
create table hourly_2019(
  CONSTRAINT __hourly_2019_check
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (hourly);
CREATE INDEX hourly_2019_idx on hourly_2019(station, network, valid);
CREATE INDEX hourly_2019_valid_idx on hourly_2019(valid);
GRANT SELECT on hourly_2019 to nobody,apache;
CREATE RULE replace_hourly_2019 as
    ON INSERT TO hourly_2019
   WHERE (EXISTS ( SELECT 1
           FROM hourly_2019
          WHERE hourly_2019.station::text = new.station::text
          AND hourly_2019.network::text = new.network::text
          AND hourly_2019.valid = new.valid)) DO INSTEAD
         UPDATE hourly_2019 SET phour = new.phour
  WHERE hourly_2019.station::text = new.station::text AND
  hourly_2019.network::text = new.network::text AND
  hourly_2019.valid = new.valid;

create table summary_2019(
  CONSTRAINT __summary_2019_check
  CHECK(day >= '2019-01-01'::date
        and day < '2020-01-01'::date))
  INHERITS (summary);
CREATE INDEX summary_2019_day_idx on summary_2019(day);
CREATE UNIQUE INDEX summary_2019_iemid_day_idx on summary_2019(iemid, day);
GRANT SELECT on summary_2019 to nobody,apache;
alter table summary_2019
  add foreign key(iemid)
  references stations(iemid) ON DELETE CASCADE;
