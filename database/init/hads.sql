CREATE EXTENSION postgis;

-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (11, now());

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


CREATE TABLE unknown(
	nwsli varchar(8),
	product varchar(64),
	network varchar(24)
);

---
---
---
CREATE TABLE raw2002(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2002 to nobody,apache;

create table raw2002_01( 
  CONSTRAINT __raw2002_01_check 
  CHECK(valid >= '2002-01-01 00:00+00'::timestamptz 
        and valid < '2002-02-01 00:00+00')) 
  INHERITS (raw2002);
CREATE INDEX raw2002_01_idx on raw2002_01(station, valid);
CREATE INDEX raw2002_01_valid_idx on raw2002_01(valid);
grant select on raw2002_01 to nobody,apache;

create table raw2002_02( 
  CONSTRAINT __raw2002_02_check 
  CHECK(valid >= '2002-02-01 00:00+00'::timestamptz 
        and valid < '2002-03-01 00:00+00')) 
  INHERITS (raw2002);
CREATE INDEX raw2002_02_idx on raw2002_02(station, valid);
CREATE INDEX raw2002_02_valid_idx on raw2002_02(valid);
grant select on raw2002_02 to nobody,apache;

create table raw2002_03( 
  CONSTRAINT __raw2002_03_check 
  CHECK(valid >= '2002-03-01 00:00+00'::timestamptz 
        and valid < '2002-04-01 00:00+00')) 
  INHERITS (raw2002);
CREATE INDEX raw2002_03_idx on raw2002_03(station, valid);
CREATE INDEX raw2002_03_valid_idx on raw2002_03(valid);
grant select on raw2002_03 to nobody,apache;

create table raw2002_04( 
  CONSTRAINT __raw2002_04_check 
  CHECK(valid >= '2002-04-01 00:00+00'::timestamptz 
        and valid < '2002-05-01 00:00+00')) 
  INHERITS (raw2002);
CREATE INDEX raw2002_04_idx on raw2002_04(station, valid);
CREATE INDEX raw2002_04_valid_idx on raw2002_04(valid);
grant select on raw2002_04 to nobody,apache;

create table raw2002_05( 
  CONSTRAINT __raw2002_05_check 
  CHECK(valid >= '2002-05-01 00:00+00'::timestamptz 
        and valid < '2002-06-01 00:00+00')) 
  INHERITS (raw2002);
CREATE INDEX raw2002_05_idx on raw2002_05(station, valid);
CREATE INDEX raw2002_05_valid_idx on raw2002_05(valid);
grant select on raw2002_05 to nobody,apache;

create table raw2002_06( 
  CONSTRAINT __raw2002_06_check 
  CHECK(valid >= '2002-06-01 00:00+00'::timestamptz 
        and valid < '2002-07-01 00:00+00')) 
  INHERITS (raw2002);
CREATE INDEX raw2002_06_idx on raw2002_06(station, valid);
CREATE INDEX raw2002_06_valid_idx on raw2002_06(valid);
grant select on raw2002_06 to nobody,apache;

create table raw2002_07( 
  CONSTRAINT __raw2002_07_check 
  CHECK(valid >= '2002-07-01 00:00+00'::timestamptz 
        and valid < '2002-08-01 00:00+00')) 
  INHERITS (raw2002);
CREATE INDEX raw2002_07_idx on raw2002_07(station, valid);
CREATE INDEX raw2002_07_valid_idx on raw2002_07(valid);
grant select on raw2002_07 to nobody,apache;

create table raw2002_08( 
  CONSTRAINT __raw2002_08_check 
  CHECK(valid >= '2002-08-01 00:00+00'::timestamptz 
        and valid < '2002-09-01 00:00+00')) 
  INHERITS (raw2002);
CREATE INDEX raw2002_08_idx on raw2002_08(station, valid);
CREATE INDEX raw2002_08_valid_idx on raw2002_08(valid);
grant select on raw2002_08 to nobody,apache;

create table raw2002_09( 
  CONSTRAINT __raw2002_09_check 
  CHECK(valid >= '2002-09-01 00:00+00'::timestamptz 
        and valid < '2002-10-01 00:00+00')) 
  INHERITS (raw2002);
CREATE INDEX raw2002_09_idx on raw2002_09(station, valid);
CREATE INDEX raw2002_09_valid_idx on raw2002_09(valid);
grant select on raw2002_09 to nobody,apache;

create table raw2002_10( 
  CONSTRAINT __raw2002_10_check 
  CHECK(valid >= '2002-10-01 00:00+00'::timestamptz 
        and valid < '2002-11-01 00:00+00')) 
  INHERITS (raw2002);
CREATE INDEX raw2002_10_idx on raw2002_10(station, valid);
CREATE INDEX raw2002_10_valid_idx on raw2002_10(valid);
grant select on raw2002_10 to nobody,apache;

create table raw2002_11( 
  CONSTRAINT __raw2002_11_check 
  CHECK(valid >= '2002-11-01 00:00+00'::timestamptz 
        and valid < '2002-12-01 00:00+00')) 
  INHERITS (raw2002);
CREATE INDEX raw2002_11_idx on raw2002_11(station, valid);
CREATE INDEX raw2002_11_valid_idx on raw2002_11(valid);
grant select on raw2002_11 to nobody,apache;

create table raw2002_12( 
  CONSTRAINT __raw2002_12_check 
  CHECK(valid >= '2002-12-01 00:00+00'::timestamptz 
        and valid < '2003-01-01 00:00+00')) 
  INHERITS (raw2002);
CREATE INDEX raw2002_12_idx on raw2002_12(station, valid);
CREATE INDEX raw2002_12_valid_idx on raw2002_12(valid);
grant select on raw2002_12 to nobody,apache;
    

---
---
---
CREATE TABLE raw2003(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2003 to nobody,apache;

create table raw2003_01( 
  CONSTRAINT __raw2003_01_check 
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz 
        and valid < '2003-02-01 00:00+00')) 
  INHERITS (raw2003);
CREATE INDEX raw2003_01_idx on raw2003_01(station, valid);
CREATE INDEX raw2003_01_valid_idx on raw2003_01(valid);
grant select on raw2003_01 to nobody,apache;

create table raw2003_02( 
  CONSTRAINT __raw2003_02_check 
  CHECK(valid >= '2003-02-01 00:00+00'::timestamptz 
        and valid < '2003-03-01 00:00+00')) 
  INHERITS (raw2003);
CREATE INDEX raw2003_02_idx on raw2003_02(station, valid);
CREATE INDEX raw2003_02_valid_idx on raw2003_02(valid);
grant select on raw2003_02 to nobody,apache;

create table raw2003_03( 
  CONSTRAINT __raw2003_03_check 
  CHECK(valid >= '2003-03-01 00:00+00'::timestamptz 
        and valid < '2003-04-01 00:00+00')) 
  INHERITS (raw2003);
CREATE INDEX raw2003_03_idx on raw2003_03(station, valid);
CREATE INDEX raw2003_03_valid_idx on raw2003_03(valid);
grant select on raw2003_03 to nobody,apache;

create table raw2003_04( 
  CONSTRAINT __raw2003_04_check 
  CHECK(valid >= '2003-04-01 00:00+00'::timestamptz 
        and valid < '2003-05-01 00:00+00')) 
  INHERITS (raw2003);
CREATE INDEX raw2003_04_idx on raw2003_04(station, valid);
CREATE INDEX raw2003_04_valid_idx on raw2003_04(valid);
grant select on raw2003_04 to nobody,apache;

create table raw2003_05( 
  CONSTRAINT __raw2003_05_check 
  CHECK(valid >= '2003-05-01 00:00+00'::timestamptz 
        and valid < '2003-06-01 00:00+00')) 
  INHERITS (raw2003);
CREATE INDEX raw2003_05_idx on raw2003_05(station, valid);
CREATE INDEX raw2003_05_valid_idx on raw2003_05(valid);
grant select on raw2003_05 to nobody,apache;

create table raw2003_06( 
  CONSTRAINT __raw2003_06_check 
  CHECK(valid >= '2003-06-01 00:00+00'::timestamptz 
        and valid < '2003-07-01 00:00+00')) 
  INHERITS (raw2003);
CREATE INDEX raw2003_06_idx on raw2003_06(station, valid);
CREATE INDEX raw2003_06_valid_idx on raw2003_06(valid);
grant select on raw2003_06 to nobody,apache;

create table raw2003_07( 
  CONSTRAINT __raw2003_07_check 
  CHECK(valid >= '2003-07-01 00:00+00'::timestamptz 
        and valid < '2003-08-01 00:00+00')) 
  INHERITS (raw2003);
CREATE INDEX raw2003_07_idx on raw2003_07(station, valid);
CREATE INDEX raw2003_07_valid_idx on raw2003_07(valid);
grant select on raw2003_07 to nobody,apache;

create table raw2003_08( 
  CONSTRAINT __raw2003_08_check 
  CHECK(valid >= '2003-08-01 00:00+00'::timestamptz 
        and valid < '2003-09-01 00:00+00')) 
  INHERITS (raw2003);
CREATE INDEX raw2003_08_idx on raw2003_08(station, valid);
CREATE INDEX raw2003_08_valid_idx on raw2003_08(valid);
grant select on raw2003_08 to nobody,apache;

create table raw2003_09( 
  CONSTRAINT __raw2003_09_check 
  CHECK(valid >= '2003-09-01 00:00+00'::timestamptz 
        and valid < '2003-10-01 00:00+00')) 
  INHERITS (raw2003);
CREATE INDEX raw2003_09_idx on raw2003_09(station, valid);
CREATE INDEX raw2003_09_valid_idx on raw2003_09(valid);
grant select on raw2003_09 to nobody,apache;

create table raw2003_10( 
  CONSTRAINT __raw2003_10_check 
  CHECK(valid >= '2003-10-01 00:00+00'::timestamptz 
        and valid < '2003-11-01 00:00+00')) 
  INHERITS (raw2003);
CREATE INDEX raw2003_10_idx on raw2003_10(station, valid);
CREATE INDEX raw2003_10_valid_idx on raw2003_10(valid);
grant select on raw2003_10 to nobody,apache;

create table raw2003_11( 
  CONSTRAINT __raw2003_11_check 
  CHECK(valid >= '2003-11-01 00:00+00'::timestamptz 
        and valid < '2003-12-01 00:00+00')) 
  INHERITS (raw2003);
CREATE INDEX raw2003_11_idx on raw2003_11(station, valid);
CREATE INDEX raw2003_11_valid_idx on raw2003_11(valid);
grant select on raw2003_11 to nobody,apache;

create table raw2003_12( 
  CONSTRAINT __raw2003_12_check 
  CHECK(valid >= '2003-12-01 00:00+00'::timestamptz 
        and valid < '2004-01-01 00:00+00')) 
  INHERITS (raw2003);
CREATE INDEX raw2003_12_idx on raw2003_12(station, valid);
CREATE INDEX raw2003_12_valid_idx on raw2003_12(valid);
grant select on raw2003_12 to nobody,apache;
    

---
---
---
CREATE TABLE raw2004(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2004 to nobody,apache;

create table raw2004_01( 
  CONSTRAINT __raw2004_01_check 
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz 
        and valid < '2004-02-01 00:00+00')) 
  INHERITS (raw2004);
CREATE INDEX raw2004_01_idx on raw2004_01(station, valid);
CREATE INDEX raw2004_01_valid_idx on raw2004_01(valid);
grant select on raw2004_01 to nobody,apache;

create table raw2004_02( 
  CONSTRAINT __raw2004_02_check 
  CHECK(valid >= '2004-02-01 00:00+00'::timestamptz 
        and valid < '2004-03-01 00:00+00')) 
  INHERITS (raw2004);
CREATE INDEX raw2004_02_idx on raw2004_02(station, valid);
CREATE INDEX raw2004_02_valid_idx on raw2004_02(valid);
grant select on raw2004_02 to nobody,apache;

create table raw2004_03( 
  CONSTRAINT __raw2004_03_check 
  CHECK(valid >= '2004-03-01 00:00+00'::timestamptz 
        and valid < '2004-04-01 00:00+00')) 
  INHERITS (raw2004);
CREATE INDEX raw2004_03_idx on raw2004_03(station, valid);
CREATE INDEX raw2004_03_valid_idx on raw2004_03(valid);
grant select on raw2004_03 to nobody,apache;

create table raw2004_04( 
  CONSTRAINT __raw2004_04_check 
  CHECK(valid >= '2004-04-01 00:00+00'::timestamptz 
        and valid < '2004-05-01 00:00+00')) 
  INHERITS (raw2004);
CREATE INDEX raw2004_04_idx on raw2004_04(station, valid);
CREATE INDEX raw2004_04_valid_idx on raw2004_04(valid);
grant select on raw2004_04 to nobody,apache;

create table raw2004_05( 
  CONSTRAINT __raw2004_05_check 
  CHECK(valid >= '2004-05-01 00:00+00'::timestamptz 
        and valid < '2004-06-01 00:00+00')) 
  INHERITS (raw2004);
CREATE INDEX raw2004_05_idx on raw2004_05(station, valid);
CREATE INDEX raw2004_05_valid_idx on raw2004_05(valid);
grant select on raw2004_05 to nobody,apache;

create table raw2004_06( 
  CONSTRAINT __raw2004_06_check 
  CHECK(valid >= '2004-06-01 00:00+00'::timestamptz 
        and valid < '2004-07-01 00:00+00')) 
  INHERITS (raw2004);
CREATE INDEX raw2004_06_idx on raw2004_06(station, valid);
CREATE INDEX raw2004_06_valid_idx on raw2004_06(valid);
grant select on raw2004_06 to nobody,apache;

create table raw2004_07( 
  CONSTRAINT __raw2004_07_check 
  CHECK(valid >= '2004-07-01 00:00+00'::timestamptz 
        and valid < '2004-08-01 00:00+00')) 
  INHERITS (raw2004);
CREATE INDEX raw2004_07_idx on raw2004_07(station, valid);
CREATE INDEX raw2004_07_valid_idx on raw2004_07(valid);
grant select on raw2004_07 to nobody,apache;

create table raw2004_08( 
  CONSTRAINT __raw2004_08_check 
  CHECK(valid >= '2004-08-01 00:00+00'::timestamptz 
        and valid < '2004-09-01 00:00+00')) 
  INHERITS (raw2004);
CREATE INDEX raw2004_08_idx on raw2004_08(station, valid);
CREATE INDEX raw2004_08_valid_idx on raw2004_08(valid);
grant select on raw2004_08 to nobody,apache;

create table raw2004_09( 
  CONSTRAINT __raw2004_09_check 
  CHECK(valid >= '2004-09-01 00:00+00'::timestamptz 
        and valid < '2004-10-01 00:00+00')) 
  INHERITS (raw2004);
CREATE INDEX raw2004_09_idx on raw2004_09(station, valid);
CREATE INDEX raw2004_09_valid_idx on raw2004_09(valid);
grant select on raw2004_09 to nobody,apache;

create table raw2004_10( 
  CONSTRAINT __raw2004_10_check 
  CHECK(valid >= '2004-10-01 00:00+00'::timestamptz 
        and valid < '2004-11-01 00:00+00')) 
  INHERITS (raw2004);
CREATE INDEX raw2004_10_idx on raw2004_10(station, valid);
CREATE INDEX raw2004_10_valid_idx on raw2004_10(valid);
grant select on raw2004_10 to nobody,apache;

create table raw2004_11( 
  CONSTRAINT __raw2004_11_check 
  CHECK(valid >= '2004-11-01 00:00+00'::timestamptz 
        and valid < '2004-12-01 00:00+00')) 
  INHERITS (raw2004);
CREATE INDEX raw2004_11_idx on raw2004_11(station, valid);
CREATE INDEX raw2004_11_valid_idx on raw2004_11(valid);
grant select on raw2004_11 to nobody,apache;

create table raw2004_12( 
  CONSTRAINT __raw2004_12_check 
  CHECK(valid >= '2004-12-01 00:00+00'::timestamptz 
        and valid < '2005-01-01 00:00+00')) 
  INHERITS (raw2004);
CREATE INDEX raw2004_12_idx on raw2004_12(station, valid);
CREATE INDEX raw2004_12_valid_idx on raw2004_12(valid);
grant select on raw2004_12 to nobody,apache;
    

---
---
---
CREATE TABLE raw2005(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2005 to nobody,apache;

create table raw2005_01( 
  CONSTRAINT __raw2005_01_check 
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz 
        and valid < '2005-02-01 00:00+00')) 
  INHERITS (raw2005);
CREATE INDEX raw2005_01_idx on raw2005_01(station, valid);
CREATE INDEX raw2005_01_valid_idx on raw2005_01(valid);
grant select on raw2005_01 to nobody,apache;

create table raw2005_02( 
  CONSTRAINT __raw2005_02_check 
  CHECK(valid >= '2005-02-01 00:00+00'::timestamptz 
        and valid < '2005-03-01 00:00+00')) 
  INHERITS (raw2005);
CREATE INDEX raw2005_02_idx on raw2005_02(station, valid);
CREATE INDEX raw2005_02_valid_idx on raw2005_02(valid);
grant select on raw2005_02 to nobody,apache;

create table raw2005_03( 
  CONSTRAINT __raw2005_03_check 
  CHECK(valid >= '2005-03-01 00:00+00'::timestamptz 
        and valid < '2005-04-01 00:00+00')) 
  INHERITS (raw2005);
CREATE INDEX raw2005_03_idx on raw2005_03(station, valid);
CREATE INDEX raw2005_03_valid_idx on raw2005_03(valid);
grant select on raw2005_03 to nobody,apache;

create table raw2005_04( 
  CONSTRAINT __raw2005_04_check 
  CHECK(valid >= '2005-04-01 00:00+00'::timestamptz 
        and valid < '2005-05-01 00:00+00')) 
  INHERITS (raw2005);
CREATE INDEX raw2005_04_idx on raw2005_04(station, valid);
CREATE INDEX raw2005_04_valid_idx on raw2005_04(valid);
grant select on raw2005_04 to nobody,apache;

create table raw2005_05( 
  CONSTRAINT __raw2005_05_check 
  CHECK(valid >= '2005-05-01 00:00+00'::timestamptz 
        and valid < '2005-06-01 00:00+00')) 
  INHERITS (raw2005);
CREATE INDEX raw2005_05_idx on raw2005_05(station, valid);
CREATE INDEX raw2005_05_valid_idx on raw2005_05(valid);
grant select on raw2005_05 to nobody,apache;

create table raw2005_06( 
  CONSTRAINT __raw2005_06_check 
  CHECK(valid >= '2005-06-01 00:00+00'::timestamptz 
        and valid < '2005-07-01 00:00+00')) 
  INHERITS (raw2005);
CREATE INDEX raw2005_06_idx on raw2005_06(station, valid);
CREATE INDEX raw2005_06_valid_idx on raw2005_06(valid);
grant select on raw2005_06 to nobody,apache;

create table raw2005_07( 
  CONSTRAINT __raw2005_07_check 
  CHECK(valid >= '2005-07-01 00:00+00'::timestamptz 
        and valid < '2005-08-01 00:00+00')) 
  INHERITS (raw2005);
CREATE INDEX raw2005_07_idx on raw2005_07(station, valid);
CREATE INDEX raw2005_07_valid_idx on raw2005_07(valid);
grant select on raw2005_07 to nobody,apache;

create table raw2005_08( 
  CONSTRAINT __raw2005_08_check 
  CHECK(valid >= '2005-08-01 00:00+00'::timestamptz 
        and valid < '2005-09-01 00:00+00')) 
  INHERITS (raw2005);
CREATE INDEX raw2005_08_idx on raw2005_08(station, valid);
CREATE INDEX raw2005_08_valid_idx on raw2005_08(valid);
grant select on raw2005_08 to nobody,apache;

create table raw2005_09( 
  CONSTRAINT __raw2005_09_check 
  CHECK(valid >= '2005-09-01 00:00+00'::timestamptz 
        and valid < '2005-10-01 00:00+00')) 
  INHERITS (raw2005);
CREATE INDEX raw2005_09_idx on raw2005_09(station, valid);
CREATE INDEX raw2005_09_valid_idx on raw2005_09(valid);
grant select on raw2005_09 to nobody,apache;

create table raw2005_10( 
  CONSTRAINT __raw2005_10_check 
  CHECK(valid >= '2005-10-01 00:00+00'::timestamptz 
        and valid < '2005-11-01 00:00+00')) 
  INHERITS (raw2005);
CREATE INDEX raw2005_10_idx on raw2005_10(station, valid);
CREATE INDEX raw2005_10_valid_idx on raw2005_10(valid);
grant select on raw2005_10 to nobody,apache;

create table raw2005_11( 
  CONSTRAINT __raw2005_11_check 
  CHECK(valid >= '2005-11-01 00:00+00'::timestamptz 
        and valid < '2005-12-01 00:00+00')) 
  INHERITS (raw2005);
CREATE INDEX raw2005_11_idx on raw2005_11(station, valid);
CREATE INDEX raw2005_11_valid_idx on raw2005_11(valid);
grant select on raw2005_11 to nobody,apache;

create table raw2005_12( 
  CONSTRAINT __raw2005_12_check 
  CHECK(valid >= '2005-12-01 00:00+00'::timestamptz 
        and valid < '2006-01-01 00:00+00')) 
  INHERITS (raw2005);
CREATE INDEX raw2005_12_idx on raw2005_12(station, valid);
CREATE INDEX raw2005_12_valid_idx on raw2005_12(valid);
grant select on raw2005_12 to nobody,apache;
    

---
---
---
CREATE TABLE raw2006(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2006 to nobody,apache;

create table raw2006_01( 
  CONSTRAINT __raw2006_01_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz 
        and valid < '2006-02-01 00:00+00')) 
  INHERITS (raw2006);
CREATE INDEX raw2006_01_idx on raw2006_01(station, valid);
CREATE INDEX raw2006_01_valid_idx on raw2006_01(valid);
grant select on raw2006_01 to nobody,apache;

create table raw2006_02( 
  CONSTRAINT __raw2006_02_check 
  CHECK(valid >= '2006-02-01 00:00+00'::timestamptz 
        and valid < '2006-03-01 00:00+00')) 
  INHERITS (raw2006);
CREATE INDEX raw2006_02_idx on raw2006_02(station, valid);
CREATE INDEX raw2006_02_valid_idx on raw2006_02(valid);
grant select on raw2006_02 to nobody,apache;

create table raw2006_03( 
  CONSTRAINT __raw2006_03_check 
  CHECK(valid >= '2006-03-01 00:00+00'::timestamptz 
        and valid < '2006-04-01 00:00+00')) 
  INHERITS (raw2006);
CREATE INDEX raw2006_03_idx on raw2006_03(station, valid);
CREATE INDEX raw2006_03_valid_idx on raw2006_03(valid);
grant select on raw2006_03 to nobody,apache;

create table raw2006_04( 
  CONSTRAINT __raw2006_04_check 
  CHECK(valid >= '2006-04-01 00:00+00'::timestamptz 
        and valid < '2006-05-01 00:00+00')) 
  INHERITS (raw2006);
CREATE INDEX raw2006_04_idx on raw2006_04(station, valid);
CREATE INDEX raw2006_04_valid_idx on raw2006_04(valid);
grant select on raw2006_04 to nobody,apache;

create table raw2006_05( 
  CONSTRAINT __raw2006_05_check 
  CHECK(valid >= '2006-05-01 00:00+00'::timestamptz 
        and valid < '2006-06-01 00:00+00')) 
  INHERITS (raw2006);
CREATE INDEX raw2006_05_idx on raw2006_05(station, valid);
CREATE INDEX raw2006_05_valid_idx on raw2006_05(valid);
grant select on raw2006_05 to nobody,apache;

create table raw2006_06( 
  CONSTRAINT __raw2006_06_check 
  CHECK(valid >= '2006-06-01 00:00+00'::timestamptz 
        and valid < '2006-07-01 00:00+00')) 
  INHERITS (raw2006);
CREATE INDEX raw2006_06_idx on raw2006_06(station, valid);
CREATE INDEX raw2006_06_valid_idx on raw2006_06(valid);
grant select on raw2006_06 to nobody,apache;

create table raw2006_07( 
  CONSTRAINT __raw2006_07_check 
  CHECK(valid >= '2006-07-01 00:00+00'::timestamptz 
        and valid < '2006-08-01 00:00+00')) 
  INHERITS (raw2006);
CREATE INDEX raw2006_07_idx on raw2006_07(station, valid);
CREATE INDEX raw2006_07_valid_idx on raw2006_07(valid);
grant select on raw2006_07 to nobody,apache;

create table raw2006_08( 
  CONSTRAINT __raw2006_08_check 
  CHECK(valid >= '2006-08-01 00:00+00'::timestamptz 
        and valid < '2006-09-01 00:00+00')) 
  INHERITS (raw2006);
CREATE INDEX raw2006_08_idx on raw2006_08(station, valid);
CREATE INDEX raw2006_08_valid_idx on raw2006_08(valid);
grant select on raw2006_08 to nobody,apache;

create table raw2006_09( 
  CONSTRAINT __raw2006_09_check 
  CHECK(valid >= '2006-09-01 00:00+00'::timestamptz 
        and valid < '2006-10-01 00:00+00')) 
  INHERITS (raw2006);
CREATE INDEX raw2006_09_idx on raw2006_09(station, valid);
CREATE INDEX raw2006_09_valid_idx on raw2006_09(valid);
grant select on raw2006_09 to nobody,apache;

create table raw2006_10( 
  CONSTRAINT __raw2006_10_check 
  CHECK(valid >= '2006-10-01 00:00+00'::timestamptz 
        and valid < '2006-11-01 00:00+00')) 
  INHERITS (raw2006);
CREATE INDEX raw2006_10_idx on raw2006_10(station, valid);
CREATE INDEX raw2006_10_valid_idx on raw2006_10(valid);
grant select on raw2006_10 to nobody,apache;

create table raw2006_11( 
  CONSTRAINT __raw2006_11_check 
  CHECK(valid >= '2006-11-01 00:00+00'::timestamptz 
        and valid < '2006-12-01 00:00+00')) 
  INHERITS (raw2006);
CREATE INDEX raw2006_11_idx on raw2006_11(station, valid);
CREATE INDEX raw2006_11_valid_idx on raw2006_11(valid);
grant select on raw2006_11 to nobody,apache;

create table raw2006_12( 
  CONSTRAINT __raw2006_12_check 
  CHECK(valid >= '2006-12-01 00:00+00'::timestamptz 
        and valid < '2007-01-01 00:00+00')) 
  INHERITS (raw2006);
CREATE INDEX raw2006_12_idx on raw2006_12(station, valid);
CREATE INDEX raw2006_12_valid_idx on raw2006_12(valid);
grant select on raw2006_12 to nobody,apache;
    

---
---
---
CREATE TABLE raw2007(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2007 to nobody,apache;

create table raw2007_01( 
  CONSTRAINT __raw2007_01_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz 
        and valid < '2007-02-01 00:00+00')) 
  INHERITS (raw2007);
CREATE INDEX raw2007_01_idx on raw2007_01(station, valid);
CREATE INDEX raw2007_01_valid_idx on raw2007_01(valid);
grant select on raw2007_01 to nobody,apache;

create table raw2007_02( 
  CONSTRAINT __raw2007_02_check 
  CHECK(valid >= '2007-02-01 00:00+00'::timestamptz 
        and valid < '2007-03-01 00:00+00')) 
  INHERITS (raw2007);
CREATE INDEX raw2007_02_idx on raw2007_02(station, valid);
CREATE INDEX raw2007_02_valid_idx on raw2007_02(valid);
grant select on raw2007_02 to nobody,apache;

create table raw2007_03( 
  CONSTRAINT __raw2007_03_check 
  CHECK(valid >= '2007-03-01 00:00+00'::timestamptz 
        and valid < '2007-04-01 00:00+00')) 
  INHERITS (raw2007);
CREATE INDEX raw2007_03_idx on raw2007_03(station, valid);
CREATE INDEX raw2007_03_valid_idx on raw2007_03(valid);
grant select on raw2007_03 to nobody,apache;

create table raw2007_04( 
  CONSTRAINT __raw2007_04_check 
  CHECK(valid >= '2007-04-01 00:00+00'::timestamptz 
        and valid < '2007-05-01 00:00+00')) 
  INHERITS (raw2007);
CREATE INDEX raw2007_04_idx on raw2007_04(station, valid);
CREATE INDEX raw2007_04_valid_idx on raw2007_04(valid);
grant select on raw2007_04 to nobody,apache;

create table raw2007_05( 
  CONSTRAINT __raw2007_05_check 
  CHECK(valid >= '2007-05-01 00:00+00'::timestamptz 
        and valid < '2007-06-01 00:00+00')) 
  INHERITS (raw2007);
CREATE INDEX raw2007_05_idx on raw2007_05(station, valid);
CREATE INDEX raw2007_05_valid_idx on raw2007_05(valid);
grant select on raw2007_05 to nobody,apache;

create table raw2007_06( 
  CONSTRAINT __raw2007_06_check 
  CHECK(valid >= '2007-06-01 00:00+00'::timestamptz 
        and valid < '2007-07-01 00:00+00')) 
  INHERITS (raw2007);
CREATE INDEX raw2007_06_idx on raw2007_06(station, valid);
CREATE INDEX raw2007_06_valid_idx on raw2007_06(valid);
grant select on raw2007_06 to nobody,apache;

create table raw2007_07( 
  CONSTRAINT __raw2007_07_check 
  CHECK(valid >= '2007-07-01 00:00+00'::timestamptz 
        and valid < '2007-08-01 00:00+00')) 
  INHERITS (raw2007);
CREATE INDEX raw2007_07_idx on raw2007_07(station, valid);
CREATE INDEX raw2007_07_valid_idx on raw2007_07(valid);
grant select on raw2007_07 to nobody,apache;

create table raw2007_08( 
  CONSTRAINT __raw2007_08_check 
  CHECK(valid >= '2007-08-01 00:00+00'::timestamptz 
        and valid < '2007-09-01 00:00+00')) 
  INHERITS (raw2007);
CREATE INDEX raw2007_08_idx on raw2007_08(station, valid);
CREATE INDEX raw2007_08_valid_idx on raw2007_08(valid);
grant select on raw2007_08 to nobody,apache;

create table raw2007_09( 
  CONSTRAINT __raw2007_09_check 
  CHECK(valid >= '2007-09-01 00:00+00'::timestamptz 
        and valid < '2007-10-01 00:00+00')) 
  INHERITS (raw2007);
CREATE INDEX raw2007_09_idx on raw2007_09(station, valid);
CREATE INDEX raw2007_09_valid_idx on raw2007_09(valid);
grant select on raw2007_09 to nobody,apache;

create table raw2007_10( 
  CONSTRAINT __raw2007_10_check 
  CHECK(valid >= '2007-10-01 00:00+00'::timestamptz 
        and valid < '2007-11-01 00:00+00')) 
  INHERITS (raw2007);
CREATE INDEX raw2007_10_idx on raw2007_10(station, valid);
CREATE INDEX raw2007_10_valid_idx on raw2007_10(valid);
grant select on raw2007_10 to nobody,apache;

create table raw2007_11( 
  CONSTRAINT __raw2007_11_check 
  CHECK(valid >= '2007-11-01 00:00+00'::timestamptz 
        and valid < '2007-12-01 00:00+00')) 
  INHERITS (raw2007);
CREATE INDEX raw2007_11_idx on raw2007_11(station, valid);
CREATE INDEX raw2007_11_valid_idx on raw2007_11(valid);
grant select on raw2007_11 to nobody,apache;

create table raw2007_12( 
  CONSTRAINT __raw2007_12_check 
  CHECK(valid >= '2007-12-01 00:00+00'::timestamptz 
        and valid < '2008-01-01 00:00+00')) 
  INHERITS (raw2007);
CREATE INDEX raw2007_12_idx on raw2007_12(station, valid);
CREATE INDEX raw2007_12_valid_idx on raw2007_12(valid);
grant select on raw2007_12 to nobody,apache;
    

---
---
---
CREATE TABLE raw2008(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2008 to nobody,apache;

create table raw2008_01( 
  CONSTRAINT __raw2008_01_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2008-02-01 00:00+00')) 
  INHERITS (raw2008);
CREATE INDEX raw2008_01_idx on raw2008_01(station, valid);
CREATE INDEX raw2008_01_valid_idx on raw2008_01(valid);
grant select on raw2008_01 to nobody,apache;

create table raw2008_02( 
  CONSTRAINT __raw2008_02_check 
  CHECK(valid >= '2008-02-01 00:00+00'::timestamptz 
        and valid < '2008-03-01 00:00+00')) 
  INHERITS (raw2008);
CREATE INDEX raw2008_02_idx on raw2008_02(station, valid);
CREATE INDEX raw2008_02_valid_idx on raw2008_02(valid);
grant select on raw2008_02 to nobody,apache;

create table raw2008_03( 
  CONSTRAINT __raw2008_03_check 
  CHECK(valid >= '2008-03-01 00:00+00'::timestamptz 
        and valid < '2008-04-01 00:00+00')) 
  INHERITS (raw2008);
CREATE INDEX raw2008_03_idx on raw2008_03(station, valid);
CREATE INDEX raw2008_03_valid_idx on raw2008_03(valid);
grant select on raw2008_03 to nobody,apache;

create table raw2008_04( 
  CONSTRAINT __raw2008_04_check 
  CHECK(valid >= '2008-04-01 00:00+00'::timestamptz 
        and valid < '2008-05-01 00:00+00')) 
  INHERITS (raw2008);
CREATE INDEX raw2008_04_idx on raw2008_04(station, valid);
CREATE INDEX raw2008_04_valid_idx on raw2008_04(valid);
grant select on raw2008_04 to nobody,apache;

create table raw2008_05( 
  CONSTRAINT __raw2008_05_check 
  CHECK(valid >= '2008-05-01 00:00+00'::timestamptz 
        and valid < '2008-06-01 00:00+00')) 
  INHERITS (raw2008);
CREATE INDEX raw2008_05_idx on raw2008_05(station, valid);
CREATE INDEX raw2008_05_valid_idx on raw2008_05(valid);
grant select on raw2008_05 to nobody,apache;

create table raw2008_06( 
  CONSTRAINT __raw2008_06_check 
  CHECK(valid >= '2008-06-01 00:00+00'::timestamptz 
        and valid < '2008-07-01 00:00+00')) 
  INHERITS (raw2008);
CREATE INDEX raw2008_06_idx on raw2008_06(station, valid);
CREATE INDEX raw2008_06_valid_idx on raw2008_06(valid);
grant select on raw2008_06 to nobody,apache;

create table raw2008_07( 
  CONSTRAINT __raw2008_07_check 
  CHECK(valid >= '2008-07-01 00:00+00'::timestamptz 
        and valid < '2008-08-01 00:00+00')) 
  INHERITS (raw2008);
CREATE INDEX raw2008_07_idx on raw2008_07(station, valid);
CREATE INDEX raw2008_07_valid_idx on raw2008_07(valid);
grant select on raw2008_07 to nobody,apache;

create table raw2008_08( 
  CONSTRAINT __raw2008_08_check 
  CHECK(valid >= '2008-08-01 00:00+00'::timestamptz 
        and valid < '2008-09-01 00:00+00')) 
  INHERITS (raw2008);
CREATE INDEX raw2008_08_idx on raw2008_08(station, valid);
CREATE INDEX raw2008_08_valid_idx on raw2008_08(valid);
grant select on raw2008_08 to nobody,apache;

create table raw2008_09( 
  CONSTRAINT __raw2008_09_check 
  CHECK(valid >= '2008-09-01 00:00+00'::timestamptz 
        and valid < '2008-10-01 00:00+00')) 
  INHERITS (raw2008);
CREATE INDEX raw2008_09_idx on raw2008_09(station, valid);
CREATE INDEX raw2008_09_valid_idx on raw2008_09(valid);
grant select on raw2008_09 to nobody,apache;

create table raw2008_10( 
  CONSTRAINT __raw2008_10_check 
  CHECK(valid >= '2008-10-01 00:00+00'::timestamptz 
        and valid < '2008-11-01 00:00+00')) 
  INHERITS (raw2008);
CREATE INDEX raw2008_10_idx on raw2008_10(station, valid);
CREATE INDEX raw2008_10_valid_idx on raw2008_10(valid);
grant select on raw2008_10 to nobody,apache;

create table raw2008_11( 
  CONSTRAINT __raw2008_11_check 
  CHECK(valid >= '2008-11-01 00:00+00'::timestamptz 
        and valid < '2008-12-01 00:00+00')) 
  INHERITS (raw2008);
CREATE INDEX raw2008_11_idx on raw2008_11(station, valid);
CREATE INDEX raw2008_11_valid_idx on raw2008_11(valid);
grant select on raw2008_11 to nobody,apache;

create table raw2008_12( 
  CONSTRAINT __raw2008_12_check 
  CHECK(valid >= '2008-12-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (raw2008);
CREATE INDEX raw2008_12_idx on raw2008_12(station, valid);
CREATE INDEX raw2008_12_valid_idx on raw2008_12(valid);
grant select on raw2008_12 to nobody,apache;
    

---
---
---
CREATE TABLE raw2009(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2009 to nobody,apache;

create table raw2009_01( 
  CONSTRAINT __raw2009_01_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2009-02-01 00:00+00')) 
  INHERITS (raw2009);
CREATE INDEX raw2009_01_idx on raw2009_01(station, valid);
CREATE INDEX raw2009_01_valid_idx on raw2009_01(valid);
grant select on raw2009_01 to nobody,apache;

create table raw2009_02( 
  CONSTRAINT __raw2009_02_check 
  CHECK(valid >= '2009-02-01 00:00+00'::timestamptz 
        and valid < '2009-03-01 00:00+00')) 
  INHERITS (raw2009);
CREATE INDEX raw2009_02_idx on raw2009_02(station, valid);
CREATE INDEX raw2009_02_valid_idx on raw2009_02(valid);
grant select on raw2009_02 to nobody,apache;

create table raw2009_03( 
  CONSTRAINT __raw2009_03_check 
  CHECK(valid >= '2009-03-01 00:00+00'::timestamptz 
        and valid < '2009-04-01 00:00+00')) 
  INHERITS (raw2009);
CREATE INDEX raw2009_03_idx on raw2009_03(station, valid);
CREATE INDEX raw2009_03_valid_idx on raw2009_03(valid);
grant select on raw2009_03 to nobody,apache;

create table raw2009_04( 
  CONSTRAINT __raw2009_04_check 
  CHECK(valid >= '2009-04-01 00:00+00'::timestamptz 
        and valid < '2009-05-01 00:00+00')) 
  INHERITS (raw2009);
CREATE INDEX raw2009_04_idx on raw2009_04(station, valid);
CREATE INDEX raw2009_04_valid_idx on raw2009_04(valid);
grant select on raw2009_04 to nobody,apache;

create table raw2009_05( 
  CONSTRAINT __raw2009_05_check 
  CHECK(valid >= '2009-05-01 00:00+00'::timestamptz 
        and valid < '2009-06-01 00:00+00')) 
  INHERITS (raw2009);
CREATE INDEX raw2009_05_idx on raw2009_05(station, valid);
CREATE INDEX raw2009_05_valid_idx on raw2009_05(valid);
grant select on raw2009_05 to nobody,apache;

create table raw2009_06( 
  CONSTRAINT __raw2009_06_check 
  CHECK(valid >= '2009-06-01 00:00+00'::timestamptz 
        and valid < '2009-07-01 00:00+00')) 
  INHERITS (raw2009);
CREATE INDEX raw2009_06_idx on raw2009_06(station, valid);
CREATE INDEX raw2009_06_valid_idx on raw2009_06(valid);
grant select on raw2009_06 to nobody,apache;

create table raw2009_07( 
  CONSTRAINT __raw2009_07_check 
  CHECK(valid >= '2009-07-01 00:00+00'::timestamptz 
        and valid < '2009-08-01 00:00+00')) 
  INHERITS (raw2009);
CREATE INDEX raw2009_07_idx on raw2009_07(station, valid);
CREATE INDEX raw2009_07_valid_idx on raw2009_07(valid);
grant select on raw2009_07 to nobody,apache;

create table raw2009_08( 
  CONSTRAINT __raw2009_08_check 
  CHECK(valid >= '2009-08-01 00:00+00'::timestamptz 
        and valid < '2009-09-01 00:00+00')) 
  INHERITS (raw2009);
CREATE INDEX raw2009_08_idx on raw2009_08(station, valid);
CREATE INDEX raw2009_08_valid_idx on raw2009_08(valid);
grant select on raw2009_08 to nobody,apache;

create table raw2009_09( 
  CONSTRAINT __raw2009_09_check 
  CHECK(valid >= '2009-09-01 00:00+00'::timestamptz 
        and valid < '2009-10-01 00:00+00')) 
  INHERITS (raw2009);
CREATE INDEX raw2009_09_idx on raw2009_09(station, valid);
CREATE INDEX raw2009_09_valid_idx on raw2009_09(valid);
grant select on raw2009_09 to nobody,apache;

create table raw2009_10( 
  CONSTRAINT __raw2009_10_check 
  CHECK(valid >= '2009-10-01 00:00+00'::timestamptz 
        and valid < '2009-11-01 00:00+00')) 
  INHERITS (raw2009);
CREATE INDEX raw2009_10_idx on raw2009_10(station, valid);
CREATE INDEX raw2009_10_valid_idx on raw2009_10(valid);
grant select on raw2009_10 to nobody,apache;

create table raw2009_11( 
  CONSTRAINT __raw2009_11_check 
  CHECK(valid >= '2009-11-01 00:00+00'::timestamptz 
        and valid < '2009-12-01 00:00+00')) 
  INHERITS (raw2009);
CREATE INDEX raw2009_11_idx on raw2009_11(station, valid);
CREATE INDEX raw2009_11_valid_idx on raw2009_11(valid);
grant select on raw2009_11 to nobody,apache;

create table raw2009_12( 
  CONSTRAINT __raw2009_12_check 
  CHECK(valid >= '2009-12-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (raw2009);
CREATE INDEX raw2009_12_idx on raw2009_12(station, valid);
CREATE INDEX raw2009_12_valid_idx on raw2009_12(valid);
grant select on raw2009_12 to nobody,apache;
    

---
---
---
CREATE TABLE raw2010(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2010 to nobody,apache;

create table raw2010_01( 
  CONSTRAINT __raw2010_01_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2010-02-01 00:00+00')) 
  INHERITS (raw2010);
CREATE INDEX raw2010_01_idx on raw2010_01(station, valid);
CREATE INDEX raw2010_01_valid_idx on raw2010_01(valid);
grant select on raw2010_01 to nobody,apache;

create table raw2010_02( 
  CONSTRAINT __raw2010_02_check 
  CHECK(valid >= '2010-02-01 00:00+00'::timestamptz 
        and valid < '2010-03-01 00:00+00')) 
  INHERITS (raw2010);
CREATE INDEX raw2010_02_idx on raw2010_02(station, valid);
CREATE INDEX raw2010_02_valid_idx on raw2010_02(valid);
grant select on raw2010_02 to nobody,apache;

create table raw2010_03( 
  CONSTRAINT __raw2010_03_check 
  CHECK(valid >= '2010-03-01 00:00+00'::timestamptz 
        and valid < '2010-04-01 00:00+00')) 
  INHERITS (raw2010);
CREATE INDEX raw2010_03_idx on raw2010_03(station, valid);
CREATE INDEX raw2010_03_valid_idx on raw2010_03(valid);
grant select on raw2010_03 to nobody,apache;

create table raw2010_04( 
  CONSTRAINT __raw2010_04_check 
  CHECK(valid >= '2010-04-01 00:00+00'::timestamptz 
        and valid < '2010-05-01 00:00+00')) 
  INHERITS (raw2010);
CREATE INDEX raw2010_04_idx on raw2010_04(station, valid);
CREATE INDEX raw2010_04_valid_idx on raw2010_04(valid);
grant select on raw2010_04 to nobody,apache;

create table raw2010_05( 
  CONSTRAINT __raw2010_05_check 
  CHECK(valid >= '2010-05-01 00:00+00'::timestamptz 
        and valid < '2010-06-01 00:00+00')) 
  INHERITS (raw2010);
CREATE INDEX raw2010_05_idx on raw2010_05(station, valid);
CREATE INDEX raw2010_05_valid_idx on raw2010_05(valid);
grant select on raw2010_05 to nobody,apache;

create table raw2010_06( 
  CONSTRAINT __raw2010_06_check 
  CHECK(valid >= '2010-06-01 00:00+00'::timestamptz 
        and valid < '2010-07-01 00:00+00')) 
  INHERITS (raw2010);
CREATE INDEX raw2010_06_idx on raw2010_06(station, valid);
CREATE INDEX raw2010_06_valid_idx on raw2010_06(valid);
grant select on raw2010_06 to nobody,apache;

create table raw2010_07( 
  CONSTRAINT __raw2010_07_check 
  CHECK(valid >= '2010-07-01 00:00+00'::timestamptz 
        and valid < '2010-08-01 00:00+00')) 
  INHERITS (raw2010);
CREATE INDEX raw2010_07_idx on raw2010_07(station, valid);
CREATE INDEX raw2010_07_valid_idx on raw2010_07(valid);
grant select on raw2010_07 to nobody,apache;

create table raw2010_08( 
  CONSTRAINT __raw2010_08_check 
  CHECK(valid >= '2010-08-01 00:00+00'::timestamptz 
        and valid < '2010-09-01 00:00+00')) 
  INHERITS (raw2010);
CREATE INDEX raw2010_08_idx on raw2010_08(station, valid);
CREATE INDEX raw2010_08_valid_idx on raw2010_08(valid);
grant select on raw2010_08 to nobody,apache;

create table raw2010_09( 
  CONSTRAINT __raw2010_09_check 
  CHECK(valid >= '2010-09-01 00:00+00'::timestamptz 
        and valid < '2010-10-01 00:00+00')) 
  INHERITS (raw2010);
CREATE INDEX raw2010_09_idx on raw2010_09(station, valid);
CREATE INDEX raw2010_09_valid_idx on raw2010_09(valid);
grant select on raw2010_09 to nobody,apache;

create table raw2010_10( 
  CONSTRAINT __raw2010_10_check 
  CHECK(valid >= '2010-10-01 00:00+00'::timestamptz 
        and valid < '2010-11-01 00:00+00')) 
  INHERITS (raw2010);
CREATE INDEX raw2010_10_idx on raw2010_10(station, valid);
CREATE INDEX raw2010_10_valid_idx on raw2010_10(valid);
grant select on raw2010_10 to nobody,apache;

create table raw2010_11( 
  CONSTRAINT __raw2010_11_check 
  CHECK(valid >= '2010-11-01 00:00+00'::timestamptz 
        and valid < '2010-12-01 00:00+00')) 
  INHERITS (raw2010);
CREATE INDEX raw2010_11_idx on raw2010_11(station, valid);
CREATE INDEX raw2010_11_valid_idx on raw2010_11(valid);
grant select on raw2010_11 to nobody,apache;

create table raw2010_12( 
  CONSTRAINT __raw2010_12_check 
  CHECK(valid >= '2010-12-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (raw2010);
CREATE INDEX raw2010_12_idx on raw2010_12(station, valid);
CREATE INDEX raw2010_12_valid_idx on raw2010_12(valid);
grant select on raw2010_12 to nobody,apache;
    

---
---
---
CREATE TABLE raw2011(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2011 to nobody,apache;

create table raw2011_01( 
  CONSTRAINT __raw2011_01_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2011-02-01 00:00+00')) 
  INHERITS (raw2011);
CREATE INDEX raw2011_01_idx on raw2011_01(station, valid);
CREATE INDEX raw2011_01_valid_idx on raw2011_01(valid);
grant select on raw2011_01 to nobody,apache;

create table raw2011_02( 
  CONSTRAINT __raw2011_02_check 
  CHECK(valid >= '2011-02-01 00:00+00'::timestamptz 
        and valid < '2011-03-01 00:00+00')) 
  INHERITS (raw2011);
CREATE INDEX raw2011_02_idx on raw2011_02(station, valid);
CREATE INDEX raw2011_02_valid_idx on raw2011_02(valid);
grant select on raw2011_02 to nobody,apache;

create table raw2011_03( 
  CONSTRAINT __raw2011_03_check 
  CHECK(valid >= '2011-03-01 00:00+00'::timestamptz 
        and valid < '2011-04-01 00:00+00')) 
  INHERITS (raw2011);
CREATE INDEX raw2011_03_idx on raw2011_03(station, valid);
CREATE INDEX raw2011_03_valid_idx on raw2011_03(valid);
grant select on raw2011_03 to nobody,apache;

create table raw2011_04( 
  CONSTRAINT __raw2011_04_check 
  CHECK(valid >= '2011-04-01 00:00+00'::timestamptz 
        and valid < '2011-05-01 00:00+00')) 
  INHERITS (raw2011);
CREATE INDEX raw2011_04_idx on raw2011_04(station, valid);
CREATE INDEX raw2011_04_valid_idx on raw2011_04(valid);
grant select on raw2011_04 to nobody,apache;

create table raw2011_05( 
  CONSTRAINT __raw2011_05_check 
  CHECK(valid >= '2011-05-01 00:00+00'::timestamptz 
        and valid < '2011-06-01 00:00+00')) 
  INHERITS (raw2011);
CREATE INDEX raw2011_05_idx on raw2011_05(station, valid);
CREATE INDEX raw2011_05_valid_idx on raw2011_05(valid);
grant select on raw2011_05 to nobody,apache;

create table raw2011_06( 
  CONSTRAINT __raw2011_06_check 
  CHECK(valid >= '2011-06-01 00:00+00'::timestamptz 
        and valid < '2011-07-01 00:00+00')) 
  INHERITS (raw2011);
CREATE INDEX raw2011_06_idx on raw2011_06(station, valid);
CREATE INDEX raw2011_06_valid_idx on raw2011_06(valid);
grant select on raw2011_06 to nobody,apache;

create table raw2011_07( 
  CONSTRAINT __raw2011_07_check 
  CHECK(valid >= '2011-07-01 00:00+00'::timestamptz 
        and valid < '2011-08-01 00:00+00')) 
  INHERITS (raw2011);
CREATE INDEX raw2011_07_idx on raw2011_07(station, valid);
CREATE INDEX raw2011_07_valid_idx on raw2011_07(valid);
grant select on raw2011_07 to nobody,apache;

create table raw2011_08( 
  CONSTRAINT __raw2011_08_check 
  CHECK(valid >= '2011-08-01 00:00+00'::timestamptz 
        and valid < '2011-09-01 00:00+00')) 
  INHERITS (raw2011);
CREATE INDEX raw2011_08_idx on raw2011_08(station, valid);
CREATE INDEX raw2011_08_valid_idx on raw2011_08(valid);
grant select on raw2011_08 to nobody,apache;

create table raw2011_09( 
  CONSTRAINT __raw2011_09_check 
  CHECK(valid >= '2011-09-01 00:00+00'::timestamptz 
        and valid < '2011-10-01 00:00+00')) 
  INHERITS (raw2011);
CREATE INDEX raw2011_09_idx on raw2011_09(station, valid);
CREATE INDEX raw2011_09_valid_idx on raw2011_09(valid);
grant select on raw2011_09 to nobody,apache;

create table raw2011_10( 
  CONSTRAINT __raw2011_10_check 
  CHECK(valid >= '2011-10-01 00:00+00'::timestamptz 
        and valid < '2011-11-01 00:00+00')) 
  INHERITS (raw2011);
CREATE INDEX raw2011_10_idx on raw2011_10(station, valid);
CREATE INDEX raw2011_10_valid_idx on raw2011_10(valid);
grant select on raw2011_10 to nobody,apache;

create table raw2011_11( 
  CONSTRAINT __raw2011_11_check 
  CHECK(valid >= '2011-11-01 00:00+00'::timestamptz 
        and valid < '2011-12-01 00:00+00')) 
  INHERITS (raw2011);
CREATE INDEX raw2011_11_idx on raw2011_11(station, valid);
CREATE INDEX raw2011_11_valid_idx on raw2011_11(valid);
grant select on raw2011_11 to nobody,apache;

create table raw2011_12( 
  CONSTRAINT __raw2011_12_check 
  CHECK(valid >= '2011-12-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (raw2011);
CREATE INDEX raw2011_12_idx on raw2011_12(station, valid);
CREATE INDEX raw2011_12_valid_idx on raw2011_12(valid);
grant select on raw2011_12 to nobody,apache;
    

---
---
---
CREATE TABLE raw2012(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2012 to nobody,apache;

create table raw2012_01( 
  CONSTRAINT __raw2012_01_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2012-02-01 00:00+00')) 
  INHERITS (raw2012);
CREATE INDEX raw2012_01_idx on raw2012_01(station, valid);
CREATE INDEX raw2012_01_valid_idx on raw2012_01(valid);
grant select on raw2012_01 to nobody,apache;

create table raw2012_02( 
  CONSTRAINT __raw2012_02_check 
  CHECK(valid >= '2012-02-01 00:00+00'::timestamptz 
        and valid < '2012-03-01 00:00+00')) 
  INHERITS (raw2012);
CREATE INDEX raw2012_02_idx on raw2012_02(station, valid);
CREATE INDEX raw2012_02_valid_idx on raw2012_02(valid);
grant select on raw2012_02 to nobody,apache;

create table raw2012_03( 
  CONSTRAINT __raw2012_03_check 
  CHECK(valid >= '2012-03-01 00:00+00'::timestamptz 
        and valid < '2012-04-01 00:00+00')) 
  INHERITS (raw2012);
CREATE INDEX raw2012_03_idx on raw2012_03(station, valid);
CREATE INDEX raw2012_03_valid_idx on raw2012_03(valid);
grant select on raw2012_03 to nobody,apache;

create table raw2012_04( 
  CONSTRAINT __raw2012_04_check 
  CHECK(valid >= '2012-04-01 00:00+00'::timestamptz 
        and valid < '2012-05-01 00:00+00')) 
  INHERITS (raw2012);
CREATE INDEX raw2012_04_idx on raw2012_04(station, valid);
CREATE INDEX raw2012_04_valid_idx on raw2012_04(valid);
grant select on raw2012_04 to nobody,apache;

create table raw2012_05( 
  CONSTRAINT __raw2012_05_check 
  CHECK(valid >= '2012-05-01 00:00+00'::timestamptz 
        and valid < '2012-06-01 00:00+00')) 
  INHERITS (raw2012);
CREATE INDEX raw2012_05_idx on raw2012_05(station, valid);
CREATE INDEX raw2012_05_valid_idx on raw2012_05(valid);
grant select on raw2012_05 to nobody,apache;

create table raw2012_06( 
  CONSTRAINT __raw2012_06_check 
  CHECK(valid >= '2012-06-01 00:00+00'::timestamptz 
        and valid < '2012-07-01 00:00+00')) 
  INHERITS (raw2012);
CREATE INDEX raw2012_06_idx on raw2012_06(station, valid);
CREATE INDEX raw2012_06_valid_idx on raw2012_06(valid);
grant select on raw2012_06 to nobody,apache;

create table raw2012_07( 
  CONSTRAINT __raw2012_07_check 
  CHECK(valid >= '2012-07-01 00:00+00'::timestamptz 
        and valid < '2012-08-01 00:00+00')) 
  INHERITS (raw2012);
CREATE INDEX raw2012_07_idx on raw2012_07(station, valid);
CREATE INDEX raw2012_07_valid_idx on raw2012_07(valid);
grant select on raw2012_07 to nobody,apache;

create table raw2012_08( 
  CONSTRAINT __raw2012_08_check 
  CHECK(valid >= '2012-08-01 00:00+00'::timestamptz 
        and valid < '2012-09-01 00:00+00')) 
  INHERITS (raw2012);
CREATE INDEX raw2012_08_idx on raw2012_08(station, valid);
CREATE INDEX raw2012_08_valid_idx on raw2012_08(valid);
grant select on raw2012_08 to nobody,apache;

create table raw2012_09( 
  CONSTRAINT __raw2012_09_check 
  CHECK(valid >= '2012-09-01 00:00+00'::timestamptz 
        and valid < '2012-10-01 00:00+00')) 
  INHERITS (raw2012);
CREATE INDEX raw2012_09_idx on raw2012_09(station, valid);
CREATE INDEX raw2012_09_valid_idx on raw2012_09(valid);
grant select on raw2012_09 to nobody,apache;

create table raw2012_10( 
  CONSTRAINT __raw2012_10_check 
  CHECK(valid >= '2012-10-01 00:00+00'::timestamptz 
        and valid < '2012-11-01 00:00+00')) 
  INHERITS (raw2012);
CREATE INDEX raw2012_10_idx on raw2012_10(station, valid);
CREATE INDEX raw2012_10_valid_idx on raw2012_10(valid);
grant select on raw2012_10 to nobody,apache;

create table raw2012_11( 
  CONSTRAINT __raw2012_11_check 
  CHECK(valid >= '2012-11-01 00:00+00'::timestamptz 
        and valid < '2012-12-01 00:00+00')) 
  INHERITS (raw2012);
CREATE INDEX raw2012_11_idx on raw2012_11(station, valid);
CREATE INDEX raw2012_11_valid_idx on raw2012_11(valid);
grant select on raw2012_11 to nobody,apache;

create table raw2012_12( 
  CONSTRAINT __raw2012_12_check 
  CHECK(valid >= '2012-12-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (raw2012);
CREATE INDEX raw2012_12_idx on raw2012_12(station, valid);
CREATE INDEX raw2012_12_valid_idx on raw2012_12(valid);
grant select on raw2012_12 to nobody,apache;
    

---
---
---
CREATE TABLE raw2013(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2013 to nobody,apache;

create table raw2013_01( 
  CONSTRAINT __raw2013_01_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2013-02-01 00:00+00')) 
  INHERITS (raw2013);
CREATE INDEX raw2013_01_idx on raw2013_01(station, valid);
CREATE INDEX raw2013_01_valid_idx on raw2013_01(valid);
grant select on raw2013_01 to nobody,apache;

create table raw2013_02( 
  CONSTRAINT __raw2013_02_check 
  CHECK(valid >= '2013-02-01 00:00+00'::timestamptz 
        and valid < '2013-03-01 00:00+00')) 
  INHERITS (raw2013);
CREATE INDEX raw2013_02_idx on raw2013_02(station, valid);
CREATE INDEX raw2013_02_valid_idx on raw2013_02(valid);
grant select on raw2013_02 to nobody,apache;

create table raw2013_03( 
  CONSTRAINT __raw2013_03_check 
  CHECK(valid >= '2013-03-01 00:00+00'::timestamptz 
        and valid < '2013-04-01 00:00+00')) 
  INHERITS (raw2013);
CREATE INDEX raw2013_03_idx on raw2013_03(station, valid);
CREATE INDEX raw2013_03_valid_idx on raw2013_03(valid);
grant select on raw2013_03 to nobody,apache;

create table raw2013_04( 
  CONSTRAINT __raw2013_04_check 
  CHECK(valid >= '2013-04-01 00:00+00'::timestamptz 
        and valid < '2013-05-01 00:00+00')) 
  INHERITS (raw2013);
CREATE INDEX raw2013_04_idx on raw2013_04(station, valid);
CREATE INDEX raw2013_04_valid_idx on raw2013_04(valid);
grant select on raw2013_04 to nobody,apache;

create table raw2013_05( 
  CONSTRAINT __raw2013_05_check 
  CHECK(valid >= '2013-05-01 00:00+00'::timestamptz 
        and valid < '2013-06-01 00:00+00')) 
  INHERITS (raw2013);
CREATE INDEX raw2013_05_idx on raw2013_05(station, valid);
CREATE INDEX raw2013_05_valid_idx on raw2013_05(valid);
grant select on raw2013_05 to nobody,apache;

create table raw2013_06( 
  CONSTRAINT __raw2013_06_check 
  CHECK(valid >= '2013-06-01 00:00+00'::timestamptz 
        and valid < '2013-07-01 00:00+00')) 
  INHERITS (raw2013);
CREATE INDEX raw2013_06_idx on raw2013_06(station, valid);
CREATE INDEX raw2013_06_valid_idx on raw2013_06(valid);
grant select on raw2013_06 to nobody,apache;

create table raw2013_07( 
  CONSTRAINT __raw2013_07_check 
  CHECK(valid >= '2013-07-01 00:00+00'::timestamptz 
        and valid < '2013-08-01 00:00+00')) 
  INHERITS (raw2013);
CREATE INDEX raw2013_07_idx on raw2013_07(station, valid);
CREATE INDEX raw2013_07_valid_idx on raw2013_07(valid);
grant select on raw2013_07 to nobody,apache;

create table raw2013_08( 
  CONSTRAINT __raw2013_08_check 
  CHECK(valid >= '2013-08-01 00:00+00'::timestamptz 
        and valid < '2013-09-01 00:00+00')) 
  INHERITS (raw2013);
CREATE INDEX raw2013_08_idx on raw2013_08(station, valid);
CREATE INDEX raw2013_08_valid_idx on raw2013_08(valid);
grant select on raw2013_08 to nobody,apache;

create table raw2013_09( 
  CONSTRAINT __raw2013_09_check 
  CHECK(valid >= '2013-09-01 00:00+00'::timestamptz 
        and valid < '2013-10-01 00:00+00')) 
  INHERITS (raw2013);
CREATE INDEX raw2013_09_idx on raw2013_09(station, valid);
CREATE INDEX raw2013_09_valid_idx on raw2013_09(valid);
grant select on raw2013_09 to nobody,apache;

create table raw2013_10( 
  CONSTRAINT __raw2013_10_check 
  CHECK(valid >= '2013-10-01 00:00+00'::timestamptz 
        and valid < '2013-11-01 00:00+00')) 
  INHERITS (raw2013);
CREATE INDEX raw2013_10_idx on raw2013_10(station, valid);
CREATE INDEX raw2013_10_valid_idx on raw2013_10(valid);
grant select on raw2013_10 to nobody,apache;

create table raw2013_11( 
  CONSTRAINT __raw2013_11_check 
  CHECK(valid >= '2013-11-01 00:00+00'::timestamptz 
        and valid < '2013-12-01 00:00+00')) 
  INHERITS (raw2013);
CREATE INDEX raw2013_11_idx on raw2013_11(station, valid);
CREATE INDEX raw2013_11_valid_idx on raw2013_11(valid);
grant select on raw2013_11 to nobody,apache;

create table raw2013_12( 
  CONSTRAINT __raw2013_12_check 
  CHECK(valid >= '2013-12-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (raw2013);
CREATE INDEX raw2013_12_idx on raw2013_12(station, valid);
CREATE INDEX raw2013_12_valid_idx on raw2013_12(valid);
grant select on raw2013_12 to nobody,apache;


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

---
---
---
CREATE TABLE raw2015(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2015 to nobody,apache;

create table raw2015_01( 
  CONSTRAINT __raw2015_01_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2015-02-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_01_idx on raw2015_01(station, valid);
CREATE INDEX raw2015_01_valid_idx on raw2015_01(valid);
grant select on raw2015_01 to nobody,apache;

create table raw2015_02( 
  CONSTRAINT __raw2015_02_check 
  CHECK(valid >= '2015-02-01 00:00+00'::timestamptz 
        and valid < '2015-03-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_02_idx on raw2015_02(station, valid);
CREATE INDEX raw2015_02_valid_idx on raw2015_02(valid);
grant select on raw2015_02 to nobody,apache;

create table raw2015_03( 
  CONSTRAINT __raw2015_03_check 
  CHECK(valid >= '2015-03-01 00:00+00'::timestamptz 
        and valid < '2015-04-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_03_idx on raw2015_03(station, valid);
CREATE INDEX raw2015_03_valid_idx on raw2015_03(valid);
grant select on raw2015_03 to nobody,apache;

create table raw2015_04( 
  CONSTRAINT __raw2015_04_check 
  CHECK(valid >= '2015-04-01 00:00+00'::timestamptz 
        and valid < '2015-05-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_04_idx on raw2015_04(station, valid);
CREATE INDEX raw2015_04_valid_idx on raw2015_04(valid);
grant select on raw2015_04 to nobody,apache;

create table raw2015_05( 
  CONSTRAINT __raw2015_05_check 
  CHECK(valid >= '2015-05-01 00:00+00'::timestamptz 
        and valid < '2015-06-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_05_idx on raw2015_05(station, valid);
CREATE INDEX raw2015_05_valid_idx on raw2015_05(valid);
grant select on raw2015_05 to nobody,apache;

create table raw2015_06( 
  CONSTRAINT __raw2015_06_check 
  CHECK(valid >= '2015-06-01 00:00+00'::timestamptz 
        and valid < '2015-07-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_06_idx on raw2015_06(station, valid);
CREATE INDEX raw2015_06_valid_idx on raw2015_06(valid);
grant select on raw2015_06 to nobody,apache;

create table raw2015_07( 
  CONSTRAINT __raw2015_07_check 
  CHECK(valid >= '2015-07-01 00:00+00'::timestamptz 
        and valid < '2015-08-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_07_idx on raw2015_07(station, valid);
CREATE INDEX raw2015_07_valid_idx on raw2015_07(valid);
grant select on raw2015_07 to nobody,apache;

create table raw2015_08( 
  CONSTRAINT __raw2015_08_check 
  CHECK(valid >= '2015-08-01 00:00+00'::timestamptz 
        and valid < '2015-09-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_08_idx on raw2015_08(station, valid);
CREATE INDEX raw2015_08_valid_idx on raw2015_08(valid);
grant select on raw2015_08 to nobody,apache;

create table raw2015_09( 
  CONSTRAINT __raw2015_09_check 
  CHECK(valid >= '2015-09-01 00:00+00'::timestamptz 
        and valid < '2015-10-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_09_idx on raw2015_09(station, valid);
CREATE INDEX raw2015_09_valid_idx on raw2015_09(valid);
grant select on raw2015_09 to nobody,apache;

create table raw2015_10( 
  CONSTRAINT __raw2015_10_check 
  CHECK(valid >= '2015-10-01 00:00+00'::timestamptz 
        and valid < '2015-11-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_10_idx on raw2015_10(station, valid);
CREATE INDEX raw2015_10_valid_idx on raw2015_10(valid);
grant select on raw2015_10 to nobody,apache;

create table raw2015_11( 
  CONSTRAINT __raw2015_11_check 
  CHECK(valid >= '2015-11-01 00:00+00'::timestamptz 
        and valid < '2015-12-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_11_idx on raw2015_11(station, valid);
CREATE INDEX raw2015_11_valid_idx on raw2015_11(valid);
grant select on raw2015_11 to nobody,apache;

create table raw2015_12( 
  CONSTRAINT __raw2015_12_check 
  CHECK(valid >= '2015-12-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_12_idx on raw2015_12(station, valid);
CREATE INDEX raw2015_12_valid_idx on raw2015_12(valid);
grant select on raw2015_12 to nobody,apache;

-- Need a faster storage for inbound data, adding it to tables with indexes
-- was too expensive
CREATE TABLE raw_inbound(
        station varchar(8),
        valid timestamptz,
        key varchar(11),
        value real
);
CREATE TABLE raw_inbound_tmp(
        station varchar(8),
        valid timestamptz,
        key varchar(11),
        value real
);

---
---
---
CREATE TABLE raw2016(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2016 to nobody,apache;

create table raw2016_01( 
  CONSTRAINT __raw2016_01_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2016-02-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_01_idx on raw2016_01(station, valid);
CREATE INDEX raw2016_01_valid_idx on raw2016_01(valid);
grant select on raw2016_01 to nobody,apache;

create table raw2016_02( 
  CONSTRAINT __raw2016_02_check 
  CHECK(valid >= '2016-02-01 00:00+00'::timestamptz 
        and valid < '2016-03-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_02_idx on raw2016_02(station, valid);
CREATE INDEX raw2016_02_valid_idx on raw2016_02(valid);
grant select on raw2016_02 to nobody,apache;

create table raw2016_03( 
  CONSTRAINT __raw2016_03_check 
  CHECK(valid >= '2016-03-01 00:00+00'::timestamptz 
        and valid < '2016-04-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_03_idx on raw2016_03(station, valid);
CREATE INDEX raw2016_03_valid_idx on raw2016_03(valid);
grant select on raw2016_03 to nobody,apache;

create table raw2016_04( 
  CONSTRAINT __raw2016_04_check 
  CHECK(valid >= '2016-04-01 00:00+00'::timestamptz 
        and valid < '2016-05-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_04_idx on raw2016_04(station, valid);
CREATE INDEX raw2016_04_valid_idx on raw2016_04(valid);
grant select on raw2016_04 to nobody,apache;

create table raw2016_05( 
  CONSTRAINT __raw2016_05_check 
  CHECK(valid >= '2016-05-01 00:00+00'::timestamptz 
        and valid < '2016-06-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_05_idx on raw2016_05(station, valid);
CREATE INDEX raw2016_05_valid_idx on raw2016_05(valid);
grant select on raw2016_05 to nobody,apache;

create table raw2016_06( 
  CONSTRAINT __raw2016_06_check 
  CHECK(valid >= '2016-06-01 00:00+00'::timestamptz 
        and valid < '2016-07-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_06_idx on raw2016_06(station, valid);
CREATE INDEX raw2016_06_valid_idx on raw2016_06(valid);
grant select on raw2016_06 to nobody,apache;

create table raw2016_07( 
  CONSTRAINT __raw2016_07_check 
  CHECK(valid >= '2016-07-01 00:00+00'::timestamptz 
        and valid < '2016-08-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_07_idx on raw2016_07(station, valid);
CREATE INDEX raw2016_07_valid_idx on raw2016_07(valid);
grant select on raw2016_07 to nobody,apache;

create table raw2016_08( 
  CONSTRAINT __raw2016_08_check 
  CHECK(valid >= '2016-08-01 00:00+00'::timestamptz 
        and valid < '2016-09-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_08_idx on raw2016_08(station, valid);
CREATE INDEX raw2016_08_valid_idx on raw2016_08(valid);
grant select on raw2016_08 to nobody,apache;

create table raw2016_09( 
  CONSTRAINT __raw2016_09_check 
  CHECK(valid >= '2016-09-01 00:00+00'::timestamptz 
        and valid < '2016-10-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_09_idx on raw2016_09(station, valid);
CREATE INDEX raw2016_09_valid_idx on raw2016_09(valid);
grant select on raw2016_09 to nobody,apache;

create table raw2016_10( 
  CONSTRAINT __raw2016_10_check 
  CHECK(valid >= '2016-10-01 00:00+00'::timestamptz 
        and valid < '2016-11-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_10_idx on raw2016_10(station, valid);
CREATE INDEX raw2016_10_valid_idx on raw2016_10(valid);
grant select on raw2016_10 to nobody,apache;

create table raw2016_11( 
  CONSTRAINT __raw2016_11_check 
  CHECK(valid >= '2016-11-01 00:00+00'::timestamptz 
        and valid < '2016-12-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_11_idx on raw2016_11(station, valid);
CREATE INDEX raw2016_11_valid_idx on raw2016_11(valid);
grant select on raw2016_11 to nobody,apache;

create table raw2016_12( 
  CONSTRAINT __raw2016_12_check 
  CHECK(valid >= '2016-12-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_12_idx on raw2016_12(station, valid);
CREATE INDEX raw2016_12_valid_idx on raw2016_12(valid);
grant select on raw2016_12 to nobody,apache;

-- Storage of HML forecasts
DROP TABLE IF EXISTS hml_forecast_data_2016;
DROP TABLE IF EXISTS hml_forecast;
CREATE TABLE hml_forecast(
  id SERIAL UNIQUE,
  station varchar(8),
  generationtime timestamptz,
  issued timestamptz,
  forecast_sts timestamptz,
  forecast_ets timestamptz,
  originator varchar(8),
  product_id varchar(32),
  primaryname varchar(64),
  primaryunits varchar(64),
  secondaryname varchar(64),
  secondaryunits varchar(64));
CREATE INDEX hml_forecast_idx on hml_forecast(station, generationtime);
GRANT SELECT on hml_forecast to nobody,apache;

CREATE TABLE hml_forecast_data_2016(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2016_idx on
  hml_forecast_data_2016(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2016 to nobody,apache;

CREATE TABLE hml_observed_keys(
  id smallint UNIQUE,
  label varchar(32));
GRANT SELECT on hml_observed_keys to nobody,apache;

INSERT into hml_observed_keys values
 (0, 'Depth Below Sfc[ft]'),
 (1, 'Discharge Velocity[mph]'),
 (2, 'Flow[kcfs]'),
 (3, 'Forebay Elevation[ft]'),
 (4, 'Generator Discharge[kcfs]'),
 (5, 'Inflow Discharge[kcfs]'),
 (6, 'Lake Elev Abv Datum[ft]'),
 (7, 'Lake Elevation[ft]'),
 (8, 'Pool[ft]'),
 (9, 'Precip[inches]'),
 (10, 'Reading Height - MSL[ft]'),
 (11, 'Reading Height - Sfc[ft]'),
 (12, 'River Discharge[kcfs]'),
 (13, 'Spillway Tailwater[ft]'),
 (14, 'Stage[ft]'),
 (15, 'Stage Trnd Indicator[code]'),
 (16, 'Tailwater[ft]'),
 (17, 'Tide Height[ft]'),
 (18, 'Total Discharge[kcfs]');


CREATE FUNCTION get_hml_observed_key(text)
RETURNS smallint
LANGUAGE sql
AS $_$
  SELECT id from hml_observed_keys where label = $1
$_$;

DROP TABLE IF EXISTS hml_observed_data_2016;
DROP TABLE IF EXISTS hml_observed_data;
CREATE TABLE hml_observed_data(
	station varchar(8),
	valid timestamptz,
	key smallint REFERENCES hml_observed_keys(id),
	value real);
GRANT SELECT on hml_observed_data to nobody,apache;

create table hml_observed_data_2016(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2016_check
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz
        and valid < '2017-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2016_idx on
	hml_observed_data_2016(station, valid);
GRANT SELECT on hml_observed_data_2016 to nobody,apache;

-- Add older table
CREATE TABLE hml_forecast_data_2014(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2014_idx on
  hml_forecast_data_2014(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2014 to nobody,apache;

CREATE TABLE hml_forecast_data_2015(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2015_idx on
  hml_forecast_data_2015(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2015 to nobody,apache;

create table hml_observed_data_2014(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2014_check
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz
        and valid < '2015-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2014_idx on
	hml_observed_data_2014(station, valid);
GRANT SELECT on hml_observed_data_2014 to nobody,apache;

create table hml_observed_data_2015(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2015_check
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz
        and valid < '2016-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2015_idx on
	hml_observed_data_2015(station, valid);
GRANT SELECT on hml_observed_data_2015 to nobody,apache;

--
CREATE TABLE hml_forecast_data_2012(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2012_idx on
  hml_forecast_data_2012(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2012 to nobody,apache;

CREATE TABLE hml_forecast_data_2013(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2013_idx on
  hml_forecast_data_2013(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2013 to nobody,apache;

create table hml_observed_data_2012(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2012_check
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz
        and valid < '2013-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2012_idx on
	hml_observed_data_2012(station, valid);
GRANT SELECT on hml_observed_data_2012 to nobody,apache;

create table hml_observed_data_2013(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2013_check
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz
        and valid < '2014-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2013_idx on
	hml_observed_data_2013(station, valid);
GRANT SELECT on hml_observed_data_2013 to nobody,apache;

CREATE INDEX hml_forecast_issued_idx on hml_forecast(issued);

---
---
---
CREATE TABLE raw2017(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2017 to nobody,apache;

create table raw2017_01( 
  CONSTRAINT __raw2017_01_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2017-02-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_01_idx on raw2017_01(station, valid);
CREATE INDEX raw2017_01_valid_idx on raw2017_01(valid);
grant select on raw2017_01 to nobody,apache;

create table raw2017_02( 
  CONSTRAINT __raw2017_02_check 
  CHECK(valid >= '2017-02-01 00:00+00'::timestamptz 
        and valid < '2017-03-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_02_idx on raw2017_02(station, valid);
CREATE INDEX raw2017_02_valid_idx on raw2017_02(valid);
grant select on raw2017_02 to nobody,apache;

create table raw2017_03( 
  CONSTRAINT __raw2017_03_check 
  CHECK(valid >= '2017-03-01 00:00+00'::timestamptz 
        and valid < '2017-04-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_03_idx on raw2017_03(station, valid);
CREATE INDEX raw2017_03_valid_idx on raw2017_03(valid);
grant select on raw2017_03 to nobody,apache;

create table raw2017_04( 
  CONSTRAINT __raw2017_04_check 
  CHECK(valid >= '2017-04-01 00:00+00'::timestamptz 
        and valid < '2017-05-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_04_idx on raw2017_04(station, valid);
CREATE INDEX raw2017_04_valid_idx on raw2017_04(valid);
grant select on raw2017_04 to nobody,apache;

create table raw2017_05( 
  CONSTRAINT __raw2017_05_check 
  CHECK(valid >= '2017-05-01 00:00+00'::timestamptz 
        and valid < '2017-06-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_05_idx on raw2017_05(station, valid);
CREATE INDEX raw2017_05_valid_idx on raw2017_05(valid);
grant select on raw2017_05 to nobody,apache;

create table raw2017_06( 
  CONSTRAINT __raw2017_06_check 
  CHECK(valid >= '2017-06-01 00:00+00'::timestamptz 
        and valid < '2017-07-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_06_idx on raw2017_06(station, valid);
CREATE INDEX raw2017_06_valid_idx on raw2017_06(valid);
grant select on raw2017_06 to nobody,apache;

create table raw2017_07( 
  CONSTRAINT __raw2017_07_check 
  CHECK(valid >= '2017-07-01 00:00+00'::timestamptz 
        and valid < '2017-08-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_07_idx on raw2017_07(station, valid);
CREATE INDEX raw2017_07_valid_idx on raw2017_07(valid);
grant select on raw2017_07 to nobody,apache;

create table raw2017_08( 
  CONSTRAINT __raw2017_08_check 
  CHECK(valid >= '2017-08-01 00:00+00'::timestamptz 
        and valid < '2017-09-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_08_idx on raw2017_08(station, valid);
CREATE INDEX raw2017_08_valid_idx on raw2017_08(valid);
grant select on raw2017_08 to nobody,apache;

create table raw2017_09( 
  CONSTRAINT __raw2017_09_check 
  CHECK(valid >= '2017-09-01 00:00+00'::timestamptz 
        and valid < '2017-10-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_09_idx on raw2017_09(station, valid);
CREATE INDEX raw2017_09_valid_idx on raw2017_09(valid);
grant select on raw2017_09 to nobody,apache;

create table raw2017_10( 
  CONSTRAINT __raw2017_10_check 
  CHECK(valid >= '2017-10-01 00:00+00'::timestamptz 
        and valid < '2017-11-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_10_idx on raw2017_10(station, valid);
CREATE INDEX raw2017_10_valid_idx on raw2017_10(valid);
grant select on raw2017_10 to nobody,apache;

create table raw2017_11( 
  CONSTRAINT __raw2017_11_check 
  CHECK(valid >= '2017-11-01 00:00+00'::timestamptz 
        and valid < '2017-12-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_11_idx on raw2017_11(station, valid);
CREATE INDEX raw2017_11_valid_idx on raw2017_11(valid);
grant select on raw2017_11 to nobody,apache;

create table raw2017_12( 
  CONSTRAINT __raw2017_12_check 
  CHECK(valid >= '2017-12-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_12_idx on raw2017_12(station, valid);
CREATE INDEX raw2017_12_valid_idx on raw2017_12(valid);
grant select on raw2017_12 to nobody,apache;


---
---
---
CREATE TABLE raw2018(
    station varchar(8),
    valid timestamptz,
    key varchar(11),
    value real
);
GRANT SELECT on raw2018 to nobody,apache;

create table raw2018_01( 
  CONSTRAINT __raw2018_01_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz 
        and valid < '2018-02-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_01_idx on raw2018_01(station, valid);
CREATE INDEX raw2018_01_valid_idx on raw2018_01(valid);
grant select on raw2018_01 to nobody,apache;

create table raw2018_02( 
  CONSTRAINT __raw2018_02_check 
  CHECK(valid >= '2018-02-01 00:00+00'::timestamptz 
        and valid < '2018-03-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_02_idx on raw2018_02(station, valid);
CREATE INDEX raw2018_02_valid_idx on raw2018_02(valid);
grant select on raw2018_02 to nobody,apache;

create table raw2018_03( 
  CONSTRAINT __raw2018_03_check 
  CHECK(valid >= '2018-03-01 00:00+00'::timestamptz 
        and valid < '2018-04-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_03_idx on raw2018_03(station, valid);
CREATE INDEX raw2018_03_valid_idx on raw2018_03(valid);
grant select on raw2018_03 to nobody,apache;

create table raw2018_04( 
  CONSTRAINT __raw2018_04_check 
  CHECK(valid >= '2018-04-01 00:00+00'::timestamptz 
        and valid < '2018-05-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_04_idx on raw2018_04(station, valid);
CREATE INDEX raw2018_04_valid_idx on raw2018_04(valid);
grant select on raw2018_04 to nobody,apache;

create table raw2018_05( 
  CONSTRAINT __raw2018_05_check 
  CHECK(valid >= '2018-05-01 00:00+00'::timestamptz 
        and valid < '2018-06-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_05_idx on raw2018_05(station, valid);
CREATE INDEX raw2018_05_valid_idx on raw2018_05(valid);
grant select on raw2018_05 to nobody,apache;

create table raw2018_06( 
  CONSTRAINT __raw2018_06_check 
  CHECK(valid >= '2018-06-01 00:00+00'::timestamptz 
        and valid < '2018-07-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_06_idx on raw2018_06(station, valid);
CREATE INDEX raw2018_06_valid_idx on raw2018_06(valid);
grant select on raw2018_06 to nobody,apache;

create table raw2018_07( 
  CONSTRAINT __raw2018_07_check 
  CHECK(valid >= '2018-07-01 00:00+00'::timestamptz 
        and valid < '2018-08-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_07_idx on raw2018_07(station, valid);
CREATE INDEX raw2018_07_valid_idx on raw2018_07(valid);
grant select on raw2018_07 to nobody,apache;

create table raw2018_08( 
  CONSTRAINT __raw2018_08_check 
  CHECK(valid >= '2018-08-01 00:00+00'::timestamptz 
        and valid < '2018-09-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_08_idx on raw2018_08(station, valid);
CREATE INDEX raw2018_08_valid_idx on raw2018_08(valid);
grant select on raw2018_08 to nobody,apache;

create table raw2018_09( 
  CONSTRAINT __raw2018_09_check 
  CHECK(valid >= '2018-09-01 00:00+00'::timestamptz 
        and valid < '2018-10-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_09_idx on raw2018_09(station, valid);
CREATE INDEX raw2018_09_valid_idx on raw2018_09(valid);
grant select on raw2018_09 to nobody,apache;

create table raw2018_10( 
  CONSTRAINT __raw2018_10_check 
  CHECK(valid >= '2018-10-01 00:00+00'::timestamptz 
        and valid < '2018-11-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_10_idx on raw2018_10(station, valid);
CREATE INDEX raw2018_10_valid_idx on raw2018_10(valid);
grant select on raw2018_10 to nobody,apache;

create table raw2018_11( 
  CONSTRAINT __raw2018_11_check 
  CHECK(valid >= '2018-11-01 00:00+00'::timestamptz 
        and valid < '2018-12-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_11_idx on raw2018_11(station, valid);
CREATE INDEX raw2018_11_valid_idx on raw2018_11(valid);
grant select on raw2018_11 to nobody,apache;

create table raw2018_12( 
  CONSTRAINT __raw2018_12_check 
  CHECK(valid >= '2018-12-01 00:00+00'::timestamptz 
        and valid < '2019-01-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_12_idx on raw2018_12(station, valid);
CREATE INDEX raw2018_12_valid_idx on raw2018_12(valid);
grant select on raw2018_12 to nobody,apache;

---
---
---
CREATE TABLE raw2019(
    station varchar(8),
    valid timestamptz,
    key varchar(11),
    value real
);
GRANT SELECT on raw2019 to nobody,apache;

create table raw2019_01( 
  CONSTRAINT __raw2019_01_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz 
        and valid < '2019-02-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_01_idx on raw2019_01(station, valid);
CREATE INDEX raw2019_01_valid_idx on raw2019_01(valid);
grant select on raw2019_01 to nobody,apache;

create table raw2019_02( 
  CONSTRAINT __raw2019_02_check 
  CHECK(valid >= '2019-02-01 00:00+00'::timestamptz 
        and valid < '2019-03-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_02_idx on raw2019_02(station, valid);
CREATE INDEX raw2019_02_valid_idx on raw2019_02(valid);
grant select on raw2019_02 to nobody,apache;

create table raw2019_03( 
  CONSTRAINT __raw2019_03_check 
  CHECK(valid >= '2019-03-01 00:00+00'::timestamptz 
        and valid < '2019-04-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_03_idx on raw2019_03(station, valid);
CREATE INDEX raw2019_03_valid_idx on raw2019_03(valid);
grant select on raw2019_03 to nobody,apache;

create table raw2019_04( 
  CONSTRAINT __raw2019_04_check 
  CHECK(valid >= '2019-04-01 00:00+00'::timestamptz 
        and valid < '2019-05-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_04_idx on raw2019_04(station, valid);
CREATE INDEX raw2019_04_valid_idx on raw2019_04(valid);
grant select on raw2019_04 to nobody,apache;

create table raw2019_05( 
  CONSTRAINT __raw2019_05_check 
  CHECK(valid >= '2019-05-01 00:00+00'::timestamptz 
        and valid < '2019-06-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_05_idx on raw2019_05(station, valid);
CREATE INDEX raw2019_05_valid_idx on raw2019_05(valid);
grant select on raw2019_05 to nobody,apache;

create table raw2019_06( 
  CONSTRAINT __raw2019_06_check 
  CHECK(valid >= '2019-06-01 00:00+00'::timestamptz 
        and valid < '2019-07-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_06_idx on raw2019_06(station, valid);
CREATE INDEX raw2019_06_valid_idx on raw2019_06(valid);
grant select on raw2019_06 to nobody,apache;

create table raw2019_07( 
  CONSTRAINT __raw2019_07_check 
  CHECK(valid >= '2019-07-01 00:00+00'::timestamptz 
        and valid < '2019-08-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_07_idx on raw2019_07(station, valid);
CREATE INDEX raw2019_07_valid_idx on raw2019_07(valid);
grant select on raw2019_07 to nobody,apache;

create table raw2019_08( 
  CONSTRAINT __raw2019_08_check 
  CHECK(valid >= '2019-08-01 00:00+00'::timestamptz 
        and valid < '2019-09-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_08_idx on raw2019_08(station, valid);
CREATE INDEX raw2019_08_valid_idx on raw2019_08(valid);
grant select on raw2019_08 to nobody,apache;

create table raw2019_09( 
  CONSTRAINT __raw2019_09_check 
  CHECK(valid >= '2019-09-01 00:00+00'::timestamptz 
        and valid < '2019-10-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_09_idx on raw2019_09(station, valid);
CREATE INDEX raw2019_09_valid_idx on raw2019_09(valid);
grant select on raw2019_09 to nobody,apache;

create table raw2019_10( 
  CONSTRAINT __raw2019_10_check 
  CHECK(valid >= '2019-10-01 00:00+00'::timestamptz 
        and valid < '2019-11-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_10_idx on raw2019_10(station, valid);
CREATE INDEX raw2019_10_valid_idx on raw2019_10(valid);
grant select on raw2019_10 to nobody,apache;

create table raw2019_11( 
  CONSTRAINT __raw2019_11_check 
  CHECK(valid >= '2019-11-01 00:00+00'::timestamptz 
        and valid < '2019-12-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_11_idx on raw2019_11(station, valid);
CREATE INDEX raw2019_11_valid_idx on raw2019_11(valid);
grant select on raw2019_11 to nobody,apache;

create table raw2019_12( 
  CONSTRAINT __raw2019_12_check 
  CHECK(valid >= '2019-12-01 00:00+00'::timestamptz 
        and valid < '2020-01-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_12_idx on raw2019_12(station, valid);
CREATE INDEX raw2019_12_valid_idx on raw2019_12(valid);
grant select on raw2019_12 to nobody,apache;


CREATE TABLE hml_forecast_data_2017(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2017_idx on
  hml_forecast_data_2017(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2017 to nobody,apache;

create table hml_observed_data_2017(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2017_check
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz
        and valid < '2018-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2017_idx on
        hml_observed_data_2017(station, valid);
GRANT SELECT on hml_observed_data_2017 to nobody,apache;

CREATE TABLE hml_forecast_data_2018(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2018_idx on
  hml_forecast_data_2018(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2018 to nobody,apache;

create table hml_observed_data_2018(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2018_check
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2018_idx on
        hml_observed_data_2018(station, valid);
GRANT SELECT on hml_observed_data_2018 to nobody,apache;

CREATE TABLE hml_forecast_data_2019(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2019_idx on
  hml_forecast_data_2019(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2019 to nobody,apache;

create table hml_observed_data_2019(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2019_check
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2019_idx on
        hml_observed_data_2019(station, valid);
GRANT SELECT on hml_observed_data_2019 to nobody,apache;

-- Storage of common / instantaneous data values
CREATE TABLE alldata(
	station varchar(8),
	valid timestamptz,
	tmpf real,
	dwpf real,
	sknt real,
	drct real);
GRANT SELECT on alldata to nobody,apache;

create table t2002( 
  CONSTRAINT __t2002_check 
  CHECK(valid >= '2002-01-01 00:00+00'::timestamptz 
        and valid < '2003-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_idx on t2002(station, valid);
CREATE INDEX t2002_valid_idx on t2002(valid);
grant select on t2002 to nobody,apache;

create table t2003( 
  CONSTRAINT __t2003_check 
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz 
        and valid < '2004-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_idx on t2003(station, valid);
CREATE INDEX t2003_valid_idx on t2003(valid);
grant select on t2003 to nobody,apache;


create table t2004( 
  CONSTRAINT __t2004_check 
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz 
        and valid < '2005-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_idx on t2004(station, valid);
CREATE INDEX t2004_valid_idx on t2004(valid);
grant select on t2004 to nobody,apache;


create table t2005( 
  CONSTRAINT __t2005_check 
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz 
        and valid < '2006-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_idx on t2005(station, valid);
CREATE INDEX t2005_valid_idx on t2005(valid);
grant select on t2005 to nobody,apache;


create table t2006( 
  CONSTRAINT __t2006_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz 
        and valid < '2007-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_idx on t2006(station, valid);
CREATE INDEX t2006_valid_idx on t2006(valid);
grant select on t2006 to nobody,apache;


create table t2007( 
  CONSTRAINT __t2007_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz 
        and valid < '2008-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_idx on t2007(station, valid);
CREATE INDEX t2007_valid_idx on t2007(valid);
grant select on t2007 to nobody,apache;


create table t2008( 
  CONSTRAINT __t2008_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_idx on t2008(station, valid);
CREATE INDEX t2008_valid_idx on t2008(valid);
grant select on t2008 to nobody,apache;


create table t2009( 
  CONSTRAINT __t2009_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_idx on t2009(station, valid);
CREATE INDEX t2009_valid_idx on t2009(valid);
grant select on t2009 to nobody,apache;


create table t2010( 
  CONSTRAINT __t2010_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_idx on t2010(station, valid);
CREATE INDEX t2010_valid_idx on t2010(valid);
grant select on t2010 to nobody,apache;


create table t2011( 
  CONSTRAINT __t2011_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_idx on t2011(station, valid);
CREATE INDEX t2011_valid_idx on t2011(valid);
grant select on t2011 to nobody,apache;


create table t2012( 
  CONSTRAINT __t2012_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_idx on t2012(station, valid);
CREATE INDEX t2012_valid_idx on t2012(valid);
grant select on t2012 to nobody,apache;


create table t2013( 
  CONSTRAINT __t2013_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_idx on t2013(station, valid);
CREATE INDEX t2013_valid_idx on t2013(valid);
grant select on t2013 to nobody,apache;


create table t2014( 
  CONSTRAINT __t2014_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_idx on t2014(station, valid);
CREATE INDEX t2014_valid_idx on t2014(valid);
grant select on t2014 to nobody,apache;


create table t2015( 
  CONSTRAINT __t2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_idx on t2015(station, valid);
CREATE INDEX t2015_valid_idx on t2015(valid);
grant select on t2015 to nobody,apache;


create table t2016( 
  CONSTRAINT __t2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_idx on t2016(station, valid);
CREATE INDEX t2016_valid_idx on t2016(valid);
grant select on t2016 to nobody,apache;


create table t2017( 
  CONSTRAINT __t2017_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_idx on t2017(station, valid);
CREATE INDEX t2017_valid_idx on t2017(valid);
grant select on t2017 to nobody,apache;

create table t2018( 
  CONSTRAINT __t2018_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz 
        and valid < '2019-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_idx on t2018(station, valid);
CREATE INDEX t2018_valid_idx on t2018(valid);
grant select on t2018 to nobody,apache;

create table t2019( 
  CONSTRAINT __t2019_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz 
        and valid < '2020-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_idx on t2019(station, valid);
CREATE INDEX t2019_valid_idx on t2019(valid);
grant select on t2019 to nobody,apache;
