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
	iemid int PRIMARY KEY,
	ncdc81 varchar(11)
	);
SELECT AddGeometryColumn('stations', 'geom', 4326, 'POINT', 2);
GRANT SELECT on stations to nobody,apache;

CREATE TABLE unknown(
	nwsli varchar(8),
	product varchar(64),
	network varchar(24)
);

---
---
---
CREATE TABLE raw2014(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2014 to nobody,apache;

create table raw2014_01( 
  CONSTRAINT __raw2014_01_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2014-02-01 00:00+00')) 
  INHERITS (raw2014);
CREATE INDEX raw2014_01_idx on raw2014_01(station, valid);
CREATE INDEX raw2014_01_valid_idx on raw2014_01(valid);
grant select on raw2014_01 to nobody,apache;

create table raw2014_02( 
  CONSTRAINT __raw2014_02_check 
  CHECK(valid >= '2014-02-01 00:00+00'::timestamptz 
        and valid < '2014-03-01 00:00+00')) 
  INHERITS (raw2014);
CREATE INDEX raw2014_02_idx on raw2014_02(station, valid);
CREATE INDEX raw2014_02_valid_idx on raw2014_02(valid);
grant select on raw2014_02 to nobody,apache;

create table raw2014_03( 
  CONSTRAINT __raw2014_03_check 
  CHECK(valid >= '2014-03-01 00:00+00'::timestamptz 
        and valid < '2014-04-01 00:00+00')) 
  INHERITS (raw2014);
CREATE INDEX raw2014_03_idx on raw2014_03(station, valid);
CREATE INDEX raw2014_03_valid_idx on raw2014_03(valid);
grant select on raw2014_03 to nobody,apache;

create table raw2014_04( 
  CONSTRAINT __raw2014_04_check 
  CHECK(valid >= '2014-04-01 00:00+00'::timestamptz 
        and valid < '2014-05-01 00:00+00')) 
  INHERITS (raw2014);
CREATE INDEX raw2014_04_idx on raw2014_04(station, valid);
CREATE INDEX raw2014_04_valid_idx on raw2014_04(valid);
grant select on raw2014_04 to nobody,apache;

create table raw2014_05( 
  CONSTRAINT __raw2014_05_check 
  CHECK(valid >= '2014-05-01 00:00+00'::timestamptz 
        and valid < '2014-06-01 00:00+00')) 
  INHERITS (raw2014);
CREATE INDEX raw2014_05_idx on raw2014_05(station, valid);
CREATE INDEX raw2014_05_valid_idx on raw2014_05(valid);
grant select on raw2014_05 to nobody,apache;

create table raw2014_06( 
  CONSTRAINT __raw2014_06_check 
  CHECK(valid >= '2014-06-01 00:00+00'::timestamptz 
        and valid < '2014-07-01 00:00+00')) 
  INHERITS (raw2014);
CREATE INDEX raw2014_06_idx on raw2014_06(station, valid);
CREATE INDEX raw2014_06_valid_idx on raw2014_06(valid);
grant select on raw2014_06 to nobody,apache;

create table raw2014_07( 
  CONSTRAINT __raw2014_07_check 
  CHECK(valid >= '2014-07-01 00:00+00'::timestamptz 
        and valid < '2014-08-01 00:00+00')) 
  INHERITS (raw2014);
CREATE INDEX raw2014_07_idx on raw2014_07(station, valid);
CREATE INDEX raw2014_07_valid_idx on raw2014_07(valid);
grant select on raw2014_07 to nobody,apache;

create table raw2014_08( 
  CONSTRAINT __raw2014_08_check 
  CHECK(valid >= '2014-08-01 00:00+00'::timestamptz 
        and valid < '2014-09-01 00:00+00')) 
  INHERITS (raw2014);
CREATE INDEX raw2014_08_idx on raw2014_08(station, valid);
CREATE INDEX raw2014_08_valid_idx on raw2014_08(valid);
grant select on raw2014_08 to nobody,apache;

create table raw2014_09( 
  CONSTRAINT __raw2014_09_check 
  CHECK(valid >= '2014-09-01 00:00+00'::timestamptz 
        and valid < '2014-10-01 00:00+00')) 
  INHERITS (raw2014);
CREATE INDEX raw2014_09_idx on raw2014_09(station, valid);
CREATE INDEX raw2014_09_valid_idx on raw2014_09(valid);
grant select on raw2014_09 to nobody,apache;

create table raw2014_10( 
  CONSTRAINT __raw2014_10_check 
  CHECK(valid >= '2014-10-01 00:00+00'::timestamptz 
        and valid < '2014-11-01 00:00+00')) 
  INHERITS (raw2014);
CREATE INDEX raw2014_10_idx on raw2014_10(station, valid);
CREATE INDEX raw2014_10_valid_idx on raw2014_10(valid);
grant select on raw2014_10 to nobody,apache;

create table raw2014_11( 
  CONSTRAINT __raw2014_11_check 
  CHECK(valid >= '2014-11-01 00:00+00'::timestamptz 
        and valid < '2014-12-01 00:00+00')) 
  INHERITS (raw2014);
CREATE INDEX raw2014_11_idx on raw2014_11(station, valid);
CREATE INDEX raw2014_11_valid_idx on raw2014_11(valid);
grant select on raw2014_11 to nobody,apache;

create table raw2014_12( 
  CONSTRAINT __raw2014_12_check 
  CHECK(valid >= '2014-12-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (raw2014);
CREATE INDEX raw2014_12_idx on raw2014_12(station, valid);
CREATE INDEX raw2014_12_valid_idx on raw2014_12(valid);
grant select on raw2014_12 to nobody,apache;
