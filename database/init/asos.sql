CREATE EXTENSION postgis;

-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (10, now());

---
--- Store unknown stations
---
CREATE TABLE unknown(
  id varchar(5),
  valid timestamptz
);

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


CREATE FUNCTION getskyc(character varying) RETURNS smallint
    LANGUAGE sql
    AS $_$select value from skycoverage where code = $1$_$;

---
--- One Minute ASOS data
---
CREATE TABLE alldata_1minute(
  station char(3),
  valid timestamptz,
  vis1_coeff real,
  vis1_nd char(1),
  vis2_coeff real,
  vis2_nd char(1),
  drct smallint,
  sknt smallint,
  gust_drct smallint,
  gust_sknt smallint,
  ptype char(2),
  precip real,
  pres1 real,
  pres2 real,
  pres3 real,
  tmpf smallint,
  dwpf smallint
);
GRANT SELECT on alldata_1minute to nobody,apache;

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

-- Storage of Type of Observation this is
CREATE TABLE alldata_report_type(
  id smallint UNIQUE NOT NULL,
  label varchar);
GRANT SELECT on alldata_report_type to nobody,apache;

INSERT into alldata_report_type VALUES
        (0, 'Unknown'),
        (1, 'MADIS HFMETAR'),
        (2, 'Routine'),
        (3, 'Special');


CREATE TABLE alldata(
 station        character varying(4),    
 valid          timestamp with time zone,
 tmpf           real,          
 dwpf           real,          
 drct           real,        
 sknt           real,         
 alti           real,      
 gust           real,       
 vsby           real,      
 skyc1          character(3),     
 skyc2          character(3),    
 skyc3          character(3),   
 skyl1          integer,  
 skyl2          integer, 
 skyl3          integer,
 metar          character varying(256),
 skyc4          character(3),
 skyl4          integer,
 p03i           real,
 p06i           real,
 p24i           real,
 max_tmpf_6hr   real,
 min_tmpf_6hr   real,
 max_tmpf_24hr  real,
 min_tmpf_24hr  real,
 mslp           real,
 p01i           real,
 wxcodes        varchar(12)[],
  report_type smallint REFERENCES alldata_report_type(id),
  ice_accretion_1hr real,
  ice_accretion_3hr real,
  ice_accretion_6hr real,
  feel real,
  relh real,
  peak_wind_gust real,
  peak_wind_drct real,
  peak_wind_time timestamptz
);
GRANT SELECT on alldata to nobody,apache;

create table t1928( 
  CONSTRAINT __t1928_check 
  CHECK(valid >= '1928-01-01 00:00+00'::timestamptz 
        and valid < '1929-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1928_station_idx on t1928(station);
CREATE INDEX t1928_valid_idx on t1928(valid);
GRANT SELECT on t1928 to nobody,apache;
GRANT ALL on t1928 to ldm,mesonet;
    

create table t1929( 
  CONSTRAINT __t1929_check 
  CHECK(valid >= '1929-01-01 00:00+00'::timestamptz 
        and valid < '1930-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1929_station_idx on t1929(station);
CREATE INDEX t1929_valid_idx on t1929(valid);
GRANT SELECT on t1929 to nobody,apache;
GRANT ALL on t1929 to ldm,mesonet;
    

create table t1930( 
  CONSTRAINT __t1930_check 
  CHECK(valid >= '1930-01-01 00:00+00'::timestamptz 
        and valid < '1931-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1930_station_idx on t1930(station);
CREATE INDEX t1930_valid_idx on t1930(valid);
GRANT SELECT on t1930 to nobody,apache;
GRANT ALL on t1930 to ldm,mesonet;
    

create table t1931( 
  CONSTRAINT __t1931_check 
  CHECK(valid >= '1931-01-01 00:00+00'::timestamptz 
        and valid < '1932-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1931_station_idx on t1931(station);
CREATE INDEX t1931_valid_idx on t1931(valid);
GRANT SELECT on t1931 to nobody,apache;
GRANT ALL on t1931 to ldm,mesonet;
    

create table t1932( 
  CONSTRAINT __t1932_check 
  CHECK(valid >= '1932-01-01 00:00+00'::timestamptz 
        and valid < '1933-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1932_station_idx on t1932(station);
CREATE INDEX t1932_valid_idx on t1932(valid);
GRANT SELECT on t1932 to nobody,apache;
GRANT ALL on t1932 to ldm,mesonet;
    

create table t1933( 
  CONSTRAINT __t1933_check 
  CHECK(valid >= '1933-01-01 00:00+00'::timestamptz 
        and valid < '1934-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1933_station_idx on t1933(station);
CREATE INDEX t1933_valid_idx on t1933(valid);
GRANT SELECT on t1933 to nobody,apache;
GRANT ALL on t1933 to ldm,mesonet;
    

create table t1934( 
  CONSTRAINT __t1934_check 
  CHECK(valid >= '1934-01-01 00:00+00'::timestamptz 
        and valid < '1935-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1934_station_idx on t1934(station);
CREATE INDEX t1934_valid_idx on t1934(valid);
GRANT SELECT on t1934 to nobody,apache;
GRANT ALL on t1934 to ldm,mesonet;
    

create table t1935( 
  CONSTRAINT __t1935_check 
  CHECK(valid >= '1935-01-01 00:00+00'::timestamptz 
        and valid < '1936-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1935_station_idx on t1935(station);
CREATE INDEX t1935_valid_idx on t1935(valid);
GRANT SELECT on t1935 to nobody,apache;
GRANT ALL on t1935 to ldm,mesonet;
    

create table t1936( 
  CONSTRAINT __t1936_check 
  CHECK(valid >= '1936-01-01 00:00+00'::timestamptz 
        and valid < '1937-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1936_station_idx on t1936(station);
CREATE INDEX t1936_valid_idx on t1936(valid);
GRANT SELECT on t1936 to nobody,apache;
GRANT ALL on t1936 to ldm,mesonet;
    

create table t1937( 
  CONSTRAINT __t1937_check 
  CHECK(valid >= '1937-01-01 00:00+00'::timestamptz 
        and valid < '1938-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1937_station_idx on t1937(station);
CREATE INDEX t1937_valid_idx on t1937(valid);
GRANT SELECT on t1937 to nobody,apache;
GRANT ALL on t1937 to ldm,mesonet;
    

create table t1938( 
  CONSTRAINT __t1938_check 
  CHECK(valid >= '1938-01-01 00:00+00'::timestamptz 
        and valid < '1939-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1938_station_idx on t1938(station);
CREATE INDEX t1938_valid_idx on t1938(valid);
GRANT SELECT on t1938 to nobody,apache;
GRANT ALL on t1938 to ldm,mesonet;
    

create table t1939( 
  CONSTRAINT __t1939_check 
  CHECK(valid >= '1939-01-01 00:00+00'::timestamptz 
        and valid < '1940-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1939_station_idx on t1939(station);
CREATE INDEX t1939_valid_idx on t1939(valid);
GRANT SELECT on t1939 to nobody,apache;
GRANT ALL on t1939 to ldm,mesonet;
    

create table t1940( 
  CONSTRAINT __t1940_check 
  CHECK(valid >= '1940-01-01 00:00+00'::timestamptz 
        and valid < '1941-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1940_station_idx on t1940(station);
CREATE INDEX t1940_valid_idx on t1940(valid);
GRANT SELECT on t1940 to nobody,apache;
GRANT ALL on t1940 to ldm,mesonet;
    

create table t1941( 
  CONSTRAINT __t1941_check 
  CHECK(valid >= '1941-01-01 00:00+00'::timestamptz 
        and valid < '1942-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1941_station_idx on t1941(station);
CREATE INDEX t1941_valid_idx on t1941(valid);
GRANT SELECT on t1941 to nobody,apache;
GRANT ALL on t1941 to ldm,mesonet;
    

create table t1942( 
  CONSTRAINT __t1942_check 
  CHECK(valid >= '1942-01-01 00:00+00'::timestamptz 
        and valid < '1943-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1942_station_idx on t1942(station);
CREATE INDEX t1942_valid_idx on t1942(valid);
GRANT SELECT on t1942 to nobody,apache;
GRANT ALL on t1942 to ldm,mesonet;
    

create table t1943( 
  CONSTRAINT __t1943_check 
  CHECK(valid >= '1943-01-01 00:00+00'::timestamptz 
        and valid < '1944-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1943_station_idx on t1943(station);
CREATE INDEX t1943_valid_idx on t1943(valid);
GRANT SELECT on t1943 to nobody,apache;
GRANT ALL on t1943 to ldm,mesonet;
    

create table t1944( 
  CONSTRAINT __t1944_check 
  CHECK(valid >= '1944-01-01 00:00+00'::timestamptz 
        and valid < '1945-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1944_station_idx on t1944(station);
CREATE INDEX t1944_valid_idx on t1944(valid);
GRANT SELECT on t1944 to nobody,apache;
GRANT ALL on t1944 to ldm,mesonet;
    

create table t1945( 
  CONSTRAINT __t1945_check 
  CHECK(valid >= '1945-01-01 00:00+00'::timestamptz 
        and valid < '1946-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1945_station_idx on t1945(station);
CREATE INDEX t1945_valid_idx on t1945(valid);
GRANT SELECT on t1945 to nobody,apache;
GRANT ALL on t1945 to ldm,mesonet;
    

create table t1946( 
  CONSTRAINT __t1946_check 
  CHECK(valid >= '1946-01-01 00:00+00'::timestamptz 
        and valid < '1947-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1946_station_idx on t1946(station);
CREATE INDEX t1946_valid_idx on t1946(valid);
GRANT SELECT on t1946 to nobody,apache;
GRANT ALL on t1946 to ldm,mesonet;
    

create table t1947( 
  CONSTRAINT __t1947_check 
  CHECK(valid >= '1947-01-01 00:00+00'::timestamptz 
        and valid < '1948-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1947_station_idx on t1947(station);
CREATE INDEX t1947_valid_idx on t1947(valid);
GRANT SELECT on t1947 to nobody,apache;
GRANT ALL on t1947 to ldm,mesonet;
    

create table t1948( 
  CONSTRAINT __t1948_check 
  CHECK(valid >= '1948-01-01 00:00+00'::timestamptz 
        and valid < '1949-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1948_station_idx on t1948(station);
CREATE INDEX t1948_valid_idx on t1948(valid);
GRANT SELECT on t1948 to nobody,apache;
GRANT ALL on t1948 to ldm,mesonet;
    

create table t1949( 
  CONSTRAINT __t1949_check 
  CHECK(valid >= '1949-01-01 00:00+00'::timestamptz 
        and valid < '1950-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1949_station_idx on t1949(station);
CREATE INDEX t1949_valid_idx on t1949(valid);
GRANT SELECT on t1949 to nobody,apache;
GRANT ALL on t1949 to ldm,mesonet;
    

create table t1950( 
  CONSTRAINT __t1950_check 
  CHECK(valid >= '1950-01-01 00:00+00'::timestamptz 
        and valid < '1951-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1950_station_idx on t1950(station);
CREATE INDEX t1950_valid_idx on t1950(valid);
GRANT SELECT on t1950 to nobody,apache;
GRANT ALL on t1950 to ldm,mesonet;
    

create table t1951( 
  CONSTRAINT __t1951_check 
  CHECK(valid >= '1951-01-01 00:00+00'::timestamptz 
        and valid < '1952-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1951_station_idx on t1951(station);
CREATE INDEX t1951_valid_idx on t1951(valid);
GRANT SELECT on t1951 to nobody,apache;
GRANT ALL on t1951 to ldm,mesonet;
    

create table t1952( 
  CONSTRAINT __t1952_check 
  CHECK(valid >= '1952-01-01 00:00+00'::timestamptz 
        and valid < '1953-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1952_station_idx on t1952(station);
CREATE INDEX t1952_valid_idx on t1952(valid);
GRANT SELECT on t1952 to nobody,apache;
GRANT ALL on t1952 to ldm,mesonet;
    

create table t1953( 
  CONSTRAINT __t1953_check 
  CHECK(valid >= '1953-01-01 00:00+00'::timestamptz 
        and valid < '1954-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1953_station_idx on t1953(station);
CREATE INDEX t1953_valid_idx on t1953(valid);
GRANT SELECT on t1953 to nobody,apache;
GRANT ALL on t1953 to ldm,mesonet;
    

create table t1954( 
  CONSTRAINT __t1954_check 
  CHECK(valid >= '1954-01-01 00:00+00'::timestamptz 
        and valid < '1955-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1954_station_idx on t1954(station);
CREATE INDEX t1954_valid_idx on t1954(valid);
GRANT SELECT on t1954 to nobody,apache;
GRANT ALL on t1954 to ldm,mesonet;
    

create table t1955( 
  CONSTRAINT __t1955_check 
  CHECK(valid >= '1955-01-01 00:00+00'::timestamptz 
        and valid < '1956-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1955_station_idx on t1955(station);
CREATE INDEX t1955_valid_idx on t1955(valid);
GRANT SELECT on t1955 to nobody,apache;
GRANT ALL on t1955 to ldm,mesonet;
    

create table t1956( 
  CONSTRAINT __t1956_check 
  CHECK(valid >= '1956-01-01 00:00+00'::timestamptz 
        and valid < '1957-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1956_station_idx on t1956(station);
CREATE INDEX t1956_valid_idx on t1956(valid);
GRANT SELECT on t1956 to nobody,apache;
GRANT ALL on t1956 to ldm,mesonet;
    

create table t1957( 
  CONSTRAINT __t1957_check 
  CHECK(valid >= '1957-01-01 00:00+00'::timestamptz 
        and valid < '1958-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1957_station_idx on t1957(station);
CREATE INDEX t1957_valid_idx on t1957(valid);
GRANT SELECT on t1957 to nobody,apache;
GRANT ALL on t1957 to ldm,mesonet;
    

create table t1958( 
  CONSTRAINT __t1958_check 
  CHECK(valid >= '1958-01-01 00:00+00'::timestamptz 
        and valid < '1959-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1958_station_idx on t1958(station);
CREATE INDEX t1958_valid_idx on t1958(valid);
GRANT SELECT on t1958 to nobody,apache;
GRANT ALL on t1958 to ldm,mesonet;
    

create table t1959( 
  CONSTRAINT __t1959_check 
  CHECK(valid >= '1959-01-01 00:00+00'::timestamptz 
        and valid < '1960-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1959_station_idx on t1959(station);
CREATE INDEX t1959_valid_idx on t1959(valid);
GRANT SELECT on t1959 to nobody,apache;
GRANT ALL on t1959 to ldm,mesonet;
    

create table t1960( 
  CONSTRAINT __t1960_check 
  CHECK(valid >= '1960-01-01 00:00+00'::timestamptz 
        and valid < '1961-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1960_station_idx on t1960(station);
CREATE INDEX t1960_valid_idx on t1960(valid);
GRANT SELECT on t1960 to nobody,apache;
GRANT ALL on t1960 to ldm,mesonet;
    

create table t1961( 
  CONSTRAINT __t1961_check 
  CHECK(valid >= '1961-01-01 00:00+00'::timestamptz 
        and valid < '1962-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1961_station_idx on t1961(station);
CREATE INDEX t1961_valid_idx on t1961(valid);
GRANT SELECT on t1961 to nobody,apache;
GRANT ALL on t1961 to ldm,mesonet;
    

create table t1962( 
  CONSTRAINT __t1962_check 
  CHECK(valid >= '1962-01-01 00:00+00'::timestamptz 
        and valid < '1963-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1962_station_idx on t1962(station);
CREATE INDEX t1962_valid_idx on t1962(valid);
GRANT SELECT on t1962 to nobody,apache;
GRANT ALL on t1962 to ldm,mesonet;
    

create table t1963( 
  CONSTRAINT __t1963_check 
  CHECK(valid >= '1963-01-01 00:00+00'::timestamptz 
        and valid < '1964-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1963_station_idx on t1963(station);
CREATE INDEX t1963_valid_idx on t1963(valid);
GRANT SELECT on t1963 to nobody,apache;
GRANT ALL on t1963 to ldm,mesonet;
    

create table t1964( 
  CONSTRAINT __t1964_check 
  CHECK(valid >= '1964-01-01 00:00+00'::timestamptz 
        and valid < '1965-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1964_station_idx on t1964(station);
CREATE INDEX t1964_valid_idx on t1964(valid);
GRANT SELECT on t1964 to nobody,apache;
GRANT ALL on t1964 to ldm,mesonet;
    

create table t1965( 
  CONSTRAINT __t1965_check 
  CHECK(valid >= '1965-01-01 00:00+00'::timestamptz 
        and valid < '1966-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1965_station_idx on t1965(station);
CREATE INDEX t1965_valid_idx on t1965(valid);
GRANT SELECT on t1965 to nobody,apache;
GRANT ALL on t1965 to ldm,mesonet;
    

create table t1966( 
  CONSTRAINT __t1966_check 
  CHECK(valid >= '1966-01-01 00:00+00'::timestamptz 
        and valid < '1967-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1966_station_idx on t1966(station);
CREATE INDEX t1966_valid_idx on t1966(valid);
GRANT SELECT on t1966 to nobody,apache;
GRANT ALL on t1966 to ldm,mesonet;
    

create table t1967( 
  CONSTRAINT __t1967_check 
  CHECK(valid >= '1967-01-01 00:00+00'::timestamptz 
        and valid < '1968-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1967_station_idx on t1967(station);
CREATE INDEX t1967_valid_idx on t1967(valid);
GRANT SELECT on t1967 to nobody,apache;
GRANT ALL on t1967 to ldm,mesonet;
    

create table t1968( 
  CONSTRAINT __t1968_check 
  CHECK(valid >= '1968-01-01 00:00+00'::timestamptz 
        and valid < '1969-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1968_station_idx on t1968(station);
CREATE INDEX t1968_valid_idx on t1968(valid);
GRANT SELECT on t1968 to nobody,apache;
GRANT ALL on t1968 to ldm,mesonet;
    

create table t1969( 
  CONSTRAINT __t1969_check 
  CHECK(valid >= '1969-01-01 00:00+00'::timestamptz 
        and valid < '1970-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1969_station_idx on t1969(station);
CREATE INDEX t1969_valid_idx on t1969(valid);
GRANT SELECT on t1969 to nobody,apache;
GRANT ALL on t1969 to ldm,mesonet;
    

create table t1970( 
  CONSTRAINT __t1970_check 
  CHECK(valid >= '1970-01-01 00:00+00'::timestamptz 
        and valid < '1971-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1970_station_idx on t1970(station);
CREATE INDEX t1970_valid_idx on t1970(valid);
GRANT SELECT on t1970 to nobody,apache;
GRANT ALL on t1970 to ldm,mesonet;
    

create table t1971( 
  CONSTRAINT __t1971_check 
  CHECK(valid >= '1971-01-01 00:00+00'::timestamptz 
        and valid < '1972-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1971_station_idx on t1971(station);
CREATE INDEX t1971_valid_idx on t1971(valid);
GRANT SELECT on t1971 to nobody,apache;
GRANT ALL on t1971 to ldm,mesonet;
    

create table t1972( 
  CONSTRAINT __t1972_check 
  CHECK(valid >= '1972-01-01 00:00+00'::timestamptz 
        and valid < '1973-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1972_station_idx on t1972(station);
CREATE INDEX t1972_valid_idx on t1972(valid);
GRANT SELECT on t1972 to nobody,apache;
GRANT ALL on t1972 to ldm,mesonet;
    

create table t1973( 
  CONSTRAINT __t1973_check 
  CHECK(valid >= '1973-01-01 00:00+00'::timestamptz 
        and valid < '1974-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1973_station_idx on t1973(station);
CREATE INDEX t1973_valid_idx on t1973(valid);
GRANT SELECT on t1973 to nobody,apache;
GRANT ALL on t1973 to ldm,mesonet;
    

create table t1974( 
  CONSTRAINT __t1974_check 
  CHECK(valid >= '1974-01-01 00:00+00'::timestamptz 
        and valid < '1975-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1974_station_idx on t1974(station);
CREATE INDEX t1974_valid_idx on t1974(valid);
GRANT SELECT on t1974 to nobody,apache;
GRANT ALL on t1974 to ldm,mesonet;
    

create table t1975( 
  CONSTRAINT __t1975_check 
  CHECK(valid >= '1975-01-01 00:00+00'::timestamptz 
        and valid < '1976-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1975_station_idx on t1975(station);
CREATE INDEX t1975_valid_idx on t1975(valid);
GRANT SELECT on t1975 to nobody,apache;
GRANT ALL on t1975 to ldm,mesonet;
    

create table t1976( 
  CONSTRAINT __t1976_check 
  CHECK(valid >= '1976-01-01 00:00+00'::timestamptz 
        and valid < '1977-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1976_station_idx on t1976(station);
CREATE INDEX t1976_valid_idx on t1976(valid);
GRANT SELECT on t1976 to nobody,apache;
GRANT ALL on t1976 to ldm,mesonet;
    

create table t1977( 
  CONSTRAINT __t1977_check 
  CHECK(valid >= '1977-01-01 00:00+00'::timestamptz 
        and valid < '1978-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1977_station_idx on t1977(station);
CREATE INDEX t1977_valid_idx on t1977(valid);
GRANT SELECT on t1977 to nobody,apache;
GRANT ALL on t1977 to ldm,mesonet;
    

create table t1978( 
  CONSTRAINT __t1978_check 
  CHECK(valid >= '1978-01-01 00:00+00'::timestamptz 
        and valid < '1979-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1978_station_idx on t1978(station);
CREATE INDEX t1978_valid_idx on t1978(valid);
GRANT SELECT on t1978 to nobody,apache;
GRANT ALL on t1978 to ldm,mesonet;
    

create table t1979( 
  CONSTRAINT __t1979_check 
  CHECK(valid >= '1979-01-01 00:00+00'::timestamptz 
        and valid < '1980-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1979_station_idx on t1979(station);
CREATE INDEX t1979_valid_idx on t1979(valid);
GRANT SELECT on t1979 to nobody,apache;
GRANT ALL on t1979 to ldm,mesonet;
    

create table t1980( 
  CONSTRAINT __t1980_check 
  CHECK(valid >= '1980-01-01 00:00+00'::timestamptz 
        and valid < '1981-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1980_station_idx on t1980(station);
CREATE INDEX t1980_valid_idx on t1980(valid);
GRANT SELECT on t1980 to nobody,apache;
GRANT ALL on t1980 to ldm,mesonet;
    

create table t1981( 
  CONSTRAINT __t1981_check 
  CHECK(valid >= '1981-01-01 00:00+00'::timestamptz 
        and valid < '1982-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1981_station_idx on t1981(station);
CREATE INDEX t1981_valid_idx on t1981(valid);
GRANT SELECT on t1981 to nobody,apache;
GRANT ALL on t1981 to ldm,mesonet;
    

create table t1982( 
  CONSTRAINT __t1982_check 
  CHECK(valid >= '1982-01-01 00:00+00'::timestamptz 
        and valid < '1983-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1982_station_idx on t1982(station);
CREATE INDEX t1982_valid_idx on t1982(valid);
GRANT SELECT on t1982 to nobody,apache;
GRANT ALL on t1982 to ldm,mesonet;
    

create table t1983( 
  CONSTRAINT __t1983_check 
  CHECK(valid >= '1983-01-01 00:00+00'::timestamptz 
        and valid < '1984-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1983_station_idx on t1983(station);
CREATE INDEX t1983_valid_idx on t1983(valid);
GRANT SELECT on t1983 to nobody,apache;
GRANT ALL on t1983 to ldm,mesonet;
    

create table t1984( 
  CONSTRAINT __t1984_check 
  CHECK(valid >= '1984-01-01 00:00+00'::timestamptz 
        and valid < '1985-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1984_station_idx on t1984(station);
CREATE INDEX t1984_valid_idx on t1984(valid);
GRANT SELECT on t1984 to nobody,apache;
GRANT ALL on t1984 to ldm,mesonet;
    

create table t1985( 
  CONSTRAINT __t1985_check 
  CHECK(valid >= '1985-01-01 00:00+00'::timestamptz 
        and valid < '1986-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1985_station_idx on t1985(station);
CREATE INDEX t1985_valid_idx on t1985(valid);
GRANT SELECT on t1985 to nobody,apache;
GRANT ALL on t1985 to ldm,mesonet;
    

create table t1986( 
  CONSTRAINT __t1986_check 
  CHECK(valid >= '1986-01-01 00:00+00'::timestamptz 
        and valid < '1987-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1986_station_idx on t1986(station);
CREATE INDEX t1986_valid_idx on t1986(valid);
GRANT SELECT on t1986 to nobody,apache;
GRANT ALL on t1986 to ldm,mesonet;
    

create table t1987( 
  CONSTRAINT __t1987_check 
  CHECK(valid >= '1987-01-01 00:00+00'::timestamptz 
        and valid < '1988-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1987_station_idx on t1987(station);
CREATE INDEX t1987_valid_idx on t1987(valid);
GRANT SELECT on t1987 to nobody,apache;
GRANT ALL on t1987 to ldm,mesonet;
    

create table t1988( 
  CONSTRAINT __t1988_check 
  CHECK(valid >= '1988-01-01 00:00+00'::timestamptz 
        and valid < '1989-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1988_station_idx on t1988(station);
CREATE INDEX t1988_valid_idx on t1988(valid);
GRANT SELECT on t1988 to nobody,apache;
GRANT ALL on t1988 to ldm,mesonet;
    

create table t1989( 
  CONSTRAINT __t1989_check 
  CHECK(valid >= '1989-01-01 00:00+00'::timestamptz 
        and valid < '1990-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1989_station_idx on t1989(station);
CREATE INDEX t1989_valid_idx on t1989(valid);
GRANT SELECT on t1989 to nobody,apache;
GRANT ALL on t1989 to ldm,mesonet;
    

create table t1990( 
  CONSTRAINT __t1990_check 
  CHECK(valid >= '1990-01-01 00:00+00'::timestamptz 
        and valid < '1991-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1990_station_idx on t1990(station);
CREATE INDEX t1990_valid_idx on t1990(valid);
GRANT SELECT on t1990 to nobody,apache;
GRANT ALL on t1990 to ldm,mesonet;
    

create table t1991( 
  CONSTRAINT __t1991_check 
  CHECK(valid >= '1991-01-01 00:00+00'::timestamptz 
        and valid < '1992-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1991_station_idx on t1991(station);
CREATE INDEX t1991_valid_idx on t1991(valid);
GRANT SELECT on t1991 to nobody,apache;
GRANT ALL on t1991 to ldm,mesonet;
    

create table t1992( 
  CONSTRAINT __t1992_check 
  CHECK(valid >= '1992-01-01 00:00+00'::timestamptz 
        and valid < '1993-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1992_station_idx on t1992(station);
CREATE INDEX t1992_valid_idx on t1992(valid);
GRANT SELECT on t1992 to nobody,apache;
GRANT ALL on t1992 to ldm,mesonet;
    

create table t1993( 
  CONSTRAINT __t1993_check 
  CHECK(valid >= '1993-01-01 00:00+00'::timestamptz 
        and valid < '1994-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1993_station_idx on t1993(station);
CREATE INDEX t1993_valid_idx on t1993(valid);
GRANT SELECT on t1993 to nobody,apache;
GRANT ALL on t1993 to ldm,mesonet;
    

create table t1994( 
  CONSTRAINT __t1994_check 
  CHECK(valid >= '1994-01-01 00:00+00'::timestamptz 
        and valid < '1995-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1994_station_idx on t1994(station);
CREATE INDEX t1994_valid_idx on t1994(valid);
GRANT SELECT on t1994 to nobody,apache;
GRANT ALL on t1994 to ldm,mesonet;
    

create table t1995( 
  CONSTRAINT __t1995_check 
  CHECK(valid >= '1995-01-01 00:00+00'::timestamptz 
        and valid < '1996-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1995_station_idx on t1995(station);
CREATE INDEX t1995_valid_idx on t1995(valid);
GRANT SELECT on t1995 to nobody,apache;
GRANT ALL on t1995 to ldm,mesonet;
    

create table t1996( 
  CONSTRAINT __t1996_check 
  CHECK(valid >= '1996-01-01 00:00+00'::timestamptz 
        and valid < '1997-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1996_station_idx on t1996(station);
CREATE INDEX t1996_valid_idx on t1996(valid);
GRANT SELECT on t1996 to nobody,apache;
GRANT ALL on t1996 to ldm,mesonet;
    

create table t1997( 
  CONSTRAINT __t1997_check 
  CHECK(valid >= '1997-01-01 00:00+00'::timestamptz 
        and valid < '1998-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1997_station_idx on t1997(station);
CREATE INDEX t1997_valid_idx on t1997(valid);
GRANT SELECT on t1997 to nobody,apache;
GRANT ALL on t1997 to ldm,mesonet;
    

create table t1998( 
  CONSTRAINT __t1998_check 
  CHECK(valid >= '1998-01-01 00:00+00'::timestamptz 
        and valid < '1999-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1998_station_idx on t1998(station);
CREATE INDEX t1998_valid_idx on t1998(valid);
GRANT SELECT on t1998 to nobody,apache;
GRANT ALL on t1998 to ldm,mesonet;
    

create table t1999( 
  CONSTRAINT __t1999_check 
  CHECK(valid >= '1999-01-01 00:00+00'::timestamptz 
        and valid < '2000-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1999_station_idx on t1999(station);
CREATE INDEX t1999_valid_idx on t1999(valid);
GRANT SELECT on t1999 to nobody,apache;
GRANT ALL on t1999 to ldm,mesonet;
    

create table t2000( 
  CONSTRAINT __t2000_check 
  CHECK(valid >= '2000-01-01 00:00+00'::timestamptz 
        and valid < '2001-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_station_idx on t2000(station);
CREATE INDEX t2000_valid_idx on t2000(valid);
GRANT SELECT on t2000 to nobody,apache;
GRANT ALL on t2000 to ldm,mesonet;
    

create table t2001( 
  CONSTRAINT __t2001_check 
  CHECK(valid >= '2001-01-01 00:00+00'::timestamptz 
        and valid < '2002-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_station_idx on t2001(station);
CREATE INDEX t2001_valid_idx on t2001(valid);
GRANT SELECT on t2001 to nobody,apache;
GRANT ALL on t2001 to ldm,mesonet;
    

create table t2002( 
  CONSTRAINT __t2002_check 
  CHECK(valid >= '2002-01-01 00:00+00'::timestamptz 
        and valid < '2003-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_station_idx on t2002(station);
CREATE INDEX t2002_valid_idx on t2002(valid);
GRANT SELECT on t2002 to nobody,apache;
GRANT ALL on t2002 to ldm,mesonet;
    

create table t2003( 
  CONSTRAINT __t2003_check 
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz 
        and valid < '2004-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_station_idx on t2003(station);
CREATE INDEX t2003_valid_idx on t2003(valid);
GRANT SELECT on t2003 to nobody,apache;
GRANT ALL on t2003 to ldm,mesonet;
    

create table t2004( 
  CONSTRAINT __t2004_check 
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz 
        and valid < '2005-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_station_idx on t2004(station);
CREATE INDEX t2004_valid_idx on t2004(valid);
GRANT SELECT on t2004 to nobody,apache;
GRANT ALL on t2004 to ldm,mesonet;
    

create table t2005( 
  CONSTRAINT __t2005_check 
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz 
        and valid < '2006-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_station_idx on t2005(station);
CREATE INDEX t2005_valid_idx on t2005(valid);
GRANT SELECT on t2005 to nobody,apache;
GRANT ALL on t2005 to ldm,mesonet;
    

create table t2006( 
  CONSTRAINT __t2006_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz 
        and valid < '2007-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_station_idx on t2006(station);
CREATE INDEX t2006_valid_idx on t2006(valid);
GRANT SELECT on t2006 to nobody,apache;
GRANT ALL on t2006 to ldm,mesonet;
    

create table t2007( 
  CONSTRAINT __t2007_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz 
        and valid < '2008-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_station_idx on t2007(station);
CREATE INDEX t2007_valid_idx on t2007(valid);
GRANT SELECT on t2007 to nobody,apache;
GRANT ALL on t2007 to ldm,mesonet;
    

create table t2008( 
  CONSTRAINT __t2008_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_station_idx on t2008(station);
CREATE INDEX t2008_valid_idx on t2008(valid);
GRANT SELECT on t2008 to nobody,apache;
GRANT ALL on t2008 to ldm,mesonet;
    

create table t2009( 
  CONSTRAINT __t2009_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_station_idx on t2009(station);
CREATE INDEX t2009_valid_idx on t2009(valid);
GRANT SELECT on t2009 to nobody,apache;
GRANT ALL on t2009 to ldm,mesonet;
    

create table t2010( 
  CONSTRAINT __t2010_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_station_idx on t2010(station);
CREATE INDEX t2010_valid_idx on t2010(valid);
GRANT SELECT on t2010 to nobody,apache;
GRANT ALL on t2010 to ldm,mesonet;
    

create table t2011( 
  CONSTRAINT __t2011_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_station_idx on t2011(station);
CREATE INDEX t2011_valid_idx on t2011(valid);
GRANT SELECT on t2011 to nobody,apache;
GRANT ALL on t2011 to ldm,mesonet;
    

create table t2012( 
  CONSTRAINT __t2012_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_station_idx on t2012(station);
CREATE INDEX t2012_valid_idx on t2012(valid);
GRANT SELECT on t2012 to nobody,apache;
GRANT ALL on t2012 to ldm,mesonet;
    

create table t2013( 
  CONSTRAINT __t2013_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_station_idx on t2013(station);
CREATE INDEX t2013_valid_idx on t2013(valid);
GRANT SELECT on t2013 to nobody,apache;
GRANT ALL on t2013 to ldm,mesonet;
    

create table t2014( 
  CONSTRAINT __t2014_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_station_idx on t2014(station);
CREATE INDEX t2014_valid_idx on t2014(valid);
GRANT SELECT on t2014 to nobody,apache;
GRANT ALL on t2014 to ldm,mesonet;
    

create table t2015( 
  CONSTRAINT __t2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_station_idx on t2015(station);
CREATE INDEX t2015_valid_idx on t2015(valid);
GRANT SELECT on t2015 to nobody,apache;
GRANT ALL on t2015 to ldm,mesonet;
    

create table t2016( 
  CONSTRAINT __t2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_station_idx on t2016(station);
CREATE INDEX t2016_valid_idx on t2016(valid);
GRANT SELECT on t2016 to nobody,apache;
GRANT ALL on t2016 to ldm,mesonet;
    

create table t2017( 
  CONSTRAINT __t2017_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_station_idx on t2017(station);
CREATE INDEX t2017_valid_idx on t2017(valid);
GRANT SELECT on t2017 to nobody,apache;
GRANT ALL on t2017 to ldm,mesonet;

create table t2018( 
  CONSTRAINT __t2018_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz 
        and valid < '2019-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_station_idx on t2018(station);
CREATE INDEX t2018_valid_idx on t2018(valid);
GRANT SELECT on t2018 to nobody,apache;
GRANT ALL on t2018 to ldm,mesonet;

---
create table t2000_1minute( 
  CONSTRAINT __t2000_1minute_check 
  CHECK(valid >= '2000-01-01 00:00+00'::timestamptz 
        and valid < '2001-01-01 00:00+00')) 
  INHERITS (alldata_1minute);
CREATE INDEX t2000_1minte_station_idx on t2000_1minute(station);
CREATE INDEX t2000_1minute_valid_idx on t2000_1minute(valid);
GRANT SELECT on t2000_1minute to nobody,apache;

---
create table t2001_1minute(
  CONSTRAINT __t2001_1minute_check
  CHECK(valid >= '2001-01-01 00:00+00'::timestamptz
        and valid < '2002-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2001_1minte_station_idx on t2001_1minute(station);
CREATE INDEX t2001_1minute_valid_idx on t2001_1minute(valid);
GRANT SELECT on t2001_1minute to nobody,apache;
    

---
create table t2002_1minute(
  CONSTRAINT __t2002_1minute_check
  CHECK(valid >= '2002-01-01 00:00+00'::timestamptz
        and valid < '2003-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2002_1minte_station_idx on t2002_1minute(station);
CREATE INDEX t2002_1minute_valid_idx on t2002_1minute(valid);
GRANT SELECT on t2002_1minute to nobody,apache;
    

---
create table t2003_1minute(
  CONSTRAINT __t2003_1minute_check
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz
        and valid < '2004-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2003_1minte_station_idx on t2003_1minute(station);
CREATE INDEX t2003_1minute_valid_idx on t2003_1minute(valid);
GRANT SELECT on t2003_1minute to nobody,apache;
    

---
create table t2004_1minute(
  CONSTRAINT __t2004_1minute_check
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz
        and valid < '2005-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2004_1minte_station_idx on t2004_1minute(station);
CREATE INDEX t2004_1minute_valid_idx on t2004_1minute(valid);
GRANT SELECT on t2004_1minute to nobody,apache;
    

---
create table t2005_1minute(
  CONSTRAINT __t2005_1minute_check
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz
        and valid < '2006-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2005_1minte_station_idx on t2005_1minute(station);
CREATE INDEX t2005_1minute_valid_idx on t2005_1minute(valid);
GRANT SELECT on t2005_1minute to nobody,apache;
    

---
create table t2006_1minute(
  CONSTRAINT __t2006_1minute_check
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz
        and valid < '2007-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2006_1minte_station_idx on t2006_1minute(station);
CREATE INDEX t2006_1minute_valid_idx on t2006_1minute(valid);
GRANT SELECT on t2006_1minute to nobody,apache;
    

---
create table t2007_1minute(
  CONSTRAINT __t2007_1minute_check
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz
        and valid < '2008-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2007_1minte_station_idx on t2007_1minute(station);
CREATE INDEX t2007_1minute_valid_idx on t2007_1minute(valid);
GRANT SELECT on t2007_1minute to nobody,apache;
    

---
create table t2008_1minute(
  CONSTRAINT __t2008_1minute_check
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz
        and valid < '2009-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2008_1minte_station_idx on t2008_1minute(station);
CREATE INDEX t2008_1minute_valid_idx on t2008_1minute(valid);
GRANT SELECT on t2008_1minute to nobody,apache;
    

---
create table t2009_1minute(
  CONSTRAINT __t2009_1minute_check
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz
        and valid < '2010-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2009_1minte_station_idx on t2009_1minute(station);
CREATE INDEX t2009_1minute_valid_idx on t2009_1minute(valid);
GRANT SELECT on t2009_1minute to nobody,apache;
    

---
create table t2010_1minute(
  CONSTRAINT __t2010_1minute_check
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz
        and valid < '2011-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2010_1minte_station_idx on t2010_1minute(station);
CREATE INDEX t2010_1minute_valid_idx on t2010_1minute(valid);
GRANT SELECT on t2010_1minute to nobody,apache;
    

---
create table t2011_1minute(
  CONSTRAINT __t2011_1minute_check
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz
        and valid < '2012-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2011_1minte_station_idx on t2011_1minute(station);
CREATE INDEX t2011_1minute_valid_idx on t2011_1minute(valid);
GRANT SELECT on t2011_1minute to nobody,apache;
    

---
create table t2012_1minute(
  CONSTRAINT __t2012_1minute_check
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz
        and valid < '2013-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2012_1minte_station_idx on t2012_1minute(station);
CREATE INDEX t2012_1minute_valid_idx on t2012_1minute(valid);
GRANT SELECT on t2012_1minute to nobody,apache;
    

---
create table t2013_1minute(
  CONSTRAINT __t2013_1minute_check
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz
        and valid < '2014-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2013_1minte_station_idx on t2013_1minute(station);
CREATE INDEX t2013_1minute_valid_idx on t2013_1minute(valid);
GRANT SELECT on t2013_1minute to nobody,apache;
    

---
create table t2014_1minute(
  CONSTRAINT __t2014_1minute_check
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz
        and valid < '2015-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2014_1minte_station_idx on t2014_1minute(station);
CREATE INDEX t2014_1minute_valid_idx on t2014_1minute(valid);
GRANT SELECT on t2014_1minute to nobody,apache;
    

---
create table t2015_1minute(
  CONSTRAINT __t2015_1minute_check
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz
        and valid < '2016-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2015_1minte_station_idx on t2015_1minute(station);
CREATE INDEX t2015_1minute_valid_idx on t2015_1minute(valid);
GRANT SELECT on t2015_1minute to nobody,apache;
    

---
create table t2016_1minute(
  CONSTRAINT __t2016_1minute_check
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz
        and valid < '2017-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2016_1minte_station_idx on t2016_1minute(station);
CREATE INDEX t2016_1minute_valid_idx on t2016_1minute(valid);
GRANT SELECT on t2016_1minute to nobody,apache;
    

---
create table t2017_1minute(
  CONSTRAINT __t2017_1minute_check
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz
        and valid < '2018-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2017_1minte_station_idx on t2017_1minute(station);
CREATE INDEX t2017_1minute_valid_idx on t2017_1minute(valid);
GRANT SELECT on t2017_1minute to nobody,apache;
    

---
create table t2018_1minute(
  CONSTRAINT __t2018_1minute_check
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2018_1minte_station_idx on t2018_1minute(station);
CREATE INDEX t2018_1minute_valid_idx on t2018_1minute(valid);
GRANT SELECT on t2018_1minute to nobody,apache;


---
create table t2019( 
  CONSTRAINT __t2019_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz 
        and valid < '2020-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_station_idx on t2019(station);
CREATE INDEX t2019_valid_idx on t2019(valid);
GRANT SELECT on t2019 to nobody,apache;
GRANT ALL on t2019 to ldm,mesonet;

---
create table t2019_1minute(
  CONSTRAINT __t2019_1minute_check
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'))
  INHERITS (alldata_1minute);
CREATE INDEX t2019_1minte_station_idx on t2019_1minute(station);
CREATE INDEX t2019_1minute_valid_idx on t2019_1minute(valid);
GRANT SELECT on t2019_1minute to nobody,apache;
