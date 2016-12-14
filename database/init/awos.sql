
-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (-1, now());

---
--- Main table that all children inherit from
---
CREATE TABLE alldata(
	station varchar(5),
	valid timestamptz,
	tmpf smallint,
	dwpf smallint,
	sknt smallint,
	drct smallint,
	gust smallint,
	p01i real,
	cl1 smallint,
	ca1 smallint,
	cl2 smallint,
	ca2 smallint,
	cl3 smallint,
	ca3 smallint,
	vsby real,
	alti real,
	qc varchar(5)
);
GRANT SELECT on alldata to nobody,apache;

create table t1994_11( 
  CONSTRAINT __t1994_11_check 
  CHECK(valid >= '1994-11-01 00:00+00'::timestamptz 
        and valid < '1994-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1994_11_station_idx on t1994_11(station);
CREATE INDEX t1994_11_valid_idx on t1994_11(valid);
GRANT SELECT on t1994_11 to nobody,apache;


create table t1994_12( 
  CONSTRAINT __t1994_12_check 
  CHECK(valid >= '1994-12-01 00:00+00'::timestamptz 
        and valid < '1995-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1994_12_station_idx on t1994_12(station);
CREATE INDEX t1994_12_valid_idx on t1994_12(valid);
GRANT SELECT on t1994_12 to nobody,apache;


create table t1995_01( 
  CONSTRAINT __t1995_01_check 
  CHECK(valid >= '1995-01-01 00:00+00'::timestamptz 
        and valid < '1995-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1995_01_station_idx on t1995_01(station);
CREATE INDEX t1995_01_valid_idx on t1995_01(valid);
GRANT SELECT on t1995_01 to nobody,apache;


create table t1995_02( 
  CONSTRAINT __t1995_02_check 
  CHECK(valid >= '1995-02-01 00:00+00'::timestamptz 
        and valid < '1995-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1995_02_station_idx on t1995_02(station);
CREATE INDEX t1995_02_valid_idx on t1995_02(valid);
GRANT SELECT on t1995_02 to nobody,apache;


create table t1995_03( 
  CONSTRAINT __t1995_03_check 
  CHECK(valid >= '1995-03-01 00:00+00'::timestamptz 
        and valid < '1995-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1995_03_station_idx on t1995_03(station);
CREATE INDEX t1995_03_valid_idx on t1995_03(valid);
GRANT SELECT on t1995_03 to nobody,apache;


create table t1995_04( 
  CONSTRAINT __t1995_04_check 
  CHECK(valid >= '1995-04-01 00:00+00'::timestamptz 
        and valid < '1995-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1995_04_station_idx on t1995_04(station);
CREATE INDEX t1995_04_valid_idx on t1995_04(valid);
GRANT SELECT on t1995_04 to nobody,apache;


create table t1995_05( 
  CONSTRAINT __t1995_05_check 
  CHECK(valid >= '1995-05-01 00:00+00'::timestamptz 
        and valid < '1995-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1995_05_station_idx on t1995_05(station);
CREATE INDEX t1995_05_valid_idx on t1995_05(valid);
GRANT SELECT on t1995_05 to nobody,apache;


create table t1995_06( 
  CONSTRAINT __t1995_06_check 
  CHECK(valid >= '1995-06-01 00:00+00'::timestamptz 
        and valid < '1995-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1995_06_station_idx on t1995_06(station);
CREATE INDEX t1995_06_valid_idx on t1995_06(valid);
GRANT SELECT on t1995_06 to nobody,apache;


create table t1995_07( 
  CONSTRAINT __t1995_07_check 
  CHECK(valid >= '1995-07-01 00:00+00'::timestamptz 
        and valid < '1995-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1995_07_station_idx on t1995_07(station);
CREATE INDEX t1995_07_valid_idx on t1995_07(valid);
GRANT SELECT on t1995_07 to nobody,apache;


create table t1995_08( 
  CONSTRAINT __t1995_08_check 
  CHECK(valid >= '1995-08-01 00:00+00'::timestamptz 
        and valid < '1995-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1995_08_station_idx on t1995_08(station);
CREATE INDEX t1995_08_valid_idx on t1995_08(valid);
GRANT SELECT on t1995_08 to nobody,apache;


create table t1995_09( 
  CONSTRAINT __t1995_09_check 
  CHECK(valid >= '1995-09-01 00:00+00'::timestamptz 
        and valid < '1995-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1995_09_station_idx on t1995_09(station);
CREATE INDEX t1995_09_valid_idx on t1995_09(valid);
GRANT SELECT on t1995_09 to nobody,apache;


create table t1995_10( 
  CONSTRAINT __t1995_10_check 
  CHECK(valid >= '1995-10-01 00:00+00'::timestamptz 
        and valid < '1995-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1995_10_station_idx on t1995_10(station);
CREATE INDEX t1995_10_valid_idx on t1995_10(valid);
GRANT SELECT on t1995_10 to nobody,apache;


create table t1995_11( 
  CONSTRAINT __t1995_11_check 
  CHECK(valid >= '1995-11-01 00:00+00'::timestamptz 
        and valid < '1995-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1995_11_station_idx on t1995_11(station);
CREATE INDEX t1995_11_valid_idx on t1995_11(valid);
GRANT SELECT on t1995_11 to nobody,apache;


create table t1995_12( 
  CONSTRAINT __t1995_12_check 
  CHECK(valid >= '1995-12-01 00:00+00'::timestamptz 
        and valid < '1996-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1995_12_station_idx on t1995_12(station);
CREATE INDEX t1995_12_valid_idx on t1995_12(valid);
GRANT SELECT on t1995_12 to nobody,apache;


create table t1996_01( 
  CONSTRAINT __t1996_01_check 
  CHECK(valid >= '1996-01-01 00:00+00'::timestamptz 
        and valid < '1996-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1996_01_station_idx on t1996_01(station);
CREATE INDEX t1996_01_valid_idx on t1996_01(valid);
GRANT SELECT on t1996_01 to nobody,apache;


create table t1996_02( 
  CONSTRAINT __t1996_02_check 
  CHECK(valid >= '1996-02-01 00:00+00'::timestamptz 
        and valid < '1996-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1996_02_station_idx on t1996_02(station);
CREATE INDEX t1996_02_valid_idx on t1996_02(valid);
GRANT SELECT on t1996_02 to nobody,apache;


create table t1996_03( 
  CONSTRAINT __t1996_03_check 
  CHECK(valid >= '1996-03-01 00:00+00'::timestamptz 
        and valid < '1996-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1996_03_station_idx on t1996_03(station);
CREATE INDEX t1996_03_valid_idx on t1996_03(valid);
GRANT SELECT on t1996_03 to nobody,apache;


create table t1996_04( 
  CONSTRAINT __t1996_04_check 
  CHECK(valid >= '1996-04-01 00:00+00'::timestamptz 
        and valid < '1996-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1996_04_station_idx on t1996_04(station);
CREATE INDEX t1996_04_valid_idx on t1996_04(valid);
GRANT SELECT on t1996_04 to nobody,apache;


create table t1996_05( 
  CONSTRAINT __t1996_05_check 
  CHECK(valid >= '1996-05-01 00:00+00'::timestamptz 
        and valid < '1996-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1996_05_station_idx on t1996_05(station);
CREATE INDEX t1996_05_valid_idx on t1996_05(valid);
GRANT SELECT on t1996_05 to nobody,apache;


create table t1996_06( 
  CONSTRAINT __t1996_06_check 
  CHECK(valid >= '1996-06-01 00:00+00'::timestamptz 
        and valid < '1996-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1996_06_station_idx on t1996_06(station);
CREATE INDEX t1996_06_valid_idx on t1996_06(valid);
GRANT SELECT on t1996_06 to nobody,apache;


create table t1996_07( 
  CONSTRAINT __t1996_07_check 
  CHECK(valid >= '1996-07-01 00:00+00'::timestamptz 
        and valid < '1996-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1996_07_station_idx on t1996_07(station);
CREATE INDEX t1996_07_valid_idx on t1996_07(valid);
GRANT SELECT on t1996_07 to nobody,apache;


create table t1996_08( 
  CONSTRAINT __t1996_08_check 
  CHECK(valid >= '1996-08-01 00:00+00'::timestamptz 
        and valid < '1996-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1996_08_station_idx on t1996_08(station);
CREATE INDEX t1996_08_valid_idx on t1996_08(valid);
GRANT SELECT on t1996_08 to nobody,apache;


create table t1996_09( 
  CONSTRAINT __t1996_09_check 
  CHECK(valid >= '1996-09-01 00:00+00'::timestamptz 
        and valid < '1996-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1996_09_station_idx on t1996_09(station);
CREATE INDEX t1996_09_valid_idx on t1996_09(valid);
GRANT SELECT on t1996_09 to nobody,apache;


create table t1996_10( 
  CONSTRAINT __t1996_10_check 
  CHECK(valid >= '1996-10-01 00:00+00'::timestamptz 
        and valid < '1996-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1996_10_station_idx on t1996_10(station);
CREATE INDEX t1996_10_valid_idx on t1996_10(valid);
GRANT SELECT on t1996_10 to nobody,apache;


create table t1996_11( 
  CONSTRAINT __t1996_11_check 
  CHECK(valid >= '1996-11-01 00:00+00'::timestamptz 
        and valid < '1996-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1996_11_station_idx on t1996_11(station);
CREATE INDEX t1996_11_valid_idx on t1996_11(valid);
GRANT SELECT on t1996_11 to nobody,apache;


create table t1996_12( 
  CONSTRAINT __t1996_12_check 
  CHECK(valid >= '1996-12-01 00:00+00'::timestamptz 
        and valid < '1997-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1996_12_station_idx on t1996_12(station);
CREATE INDEX t1996_12_valid_idx on t1996_12(valid);
GRANT SELECT on t1996_12 to nobody,apache;


create table t1997_01( 
  CONSTRAINT __t1997_01_check 
  CHECK(valid >= '1997-01-01 00:00+00'::timestamptz 
        and valid < '1997-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1997_01_station_idx on t1997_01(station);
CREATE INDEX t1997_01_valid_idx on t1997_01(valid);
GRANT SELECT on t1997_01 to nobody,apache;


create table t1997_02( 
  CONSTRAINT __t1997_02_check 
  CHECK(valid >= '1997-02-01 00:00+00'::timestamptz 
        and valid < '1997-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1997_02_station_idx on t1997_02(station);
CREATE INDEX t1997_02_valid_idx on t1997_02(valid);
GRANT SELECT on t1997_02 to nobody,apache;


create table t1997_03( 
  CONSTRAINT __t1997_03_check 
  CHECK(valid >= '1997-03-01 00:00+00'::timestamptz 
        and valid < '1997-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1997_03_station_idx on t1997_03(station);
CREATE INDEX t1997_03_valid_idx on t1997_03(valid);
GRANT SELECT on t1997_03 to nobody,apache;


create table t1997_04( 
  CONSTRAINT __t1997_04_check 
  CHECK(valid >= '1997-04-01 00:00+00'::timestamptz 
        and valid < '1997-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1997_04_station_idx on t1997_04(station);
CREATE INDEX t1997_04_valid_idx on t1997_04(valid);
GRANT SELECT on t1997_04 to nobody,apache;


create table t1997_05( 
  CONSTRAINT __t1997_05_check 
  CHECK(valid >= '1997-05-01 00:00+00'::timestamptz 
        and valid < '1997-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1997_05_station_idx on t1997_05(station);
CREATE INDEX t1997_05_valid_idx on t1997_05(valid);
GRANT SELECT on t1997_05 to nobody,apache;


create table t1997_06( 
  CONSTRAINT __t1997_06_check 
  CHECK(valid >= '1997-06-01 00:00+00'::timestamptz 
        and valid < '1997-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1997_06_station_idx on t1997_06(station);
CREATE INDEX t1997_06_valid_idx on t1997_06(valid);
GRANT SELECT on t1997_06 to nobody,apache;


create table t1997_07( 
  CONSTRAINT __t1997_07_check 
  CHECK(valid >= '1997-07-01 00:00+00'::timestamptz 
        and valid < '1997-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1997_07_station_idx on t1997_07(station);
CREATE INDEX t1997_07_valid_idx on t1997_07(valid);
GRANT SELECT on t1997_07 to nobody,apache;


create table t1997_08( 
  CONSTRAINT __t1997_08_check 
  CHECK(valid >= '1997-08-01 00:00+00'::timestamptz 
        and valid < '1997-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1997_08_station_idx on t1997_08(station);
CREATE INDEX t1997_08_valid_idx on t1997_08(valid);
GRANT SELECT on t1997_08 to nobody,apache;


create table t1997_09( 
  CONSTRAINT __t1997_09_check 
  CHECK(valid >= '1997-09-01 00:00+00'::timestamptz 
        and valid < '1997-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1997_09_station_idx on t1997_09(station);
CREATE INDEX t1997_09_valid_idx on t1997_09(valid);
GRANT SELECT on t1997_09 to nobody,apache;


create table t1997_10( 
  CONSTRAINT __t1997_10_check 
  CHECK(valid >= '1997-10-01 00:00+00'::timestamptz 
        and valid < '1997-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1997_10_station_idx on t1997_10(station);
CREATE INDEX t1997_10_valid_idx on t1997_10(valid);
GRANT SELECT on t1997_10 to nobody,apache;


create table t1997_11( 
  CONSTRAINT __t1997_11_check 
  CHECK(valid >= '1997-11-01 00:00+00'::timestamptz 
        and valid < '1997-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1997_11_station_idx on t1997_11(station);
CREATE INDEX t1997_11_valid_idx on t1997_11(valid);
GRANT SELECT on t1997_11 to nobody,apache;


create table t1997_12( 
  CONSTRAINT __t1997_12_check 
  CHECK(valid >= '1997-12-01 00:00+00'::timestamptz 
        and valid < '1998-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1997_12_station_idx on t1997_12(station);
CREATE INDEX t1997_12_valid_idx on t1997_12(valid);
GRANT SELECT on t1997_12 to nobody,apache;


create table t1998_01( 
  CONSTRAINT __t1998_01_check 
  CHECK(valid >= '1998-01-01 00:00+00'::timestamptz 
        and valid < '1998-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1998_01_station_idx on t1998_01(station);
CREATE INDEX t1998_01_valid_idx on t1998_01(valid);
GRANT SELECT on t1998_01 to nobody,apache;


create table t1998_02( 
  CONSTRAINT __t1998_02_check 
  CHECK(valid >= '1998-02-01 00:00+00'::timestamptz 
        and valid < '1998-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1998_02_station_idx on t1998_02(station);
CREATE INDEX t1998_02_valid_idx on t1998_02(valid);
GRANT SELECT on t1998_02 to nobody,apache;


create table t1998_03( 
  CONSTRAINT __t1998_03_check 
  CHECK(valid >= '1998-03-01 00:00+00'::timestamptz 
        and valid < '1998-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1998_03_station_idx on t1998_03(station);
CREATE INDEX t1998_03_valid_idx on t1998_03(valid);
GRANT SELECT on t1998_03 to nobody,apache;


create table t1998_04( 
  CONSTRAINT __t1998_04_check 
  CHECK(valid >= '1998-04-01 00:00+00'::timestamptz 
        and valid < '1998-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1998_04_station_idx on t1998_04(station);
CREATE INDEX t1998_04_valid_idx on t1998_04(valid);
GRANT SELECT on t1998_04 to nobody,apache;


create table t1998_05( 
  CONSTRAINT __t1998_05_check 
  CHECK(valid >= '1998-05-01 00:00+00'::timestamptz 
        and valid < '1998-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1998_05_station_idx on t1998_05(station);
CREATE INDEX t1998_05_valid_idx on t1998_05(valid);
GRANT SELECT on t1998_05 to nobody,apache;


create table t1998_06( 
  CONSTRAINT __t1998_06_check 
  CHECK(valid >= '1998-06-01 00:00+00'::timestamptz 
        and valid < '1998-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1998_06_station_idx on t1998_06(station);
CREATE INDEX t1998_06_valid_idx on t1998_06(valid);
GRANT SELECT on t1998_06 to nobody,apache;


create table t1998_07( 
  CONSTRAINT __t1998_07_check 
  CHECK(valid >= '1998-07-01 00:00+00'::timestamptz 
        and valid < '1998-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1998_07_station_idx on t1998_07(station);
CREATE INDEX t1998_07_valid_idx on t1998_07(valid);
GRANT SELECT on t1998_07 to nobody,apache;


create table t1998_08( 
  CONSTRAINT __t1998_08_check 
  CHECK(valid >= '1998-08-01 00:00+00'::timestamptz 
        and valid < '1998-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1998_08_station_idx on t1998_08(station);
CREATE INDEX t1998_08_valid_idx on t1998_08(valid);
GRANT SELECT on t1998_08 to nobody,apache;


create table t1998_09( 
  CONSTRAINT __t1998_09_check 
  CHECK(valid >= '1998-09-01 00:00+00'::timestamptz 
        and valid < '1998-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1998_09_station_idx on t1998_09(station);
CREATE INDEX t1998_09_valid_idx on t1998_09(valid);
GRANT SELECT on t1998_09 to nobody,apache;


create table t1998_10( 
  CONSTRAINT __t1998_10_check 
  CHECK(valid >= '1998-10-01 00:00+00'::timestamptz 
        and valid < '1998-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1998_10_station_idx on t1998_10(station);
CREATE INDEX t1998_10_valid_idx on t1998_10(valid);
GRANT SELECT on t1998_10 to nobody,apache;


create table t1998_11( 
  CONSTRAINT __t1998_11_check 
  CHECK(valid >= '1998-11-01 00:00+00'::timestamptz 
        and valid < '1998-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1998_11_station_idx on t1998_11(station);
CREATE INDEX t1998_11_valid_idx on t1998_11(valid);
GRANT SELECT on t1998_11 to nobody,apache;


create table t1998_12( 
  CONSTRAINT __t1998_12_check 
  CHECK(valid >= '1998-12-01 00:00+00'::timestamptz 
        and valid < '1999-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1998_12_station_idx on t1998_12(station);
CREATE INDEX t1998_12_valid_idx on t1998_12(valid);
GRANT SELECT on t1998_12 to nobody,apache;


create table t1999_01( 
  CONSTRAINT __t1999_01_check 
  CHECK(valid >= '1999-01-01 00:00+00'::timestamptz 
        and valid < '1999-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1999_01_station_idx on t1999_01(station);
CREATE INDEX t1999_01_valid_idx on t1999_01(valid);
GRANT SELECT on t1999_01 to nobody,apache;


create table t1999_02( 
  CONSTRAINT __t1999_02_check 
  CHECK(valid >= '1999-02-01 00:00+00'::timestamptz 
        and valid < '1999-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1999_02_station_idx on t1999_02(station);
CREATE INDEX t1999_02_valid_idx on t1999_02(valid);
GRANT SELECT on t1999_02 to nobody,apache;


create table t1999_03( 
  CONSTRAINT __t1999_03_check 
  CHECK(valid >= '1999-03-01 00:00+00'::timestamptz 
        and valid < '1999-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1999_03_station_idx on t1999_03(station);
CREATE INDEX t1999_03_valid_idx on t1999_03(valid);
GRANT SELECT on t1999_03 to nobody,apache;


create table t1999_04( 
  CONSTRAINT __t1999_04_check 
  CHECK(valid >= '1999-04-01 00:00+00'::timestamptz 
        and valid < '1999-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1999_04_station_idx on t1999_04(station);
CREATE INDEX t1999_04_valid_idx on t1999_04(valid);
GRANT SELECT on t1999_04 to nobody,apache;


create table t1999_05( 
  CONSTRAINT __t1999_05_check 
  CHECK(valid >= '1999-05-01 00:00+00'::timestamptz 
        and valid < '1999-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1999_05_station_idx on t1999_05(station);
CREATE INDEX t1999_05_valid_idx on t1999_05(valid);
GRANT SELECT on t1999_05 to nobody,apache;


create table t1999_06( 
  CONSTRAINT __t1999_06_check 
  CHECK(valid >= '1999-06-01 00:00+00'::timestamptz 
        and valid < '1999-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1999_06_station_idx on t1999_06(station);
CREATE INDEX t1999_06_valid_idx on t1999_06(valid);
GRANT SELECT on t1999_06 to nobody,apache;


create table t1999_07( 
  CONSTRAINT __t1999_07_check 
  CHECK(valid >= '1999-07-01 00:00+00'::timestamptz 
        and valid < '1999-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1999_07_station_idx on t1999_07(station);
CREATE INDEX t1999_07_valid_idx on t1999_07(valid);
GRANT SELECT on t1999_07 to nobody,apache;


create table t1999_08( 
  CONSTRAINT __t1999_08_check 
  CHECK(valid >= '1999-08-01 00:00+00'::timestamptz 
        and valid < '1999-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1999_08_station_idx on t1999_08(station);
CREATE INDEX t1999_08_valid_idx on t1999_08(valid);
GRANT SELECT on t1999_08 to nobody,apache;


create table t1999_09( 
  CONSTRAINT __t1999_09_check 
  CHECK(valid >= '1999-09-01 00:00+00'::timestamptz 
        and valid < '1999-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1999_09_station_idx on t1999_09(station);
CREATE INDEX t1999_09_valid_idx on t1999_09(valid);
GRANT SELECT on t1999_09 to nobody,apache;


create table t1999_10( 
  CONSTRAINT __t1999_10_check 
  CHECK(valid >= '1999-10-01 00:00+00'::timestamptz 
        and valid < '1999-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1999_10_station_idx on t1999_10(station);
CREATE INDEX t1999_10_valid_idx on t1999_10(valid);
GRANT SELECT on t1999_10 to nobody,apache;


create table t1999_11( 
  CONSTRAINT __t1999_11_check 
  CHECK(valid >= '1999-11-01 00:00+00'::timestamptz 
        and valid < '1999-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1999_11_station_idx on t1999_11(station);
CREATE INDEX t1999_11_valid_idx on t1999_11(valid);
GRANT SELECT on t1999_11 to nobody,apache;


create table t1999_12( 
  CONSTRAINT __t1999_12_check 
  CHECK(valid >= '1999-12-01 00:00+00'::timestamptz 
        and valid < '2000-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t1999_12_station_idx on t1999_12(station);
CREATE INDEX t1999_12_valid_idx on t1999_12(valid);
GRANT SELECT on t1999_12 to nobody,apache;


create table t2000_01( 
  CONSTRAINT __t2000_01_check 
  CHECK(valid >= '2000-01-01 00:00+00'::timestamptz 
        and valid < '2000-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_01_station_idx on t2000_01(station);
CREATE INDEX t2000_01_valid_idx on t2000_01(valid);
GRANT SELECT on t2000_01 to nobody,apache;


create table t2000_02( 
  CONSTRAINT __t2000_02_check 
  CHECK(valid >= '2000-02-01 00:00+00'::timestamptz 
        and valid < '2000-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_02_station_idx on t2000_02(station);
CREATE INDEX t2000_02_valid_idx on t2000_02(valid);
GRANT SELECT on t2000_02 to nobody,apache;


create table t2000_03( 
  CONSTRAINT __t2000_03_check 
  CHECK(valid >= '2000-03-01 00:00+00'::timestamptz 
        and valid < '2000-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_03_station_idx on t2000_03(station);
CREATE INDEX t2000_03_valid_idx on t2000_03(valid);
GRANT SELECT on t2000_03 to nobody,apache;


create table t2000_04( 
  CONSTRAINT __t2000_04_check 
  CHECK(valid >= '2000-04-01 00:00+00'::timestamptz 
        and valid < '2000-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_04_station_idx on t2000_04(station);
CREATE INDEX t2000_04_valid_idx on t2000_04(valid);
GRANT SELECT on t2000_04 to nobody,apache;


create table t2000_05( 
  CONSTRAINT __t2000_05_check 
  CHECK(valid >= '2000-05-01 00:00+00'::timestamptz 
        and valid < '2000-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_05_station_idx on t2000_05(station);
CREATE INDEX t2000_05_valid_idx on t2000_05(valid);
GRANT SELECT on t2000_05 to nobody,apache;


create table t2000_06( 
  CONSTRAINT __t2000_06_check 
  CHECK(valid >= '2000-06-01 00:00+00'::timestamptz 
        and valid < '2000-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_06_station_idx on t2000_06(station);
CREATE INDEX t2000_06_valid_idx on t2000_06(valid);
GRANT SELECT on t2000_06 to nobody,apache;


create table t2000_07( 
  CONSTRAINT __t2000_07_check 
  CHECK(valid >= '2000-07-01 00:00+00'::timestamptz 
        and valid < '2000-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_07_station_idx on t2000_07(station);
CREATE INDEX t2000_07_valid_idx on t2000_07(valid);
GRANT SELECT on t2000_07 to nobody,apache;


create table t2000_08( 
  CONSTRAINT __t2000_08_check 
  CHECK(valid >= '2000-08-01 00:00+00'::timestamptz 
        and valid < '2000-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_08_station_idx on t2000_08(station);
CREATE INDEX t2000_08_valid_idx on t2000_08(valid);
GRANT SELECT on t2000_08 to nobody,apache;


create table t2000_09( 
  CONSTRAINT __t2000_09_check 
  CHECK(valid >= '2000-09-01 00:00+00'::timestamptz 
        and valid < '2000-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_09_station_idx on t2000_09(station);
CREATE INDEX t2000_09_valid_idx on t2000_09(valid);
GRANT SELECT on t2000_09 to nobody,apache;


create table t2000_10( 
  CONSTRAINT __t2000_10_check 
  CHECK(valid >= '2000-10-01 00:00+00'::timestamptz 
        and valid < '2000-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_10_station_idx on t2000_10(station);
CREATE INDEX t2000_10_valid_idx on t2000_10(valid);
GRANT SELECT on t2000_10 to nobody,apache;


create table t2000_11( 
  CONSTRAINT __t2000_11_check 
  CHECK(valid >= '2000-11-01 00:00+00'::timestamptz 
        and valid < '2000-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_11_station_idx on t2000_11(station);
CREATE INDEX t2000_11_valid_idx on t2000_11(valid);
GRANT SELECT on t2000_11 to nobody,apache;


create table t2000_12( 
  CONSTRAINT __t2000_12_check 
  CHECK(valid >= '2000-12-01 00:00+00'::timestamptz 
        and valid < '2001-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2000_12_station_idx on t2000_12(station);
CREATE INDEX t2000_12_valid_idx on t2000_12(valid);
GRANT SELECT on t2000_12 to nobody,apache;


create table t2001_01( 
  CONSTRAINT __t2001_01_check 
  CHECK(valid >= '2001-01-01 00:00+00'::timestamptz 
        and valid < '2001-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_01_station_idx on t2001_01(station);
CREATE INDEX t2001_01_valid_idx on t2001_01(valid);
GRANT SELECT on t2001_01 to nobody,apache;


create table t2001_02( 
  CONSTRAINT __t2001_02_check 
  CHECK(valid >= '2001-02-01 00:00+00'::timestamptz 
        and valid < '2001-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_02_station_idx on t2001_02(station);
CREATE INDEX t2001_02_valid_idx on t2001_02(valid);
GRANT SELECT on t2001_02 to nobody,apache;


create table t2001_03( 
  CONSTRAINT __t2001_03_check 
  CHECK(valid >= '2001-03-01 00:00+00'::timestamptz 
        and valid < '2001-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_03_station_idx on t2001_03(station);
CREATE INDEX t2001_03_valid_idx on t2001_03(valid);
GRANT SELECT on t2001_03 to nobody,apache;


create table t2001_04( 
  CONSTRAINT __t2001_04_check 
  CHECK(valid >= '2001-04-01 00:00+00'::timestamptz 
        and valid < '2001-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_04_station_idx on t2001_04(station);
CREATE INDEX t2001_04_valid_idx on t2001_04(valid);
GRANT SELECT on t2001_04 to nobody,apache;


create table t2001_05( 
  CONSTRAINT __t2001_05_check 
  CHECK(valid >= '2001-05-01 00:00+00'::timestamptz 
        and valid < '2001-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_05_station_idx on t2001_05(station);
CREATE INDEX t2001_05_valid_idx on t2001_05(valid);
GRANT SELECT on t2001_05 to nobody,apache;


create table t2001_06( 
  CONSTRAINT __t2001_06_check 
  CHECK(valid >= '2001-06-01 00:00+00'::timestamptz 
        and valid < '2001-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_06_station_idx on t2001_06(station);
CREATE INDEX t2001_06_valid_idx on t2001_06(valid);
GRANT SELECT on t2001_06 to nobody,apache;


create table t2001_07( 
  CONSTRAINT __t2001_07_check 
  CHECK(valid >= '2001-07-01 00:00+00'::timestamptz 
        and valid < '2001-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_07_station_idx on t2001_07(station);
CREATE INDEX t2001_07_valid_idx on t2001_07(valid);
GRANT SELECT on t2001_07 to nobody,apache;


create table t2001_08( 
  CONSTRAINT __t2001_08_check 
  CHECK(valid >= '2001-08-01 00:00+00'::timestamptz 
        and valid < '2001-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_08_station_idx on t2001_08(station);
CREATE INDEX t2001_08_valid_idx on t2001_08(valid);
GRANT SELECT on t2001_08 to nobody,apache;


create table t2001_09( 
  CONSTRAINT __t2001_09_check 
  CHECK(valid >= '2001-09-01 00:00+00'::timestamptz 
        and valid < '2001-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_09_station_idx on t2001_09(station);
CREATE INDEX t2001_09_valid_idx on t2001_09(valid);
GRANT SELECT on t2001_09 to nobody,apache;


create table t2001_10( 
  CONSTRAINT __t2001_10_check 
  CHECK(valid >= '2001-10-01 00:00+00'::timestamptz 
        and valid < '2001-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_10_station_idx on t2001_10(station);
CREATE INDEX t2001_10_valid_idx on t2001_10(valid);
GRANT SELECT on t2001_10 to nobody,apache;


create table t2001_11( 
  CONSTRAINT __t2001_11_check 
  CHECK(valid >= '2001-11-01 00:00+00'::timestamptz 
        and valid < '2001-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_11_station_idx on t2001_11(station);
CREATE INDEX t2001_11_valid_idx on t2001_11(valid);
GRANT SELECT on t2001_11 to nobody,apache;


create table t2001_12( 
  CONSTRAINT __t2001_12_check 
  CHECK(valid >= '2001-12-01 00:00+00'::timestamptz 
        and valid < '2002-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2001_12_station_idx on t2001_12(station);
CREATE INDEX t2001_12_valid_idx on t2001_12(valid);
GRANT SELECT on t2001_12 to nobody,apache;


create table t2002_01( 
  CONSTRAINT __t2002_01_check 
  CHECK(valid >= '2002-01-01 00:00+00'::timestamptz 
        and valid < '2002-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_01_station_idx on t2002_01(station);
CREATE INDEX t2002_01_valid_idx on t2002_01(valid);
GRANT SELECT on t2002_01 to nobody,apache;


create table t2002_02( 
  CONSTRAINT __t2002_02_check 
  CHECK(valid >= '2002-02-01 00:00+00'::timestamptz 
        and valid < '2002-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_02_station_idx on t2002_02(station);
CREATE INDEX t2002_02_valid_idx on t2002_02(valid);
GRANT SELECT on t2002_02 to nobody,apache;


create table t2002_03( 
  CONSTRAINT __t2002_03_check 
  CHECK(valid >= '2002-03-01 00:00+00'::timestamptz 
        and valid < '2002-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_03_station_idx on t2002_03(station);
CREATE INDEX t2002_03_valid_idx on t2002_03(valid);
GRANT SELECT on t2002_03 to nobody,apache;


create table t2002_04( 
  CONSTRAINT __t2002_04_check 
  CHECK(valid >= '2002-04-01 00:00+00'::timestamptz 
        and valid < '2002-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_04_station_idx on t2002_04(station);
CREATE INDEX t2002_04_valid_idx on t2002_04(valid);
GRANT SELECT on t2002_04 to nobody,apache;


create table t2002_05( 
  CONSTRAINT __t2002_05_check 
  CHECK(valid >= '2002-05-01 00:00+00'::timestamptz 
        and valid < '2002-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_05_station_idx on t2002_05(station);
CREATE INDEX t2002_05_valid_idx on t2002_05(valid);
GRANT SELECT on t2002_05 to nobody,apache;


create table t2002_06( 
  CONSTRAINT __t2002_06_check 
  CHECK(valid >= '2002-06-01 00:00+00'::timestamptz 
        and valid < '2002-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_06_station_idx on t2002_06(station);
CREATE INDEX t2002_06_valid_idx on t2002_06(valid);
GRANT SELECT on t2002_06 to nobody,apache;


create table t2002_07( 
  CONSTRAINT __t2002_07_check 
  CHECK(valid >= '2002-07-01 00:00+00'::timestamptz 
        and valid < '2002-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_07_station_idx on t2002_07(station);
CREATE INDEX t2002_07_valid_idx on t2002_07(valid);
GRANT SELECT on t2002_07 to nobody,apache;


create table t2002_08( 
  CONSTRAINT __t2002_08_check 
  CHECK(valid >= '2002-08-01 00:00+00'::timestamptz 
        and valid < '2002-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_08_station_idx on t2002_08(station);
CREATE INDEX t2002_08_valid_idx on t2002_08(valid);
GRANT SELECT on t2002_08 to nobody,apache;


create table t2002_09( 
  CONSTRAINT __t2002_09_check 
  CHECK(valid >= '2002-09-01 00:00+00'::timestamptz 
        and valid < '2002-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_09_station_idx on t2002_09(station);
CREATE INDEX t2002_09_valid_idx on t2002_09(valid);
GRANT SELECT on t2002_09 to nobody,apache;


create table t2002_10( 
  CONSTRAINT __t2002_10_check 
  CHECK(valid >= '2002-10-01 00:00+00'::timestamptz 
        and valid < '2002-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_10_station_idx on t2002_10(station);
CREATE INDEX t2002_10_valid_idx on t2002_10(valid);
GRANT SELECT on t2002_10 to nobody,apache;


create table t2002_11( 
  CONSTRAINT __t2002_11_check 
  CHECK(valid >= '2002-11-01 00:00+00'::timestamptz 
        and valid < '2002-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_11_station_idx on t2002_11(station);
CREATE INDEX t2002_11_valid_idx on t2002_11(valid);
GRANT SELECT on t2002_11 to nobody,apache;


create table t2002_12( 
  CONSTRAINT __t2002_12_check 
  CHECK(valid >= '2002-12-01 00:00+00'::timestamptz 
        and valid < '2003-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_12_station_idx on t2002_12(station);
CREATE INDEX t2002_12_valid_idx on t2002_12(valid);
GRANT SELECT on t2002_12 to nobody,apache;


create table t2003_01( 
  CONSTRAINT __t2003_01_check 
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz 
        and valid < '2003-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_01_station_idx on t2003_01(station);
CREATE INDEX t2003_01_valid_idx on t2003_01(valid);
GRANT SELECT on t2003_01 to nobody,apache;


create table t2003_02( 
  CONSTRAINT __t2003_02_check 
  CHECK(valid >= '2003-02-01 00:00+00'::timestamptz 
        and valid < '2003-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_02_station_idx on t2003_02(station);
CREATE INDEX t2003_02_valid_idx on t2003_02(valid);
GRANT SELECT on t2003_02 to nobody,apache;


create table t2003_03( 
  CONSTRAINT __t2003_03_check 
  CHECK(valid >= '2003-03-01 00:00+00'::timestamptz 
        and valid < '2003-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_03_station_idx on t2003_03(station);
CREATE INDEX t2003_03_valid_idx on t2003_03(valid);
GRANT SELECT on t2003_03 to nobody,apache;


create table t2003_04( 
  CONSTRAINT __t2003_04_check 
  CHECK(valid >= '2003-04-01 00:00+00'::timestamptz 
        and valid < '2003-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_04_station_idx on t2003_04(station);
CREATE INDEX t2003_04_valid_idx on t2003_04(valid);
GRANT SELECT on t2003_04 to nobody,apache;


create table t2003_05( 
  CONSTRAINT __t2003_05_check 
  CHECK(valid >= '2003-05-01 00:00+00'::timestamptz 
        and valid < '2003-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_05_station_idx on t2003_05(station);
CREATE INDEX t2003_05_valid_idx on t2003_05(valid);
GRANT SELECT on t2003_05 to nobody,apache;


create table t2003_06( 
  CONSTRAINT __t2003_06_check 
  CHECK(valid >= '2003-06-01 00:00+00'::timestamptz 
        and valid < '2003-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_06_station_idx on t2003_06(station);
CREATE INDEX t2003_06_valid_idx on t2003_06(valid);
GRANT SELECT on t2003_06 to nobody,apache;


create table t2003_07( 
  CONSTRAINT __t2003_07_check 
  CHECK(valid >= '2003-07-01 00:00+00'::timestamptz 
        and valid < '2003-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_07_station_idx on t2003_07(station);
CREATE INDEX t2003_07_valid_idx on t2003_07(valid);
GRANT SELECT on t2003_07 to nobody,apache;


create table t2003_08( 
  CONSTRAINT __t2003_08_check 
  CHECK(valid >= '2003-08-01 00:00+00'::timestamptz 
        and valid < '2003-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_08_station_idx on t2003_08(station);
CREATE INDEX t2003_08_valid_idx on t2003_08(valid);
GRANT SELECT on t2003_08 to nobody,apache;


create table t2003_09( 
  CONSTRAINT __t2003_09_check 
  CHECK(valid >= '2003-09-01 00:00+00'::timestamptz 
        and valid < '2003-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_09_station_idx on t2003_09(station);
CREATE INDEX t2003_09_valid_idx on t2003_09(valid);
GRANT SELECT on t2003_09 to nobody,apache;


create table t2003_10( 
  CONSTRAINT __t2003_10_check 
  CHECK(valid >= '2003-10-01 00:00+00'::timestamptz 
        and valid < '2003-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_10_station_idx on t2003_10(station);
CREATE INDEX t2003_10_valid_idx on t2003_10(valid);
GRANT SELECT on t2003_10 to nobody,apache;


create table t2003_11( 
  CONSTRAINT __t2003_11_check 
  CHECK(valid >= '2003-11-01 00:00+00'::timestamptz 
        and valid < '2003-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_11_station_idx on t2003_11(station);
CREATE INDEX t2003_11_valid_idx on t2003_11(valid);
GRANT SELECT on t2003_11 to nobody,apache;


create table t2003_12( 
  CONSTRAINT __t2003_12_check 
  CHECK(valid >= '2003-12-01 00:00+00'::timestamptz 
        and valid < '2004-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_12_station_idx on t2003_12(station);
CREATE INDEX t2003_12_valid_idx on t2003_12(valid);
GRANT SELECT on t2003_12 to nobody,apache;


create table t2004_01( 
  CONSTRAINT __t2004_01_check 
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz 
        and valid < '2004-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_01_station_idx on t2004_01(station);
CREATE INDEX t2004_01_valid_idx on t2004_01(valid);
GRANT SELECT on t2004_01 to nobody,apache;


create table t2004_02( 
  CONSTRAINT __t2004_02_check 
  CHECK(valid >= '2004-02-01 00:00+00'::timestamptz 
        and valid < '2004-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_02_station_idx on t2004_02(station);
CREATE INDEX t2004_02_valid_idx on t2004_02(valid);
GRANT SELECT on t2004_02 to nobody,apache;


create table t2004_03( 
  CONSTRAINT __t2004_03_check 
  CHECK(valid >= '2004-03-01 00:00+00'::timestamptz 
        and valid < '2004-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_03_station_idx on t2004_03(station);
CREATE INDEX t2004_03_valid_idx on t2004_03(valid);
GRANT SELECT on t2004_03 to nobody,apache;


create table t2004_04( 
  CONSTRAINT __t2004_04_check 
  CHECK(valid >= '2004-04-01 00:00+00'::timestamptz 
        and valid < '2004-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_04_station_idx on t2004_04(station);
CREATE INDEX t2004_04_valid_idx on t2004_04(valid);
GRANT SELECT on t2004_04 to nobody,apache;


create table t2004_05( 
  CONSTRAINT __t2004_05_check 
  CHECK(valid >= '2004-05-01 00:00+00'::timestamptz 
        and valid < '2004-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_05_station_idx on t2004_05(station);
CREATE INDEX t2004_05_valid_idx on t2004_05(valid);
GRANT SELECT on t2004_05 to nobody,apache;


create table t2004_06( 
  CONSTRAINT __t2004_06_check 
  CHECK(valid >= '2004-06-01 00:00+00'::timestamptz 
        and valid < '2004-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_06_station_idx on t2004_06(station);
CREATE INDEX t2004_06_valid_idx on t2004_06(valid);
GRANT SELECT on t2004_06 to nobody,apache;


create table t2004_07( 
  CONSTRAINT __t2004_07_check 
  CHECK(valid >= '2004-07-01 00:00+00'::timestamptz 
        and valid < '2004-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_07_station_idx on t2004_07(station);
CREATE INDEX t2004_07_valid_idx on t2004_07(valid);
GRANT SELECT on t2004_07 to nobody,apache;


create table t2004_08( 
  CONSTRAINT __t2004_08_check 
  CHECK(valid >= '2004-08-01 00:00+00'::timestamptz 
        and valid < '2004-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_08_station_idx on t2004_08(station);
CREATE INDEX t2004_08_valid_idx on t2004_08(valid);
GRANT SELECT on t2004_08 to nobody,apache;


create table t2004_09( 
  CONSTRAINT __t2004_09_check 
  CHECK(valid >= '2004-09-01 00:00+00'::timestamptz 
        and valid < '2004-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_09_station_idx on t2004_09(station);
CREATE INDEX t2004_09_valid_idx on t2004_09(valid);
GRANT SELECT on t2004_09 to nobody,apache;


create table t2004_10( 
  CONSTRAINT __t2004_10_check 
  CHECK(valid >= '2004-10-01 00:00+00'::timestamptz 
        and valid < '2004-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_10_station_idx on t2004_10(station);
CREATE INDEX t2004_10_valid_idx on t2004_10(valid);
GRANT SELECT on t2004_10 to nobody,apache;


create table t2004_11( 
  CONSTRAINT __t2004_11_check 
  CHECK(valid >= '2004-11-01 00:00+00'::timestamptz 
        and valid < '2004-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_11_station_idx on t2004_11(station);
CREATE INDEX t2004_11_valid_idx on t2004_11(valid);
GRANT SELECT on t2004_11 to nobody,apache;


create table t2004_12( 
  CONSTRAINT __t2004_12_check 
  CHECK(valid >= '2004-12-01 00:00+00'::timestamptz 
        and valid < '2005-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_12_station_idx on t2004_12(station);
CREATE INDEX t2004_12_valid_idx on t2004_12(valid);
GRANT SELECT on t2004_12 to nobody,apache;


create table t2005_01( 
  CONSTRAINT __t2005_01_check 
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz 
        and valid < '2005-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_01_station_idx on t2005_01(station);
CREATE INDEX t2005_01_valid_idx on t2005_01(valid);
GRANT SELECT on t2005_01 to nobody,apache;


create table t2005_02( 
  CONSTRAINT __t2005_02_check 
  CHECK(valid >= '2005-02-01 00:00+00'::timestamptz 
        and valid < '2005-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_02_station_idx on t2005_02(station);
CREATE INDEX t2005_02_valid_idx on t2005_02(valid);
GRANT SELECT on t2005_02 to nobody,apache;


create table t2005_03( 
  CONSTRAINT __t2005_03_check 
  CHECK(valid >= '2005-03-01 00:00+00'::timestamptz 
        and valid < '2005-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_03_station_idx on t2005_03(station);
CREATE INDEX t2005_03_valid_idx on t2005_03(valid);
GRANT SELECT on t2005_03 to nobody,apache;


create table t2005_04( 
  CONSTRAINT __t2005_04_check 
  CHECK(valid >= '2005-04-01 00:00+00'::timestamptz 
        and valid < '2005-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_04_station_idx on t2005_04(station);
CREATE INDEX t2005_04_valid_idx on t2005_04(valid);
GRANT SELECT on t2005_04 to nobody,apache;


create table t2005_05( 
  CONSTRAINT __t2005_05_check 
  CHECK(valid >= '2005-05-01 00:00+00'::timestamptz 
        and valid < '2005-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_05_station_idx on t2005_05(station);
CREATE INDEX t2005_05_valid_idx on t2005_05(valid);
GRANT SELECT on t2005_05 to nobody,apache;


create table t2005_06( 
  CONSTRAINT __t2005_06_check 
  CHECK(valid >= '2005-06-01 00:00+00'::timestamptz 
        and valid < '2005-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_06_station_idx on t2005_06(station);
CREATE INDEX t2005_06_valid_idx on t2005_06(valid);
GRANT SELECT on t2005_06 to nobody,apache;


create table t2005_07( 
  CONSTRAINT __t2005_07_check 
  CHECK(valid >= '2005-07-01 00:00+00'::timestamptz 
        and valid < '2005-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_07_station_idx on t2005_07(station);
CREATE INDEX t2005_07_valid_idx on t2005_07(valid);
GRANT SELECT on t2005_07 to nobody,apache;


create table t2005_08( 
  CONSTRAINT __t2005_08_check 
  CHECK(valid >= '2005-08-01 00:00+00'::timestamptz 
        and valid < '2005-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_08_station_idx on t2005_08(station);
CREATE INDEX t2005_08_valid_idx on t2005_08(valid);
GRANT SELECT on t2005_08 to nobody,apache;


create table t2005_09( 
  CONSTRAINT __t2005_09_check 
  CHECK(valid >= '2005-09-01 00:00+00'::timestamptz 
        and valid < '2005-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_09_station_idx on t2005_09(station);
CREATE INDEX t2005_09_valid_idx on t2005_09(valid);
GRANT SELECT on t2005_09 to nobody,apache;


create table t2005_10( 
  CONSTRAINT __t2005_10_check 
  CHECK(valid >= '2005-10-01 00:00+00'::timestamptz 
        and valid < '2005-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_10_station_idx on t2005_10(station);
CREATE INDEX t2005_10_valid_idx on t2005_10(valid);
GRANT SELECT on t2005_10 to nobody,apache;


create table t2005_11( 
  CONSTRAINT __t2005_11_check 
  CHECK(valid >= '2005-11-01 00:00+00'::timestamptz 
        and valid < '2005-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_11_station_idx on t2005_11(station);
CREATE INDEX t2005_11_valid_idx on t2005_11(valid);
GRANT SELECT on t2005_11 to nobody,apache;


create table t2005_12( 
  CONSTRAINT __t2005_12_check 
  CHECK(valid >= '2005-12-01 00:00+00'::timestamptz 
        and valid < '2006-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_12_station_idx on t2005_12(station);
CREATE INDEX t2005_12_valid_idx on t2005_12(valid);
GRANT SELECT on t2005_12 to nobody,apache;


create table t2006_01( 
  CONSTRAINT __t2006_01_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz 
        and valid < '2006-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_01_station_idx on t2006_01(station);
CREATE INDEX t2006_01_valid_idx on t2006_01(valid);
GRANT SELECT on t2006_01 to nobody,apache;


create table t2006_02( 
  CONSTRAINT __t2006_02_check 
  CHECK(valid >= '2006-02-01 00:00+00'::timestamptz 
        and valid < '2006-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_02_station_idx on t2006_02(station);
CREATE INDEX t2006_02_valid_idx on t2006_02(valid);
GRANT SELECT on t2006_02 to nobody,apache;


create table t2006_03( 
  CONSTRAINT __t2006_03_check 
  CHECK(valid >= '2006-03-01 00:00+00'::timestamptz 
        and valid < '2006-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_03_station_idx on t2006_03(station);
CREATE INDEX t2006_03_valid_idx on t2006_03(valid);
GRANT SELECT on t2006_03 to nobody,apache;


create table t2006_04( 
  CONSTRAINT __t2006_04_check 
  CHECK(valid >= '2006-04-01 00:00+00'::timestamptz 
        and valid < '2006-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_04_station_idx on t2006_04(station);
CREATE INDEX t2006_04_valid_idx on t2006_04(valid);
GRANT SELECT on t2006_04 to nobody,apache;


create table t2006_05( 
  CONSTRAINT __t2006_05_check 
  CHECK(valid >= '2006-05-01 00:00+00'::timestamptz 
        and valid < '2006-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_05_station_idx on t2006_05(station);
CREATE INDEX t2006_05_valid_idx on t2006_05(valid);
GRANT SELECT on t2006_05 to nobody,apache;


create table t2006_06( 
  CONSTRAINT __t2006_06_check 
  CHECK(valid >= '2006-06-01 00:00+00'::timestamptz 
        and valid < '2006-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_06_station_idx on t2006_06(station);
CREATE INDEX t2006_06_valid_idx on t2006_06(valid);
GRANT SELECT on t2006_06 to nobody,apache;


create table t2006_07( 
  CONSTRAINT __t2006_07_check 
  CHECK(valid >= '2006-07-01 00:00+00'::timestamptz 
        and valid < '2006-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_07_station_idx on t2006_07(station);
CREATE INDEX t2006_07_valid_idx on t2006_07(valid);
GRANT SELECT on t2006_07 to nobody,apache;


create table t2006_08( 
  CONSTRAINT __t2006_08_check 
  CHECK(valid >= '2006-08-01 00:00+00'::timestamptz 
        and valid < '2006-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_08_station_idx on t2006_08(station);
CREATE INDEX t2006_08_valid_idx on t2006_08(valid);
GRANT SELECT on t2006_08 to nobody,apache;


create table t2006_09( 
  CONSTRAINT __t2006_09_check 
  CHECK(valid >= '2006-09-01 00:00+00'::timestamptz 
        and valid < '2006-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_09_station_idx on t2006_09(station);
CREATE INDEX t2006_09_valid_idx on t2006_09(valid);
GRANT SELECT on t2006_09 to nobody,apache;


create table t2006_10( 
  CONSTRAINT __t2006_10_check 
  CHECK(valid >= '2006-10-01 00:00+00'::timestamptz 
        and valid < '2006-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_10_station_idx on t2006_10(station);
CREATE INDEX t2006_10_valid_idx on t2006_10(valid);
GRANT SELECT on t2006_10 to nobody,apache;


create table t2006_11( 
  CONSTRAINT __t2006_11_check 
  CHECK(valid >= '2006-11-01 00:00+00'::timestamptz 
        and valid < '2006-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_11_station_idx on t2006_11(station);
CREATE INDEX t2006_11_valid_idx on t2006_11(valid);
GRANT SELECT on t2006_11 to nobody,apache;


create table t2006_12( 
  CONSTRAINT __t2006_12_check 
  CHECK(valid >= '2006-12-01 00:00+00'::timestamptz 
        and valid < '2007-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_12_station_idx on t2006_12(station);
CREATE INDEX t2006_12_valid_idx on t2006_12(valid);
GRANT SELECT on t2006_12 to nobody,apache;


create table t2007_01( 
  CONSTRAINT __t2007_01_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz 
        and valid < '2007-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_01_station_idx on t2007_01(station);
CREATE INDEX t2007_01_valid_idx on t2007_01(valid);
GRANT SELECT on t2007_01 to nobody,apache;


create table t2007_02( 
  CONSTRAINT __t2007_02_check 
  CHECK(valid >= '2007-02-01 00:00+00'::timestamptz 
        and valid < '2007-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_02_station_idx on t2007_02(station);
CREATE INDEX t2007_02_valid_idx on t2007_02(valid);
GRANT SELECT on t2007_02 to nobody,apache;


create table t2007_03( 
  CONSTRAINT __t2007_03_check 
  CHECK(valid >= '2007-03-01 00:00+00'::timestamptz 
        and valid < '2007-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_03_station_idx on t2007_03(station);
CREATE INDEX t2007_03_valid_idx on t2007_03(valid);
GRANT SELECT on t2007_03 to nobody,apache;


create table t2007_04( 
  CONSTRAINT __t2007_04_check 
  CHECK(valid >= '2007-04-01 00:00+00'::timestamptz 
        and valid < '2007-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_04_station_idx on t2007_04(station);
CREATE INDEX t2007_04_valid_idx on t2007_04(valid);
GRANT SELECT on t2007_04 to nobody,apache;


create table t2007_05( 
  CONSTRAINT __t2007_05_check 
  CHECK(valid >= '2007-05-01 00:00+00'::timestamptz 
        and valid < '2007-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_05_station_idx on t2007_05(station);
CREATE INDEX t2007_05_valid_idx on t2007_05(valid);
GRANT SELECT on t2007_05 to nobody,apache;


create table t2007_06( 
  CONSTRAINT __t2007_06_check 
  CHECK(valid >= '2007-06-01 00:00+00'::timestamptz 
        and valid < '2007-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_06_station_idx on t2007_06(station);
CREATE INDEX t2007_06_valid_idx on t2007_06(valid);
GRANT SELECT on t2007_06 to nobody,apache;


create table t2007_07( 
  CONSTRAINT __t2007_07_check 
  CHECK(valid >= '2007-07-01 00:00+00'::timestamptz 
        and valid < '2007-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_07_station_idx on t2007_07(station);
CREATE INDEX t2007_07_valid_idx on t2007_07(valid);
GRANT SELECT on t2007_07 to nobody,apache;


create table t2007_08( 
  CONSTRAINT __t2007_08_check 
  CHECK(valid >= '2007-08-01 00:00+00'::timestamptz 
        and valid < '2007-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_08_station_idx on t2007_08(station);
CREATE INDEX t2007_08_valid_idx on t2007_08(valid);
GRANT SELECT on t2007_08 to nobody,apache;


create table t2007_09( 
  CONSTRAINT __t2007_09_check 
  CHECK(valid >= '2007-09-01 00:00+00'::timestamptz 
        and valid < '2007-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_09_station_idx on t2007_09(station);
CREATE INDEX t2007_09_valid_idx on t2007_09(valid);
GRANT SELECT on t2007_09 to nobody,apache;


create table t2007_10( 
  CONSTRAINT __t2007_10_check 
  CHECK(valid >= '2007-10-01 00:00+00'::timestamptz 
        and valid < '2007-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_10_station_idx on t2007_10(station);
CREATE INDEX t2007_10_valid_idx on t2007_10(valid);
GRANT SELECT on t2007_10 to nobody,apache;


create table t2007_11( 
  CONSTRAINT __t2007_11_check 
  CHECK(valid >= '2007-11-01 00:00+00'::timestamptz 
        and valid < '2007-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_11_station_idx on t2007_11(station);
CREATE INDEX t2007_11_valid_idx on t2007_11(valid);
GRANT SELECT on t2007_11 to nobody,apache;


create table t2007_12( 
  CONSTRAINT __t2007_12_check 
  CHECK(valid >= '2007-12-01 00:00+00'::timestamptz 
        and valid < '2008-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_12_station_idx on t2007_12(station);
CREATE INDEX t2007_12_valid_idx on t2007_12(valid);
GRANT SELECT on t2007_12 to nobody,apache;


create table t2008_01( 
  CONSTRAINT __t2008_01_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2008-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_01_station_idx on t2008_01(station);
CREATE INDEX t2008_01_valid_idx on t2008_01(valid);
GRANT SELECT on t2008_01 to nobody,apache;


create table t2008_02( 
  CONSTRAINT __t2008_02_check 
  CHECK(valid >= '2008-02-01 00:00+00'::timestamptz 
        and valid < '2008-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_02_station_idx on t2008_02(station);
CREATE INDEX t2008_02_valid_idx on t2008_02(valid);
GRANT SELECT on t2008_02 to nobody,apache;


create table t2008_03( 
  CONSTRAINT __t2008_03_check 
  CHECK(valid >= '2008-03-01 00:00+00'::timestamptz 
        and valid < '2008-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_03_station_idx on t2008_03(station);
CREATE INDEX t2008_03_valid_idx on t2008_03(valid);
GRANT SELECT on t2008_03 to nobody,apache;


create table t2008_04( 
  CONSTRAINT __t2008_04_check 
  CHECK(valid >= '2008-04-01 00:00+00'::timestamptz 
        and valid < '2008-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_04_station_idx on t2008_04(station);
CREATE INDEX t2008_04_valid_idx on t2008_04(valid);
GRANT SELECT on t2008_04 to nobody,apache;


create table t2008_05( 
  CONSTRAINT __t2008_05_check 
  CHECK(valid >= '2008-05-01 00:00+00'::timestamptz 
        and valid < '2008-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_05_station_idx on t2008_05(station);
CREATE INDEX t2008_05_valid_idx on t2008_05(valid);
GRANT SELECT on t2008_05 to nobody,apache;


create table t2008_06( 
  CONSTRAINT __t2008_06_check 
  CHECK(valid >= '2008-06-01 00:00+00'::timestamptz 
        and valid < '2008-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_06_station_idx on t2008_06(station);
CREATE INDEX t2008_06_valid_idx on t2008_06(valid);
GRANT SELECT on t2008_06 to nobody,apache;


create table t2008_07( 
  CONSTRAINT __t2008_07_check 
  CHECK(valid >= '2008-07-01 00:00+00'::timestamptz 
        and valid < '2008-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_07_station_idx on t2008_07(station);
CREATE INDEX t2008_07_valid_idx on t2008_07(valid);
GRANT SELECT on t2008_07 to nobody,apache;


create table t2008_08( 
  CONSTRAINT __t2008_08_check 
  CHECK(valid >= '2008-08-01 00:00+00'::timestamptz 
        and valid < '2008-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_08_station_idx on t2008_08(station);
CREATE INDEX t2008_08_valid_idx on t2008_08(valid);
GRANT SELECT on t2008_08 to nobody,apache;


create table t2008_09( 
  CONSTRAINT __t2008_09_check 
  CHECK(valid >= '2008-09-01 00:00+00'::timestamptz 
        and valid < '2008-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_09_station_idx on t2008_09(station);
CREATE INDEX t2008_09_valid_idx on t2008_09(valid);
GRANT SELECT on t2008_09 to nobody,apache;


create table t2008_10( 
  CONSTRAINT __t2008_10_check 
  CHECK(valid >= '2008-10-01 00:00+00'::timestamptz 
        and valid < '2008-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_10_station_idx on t2008_10(station);
CREATE INDEX t2008_10_valid_idx on t2008_10(valid);
GRANT SELECT on t2008_10 to nobody,apache;


create table t2008_11( 
  CONSTRAINT __t2008_11_check 
  CHECK(valid >= '2008-11-01 00:00+00'::timestamptz 
        and valid < '2008-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_11_station_idx on t2008_11(station);
CREATE INDEX t2008_11_valid_idx on t2008_11(valid);
GRANT SELECT on t2008_11 to nobody,apache;


create table t2008_12( 
  CONSTRAINT __t2008_12_check 
  CHECK(valid >= '2008-12-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_12_station_idx on t2008_12(station);
CREATE INDEX t2008_12_valid_idx on t2008_12(valid);
GRANT SELECT on t2008_12 to nobody,apache;


create table t2009_01( 
  CONSTRAINT __t2009_01_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2009-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_01_station_idx on t2009_01(station);
CREATE INDEX t2009_01_valid_idx on t2009_01(valid);
GRANT SELECT on t2009_01 to nobody,apache;


create table t2009_02( 
  CONSTRAINT __t2009_02_check 
  CHECK(valid >= '2009-02-01 00:00+00'::timestamptz 
        and valid < '2009-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_02_station_idx on t2009_02(station);
CREATE INDEX t2009_02_valid_idx on t2009_02(valid);
GRANT SELECT on t2009_02 to nobody,apache;


create table t2009_03( 
  CONSTRAINT __t2009_03_check 
  CHECK(valid >= '2009-03-01 00:00+00'::timestamptz 
        and valid < '2009-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_03_station_idx on t2009_03(station);
CREATE INDEX t2009_03_valid_idx on t2009_03(valid);
GRANT SELECT on t2009_03 to nobody,apache;


create table t2009_04( 
  CONSTRAINT __t2009_04_check 
  CHECK(valid >= '2009-04-01 00:00+00'::timestamptz 
        and valid < '2009-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_04_station_idx on t2009_04(station);
CREATE INDEX t2009_04_valid_idx on t2009_04(valid);
GRANT SELECT on t2009_04 to nobody,apache;


create table t2009_05( 
  CONSTRAINT __t2009_05_check 
  CHECK(valid >= '2009-05-01 00:00+00'::timestamptz 
        and valid < '2009-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_05_station_idx on t2009_05(station);
CREATE INDEX t2009_05_valid_idx on t2009_05(valid);
GRANT SELECT on t2009_05 to nobody,apache;


create table t2009_06( 
  CONSTRAINT __t2009_06_check 
  CHECK(valid >= '2009-06-01 00:00+00'::timestamptz 
        and valid < '2009-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_06_station_idx on t2009_06(station);
CREATE INDEX t2009_06_valid_idx on t2009_06(valid);
GRANT SELECT on t2009_06 to nobody,apache;


create table t2009_07( 
  CONSTRAINT __t2009_07_check 
  CHECK(valid >= '2009-07-01 00:00+00'::timestamptz 
        and valid < '2009-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_07_station_idx on t2009_07(station);
CREATE INDEX t2009_07_valid_idx on t2009_07(valid);
GRANT SELECT on t2009_07 to nobody,apache;


create table t2009_08( 
  CONSTRAINT __t2009_08_check 
  CHECK(valid >= '2009-08-01 00:00+00'::timestamptz 
        and valid < '2009-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_08_station_idx on t2009_08(station);
CREATE INDEX t2009_08_valid_idx on t2009_08(valid);
GRANT SELECT on t2009_08 to nobody,apache;


create table t2009_09( 
  CONSTRAINT __t2009_09_check 
  CHECK(valid >= '2009-09-01 00:00+00'::timestamptz 
        and valid < '2009-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_09_station_idx on t2009_09(station);
CREATE INDEX t2009_09_valid_idx on t2009_09(valid);
GRANT SELECT on t2009_09 to nobody,apache;


create table t2009_10( 
  CONSTRAINT __t2009_10_check 
  CHECK(valid >= '2009-10-01 00:00+00'::timestamptz 
        and valid < '2009-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_10_station_idx on t2009_10(station);
CREATE INDEX t2009_10_valid_idx on t2009_10(valid);
GRANT SELECT on t2009_10 to nobody,apache;


create table t2009_11( 
  CONSTRAINT __t2009_11_check 
  CHECK(valid >= '2009-11-01 00:00+00'::timestamptz 
        and valid < '2009-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_11_station_idx on t2009_11(station);
CREATE INDEX t2009_11_valid_idx on t2009_11(valid);
GRANT SELECT on t2009_11 to nobody,apache;


create table t2009_12( 
  CONSTRAINT __t2009_12_check 
  CHECK(valid >= '2009-12-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_12_station_idx on t2009_12(station);
CREATE INDEX t2009_12_valid_idx on t2009_12(valid);
GRANT SELECT on t2009_12 to nobody,apache;


create table t2010_01( 
  CONSTRAINT __t2010_01_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2010-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_01_station_idx on t2010_01(station);
CREATE INDEX t2010_01_valid_idx on t2010_01(valid);
GRANT SELECT on t2010_01 to nobody,apache;


create table t2010_02( 
  CONSTRAINT __t2010_02_check 
  CHECK(valid >= '2010-02-01 00:00+00'::timestamptz 
        and valid < '2010-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_02_station_idx on t2010_02(station);
CREATE INDEX t2010_02_valid_idx on t2010_02(valid);
GRANT SELECT on t2010_02 to nobody,apache;


create table t2010_03( 
  CONSTRAINT __t2010_03_check 
  CHECK(valid >= '2010-03-01 00:00+00'::timestamptz 
        and valid < '2010-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_03_station_idx on t2010_03(station);
CREATE INDEX t2010_03_valid_idx on t2010_03(valid);
GRANT SELECT on t2010_03 to nobody,apache;


create table t2010_04( 
  CONSTRAINT __t2010_04_check 
  CHECK(valid >= '2010-04-01 00:00+00'::timestamptz 
        and valid < '2010-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_04_station_idx on t2010_04(station);
CREATE INDEX t2010_04_valid_idx on t2010_04(valid);
GRANT SELECT on t2010_04 to nobody,apache;


create table t2010_05( 
  CONSTRAINT __t2010_05_check 
  CHECK(valid >= '2010-05-01 00:00+00'::timestamptz 
        and valid < '2010-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_05_station_idx on t2010_05(station);
CREATE INDEX t2010_05_valid_idx on t2010_05(valid);
GRANT SELECT on t2010_05 to nobody,apache;


create table t2010_06( 
  CONSTRAINT __t2010_06_check 
  CHECK(valid >= '2010-06-01 00:00+00'::timestamptz 
        and valid < '2010-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_06_station_idx on t2010_06(station);
CREATE INDEX t2010_06_valid_idx on t2010_06(valid);
GRANT SELECT on t2010_06 to nobody,apache;


create table t2010_07( 
  CONSTRAINT __t2010_07_check 
  CHECK(valid >= '2010-07-01 00:00+00'::timestamptz 
        and valid < '2010-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_07_station_idx on t2010_07(station);
CREATE INDEX t2010_07_valid_idx on t2010_07(valid);
GRANT SELECT on t2010_07 to nobody,apache;


create table t2010_08( 
  CONSTRAINT __t2010_08_check 
  CHECK(valid >= '2010-08-01 00:00+00'::timestamptz 
        and valid < '2010-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_08_station_idx on t2010_08(station);
CREATE INDEX t2010_08_valid_idx on t2010_08(valid);
GRANT SELECT on t2010_08 to nobody,apache;


create table t2010_09( 
  CONSTRAINT __t2010_09_check 
  CHECK(valid >= '2010-09-01 00:00+00'::timestamptz 
        and valid < '2010-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_09_station_idx on t2010_09(station);
CREATE INDEX t2010_09_valid_idx on t2010_09(valid);
GRANT SELECT on t2010_09 to nobody,apache;


create table t2010_10( 
  CONSTRAINT __t2010_10_check 
  CHECK(valid >= '2010-10-01 00:00+00'::timestamptz 
        and valid < '2010-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_10_station_idx on t2010_10(station);
CREATE INDEX t2010_10_valid_idx on t2010_10(valid);
GRANT SELECT on t2010_10 to nobody,apache;


create table t2010_11( 
  CONSTRAINT __t2010_11_check 
  CHECK(valid >= '2010-11-01 00:00+00'::timestamptz 
        and valid < '2010-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_11_station_idx on t2010_11(station);
CREATE INDEX t2010_11_valid_idx on t2010_11(valid);
GRANT SELECT on t2010_11 to nobody,apache;


create table t2010_12( 
  CONSTRAINT __t2010_12_check 
  CHECK(valid >= '2010-12-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_12_station_idx on t2010_12(station);
CREATE INDEX t2010_12_valid_idx on t2010_12(valid);
GRANT SELECT on t2010_12 to nobody,apache;


create table t2011_01( 
  CONSTRAINT __t2011_01_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2011-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_01_station_idx on t2011_01(station);
CREATE INDEX t2011_01_valid_idx on t2011_01(valid);
GRANT SELECT on t2011_01 to nobody,apache;


create table t2011_02( 
  CONSTRAINT __t2011_02_check 
  CHECK(valid >= '2011-02-01 00:00+00'::timestamptz 
        and valid < '2011-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_02_station_idx on t2011_02(station);
CREATE INDEX t2011_02_valid_idx on t2011_02(valid);
GRANT SELECT on t2011_02 to nobody,apache;


create table t2011_03( 
  CONSTRAINT __t2011_03_check 
  CHECK(valid >= '2011-03-01 00:00+00'::timestamptz 
        and valid < '2011-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_03_station_idx on t2011_03(station);
CREATE INDEX t2011_03_valid_idx on t2011_03(valid);
GRANT SELECT on t2011_03 to nobody,apache;
