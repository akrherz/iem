-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (4, now());

CREATE FUNCTION local_date(timestamp with time zone) RETURNS date
    LANGUAGE sql IMMUTABLE
    AS $_$select date($1)$_$;


CREATE TABLE dump (
    station character varying(5),
    valid timestamp with time zone,
    tmpf smallint,
    dwpf smallint,
    drct smallint,
    sknt real,
    pday real,
    pmonth real,
    srad real,
    relh real,
    alti real,
    gust real
);

CREATE TABLE temp (
    station character varying(5),
    valid timestamp with time zone,
    tmpf smallint,
    dwpf smallint,
    drct smallint,
    sknt real,
    pday real,
    pmonth real,
    srad real,
    relh real,
    alti real,
    gust real
);

CREATE TABLE alldata (
    station character varying(5),
    valid timestamp with time zone,
    tmpf smallint,
    dwpf smallint,
    drct smallint,
    sknt real,
    pday real,
    pmonth real,
    srad real,
    relh real,
    alti real,
    gust real
);
GRANT SELECT on alldata to nobody,apache;

 create table t2002_01( 
  CONSTRAINT __t2002_01_check 
  CHECK(valid >= '2002-01-01 00:00+00'::timestamptz 
        and valid < '2002-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_01_station on t2002_01(station);
CREATE INDEX t2002_01_valid_idx on t2002_01(valid);
GRANT SELECT on t2002_01 to nobody,apache;


 create table t2002_02( 
  CONSTRAINT __t2002_02_check 
  CHECK(valid >= '2002-02-01 00:00+00'::timestamptz 
        and valid < '2002-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_02_station on t2002_02(station);
CREATE INDEX t2002_02_valid_idx on t2002_02(valid);
GRANT SELECT on t2002_02 to nobody,apache;


 create table t2002_03( 
  CONSTRAINT __t2002_03_check 
  CHECK(valid >= '2002-03-01 00:00+00'::timestamptz 
        and valid < '2002-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_03_station on t2002_03(station);
CREATE INDEX t2002_03_valid_idx on t2002_03(valid);
GRANT SELECT on t2002_03 to nobody,apache;


 create table t2002_04( 
  CONSTRAINT __t2002_04_check 
  CHECK(valid >= '2002-04-01 00:00+00'::timestamptz 
        and valid < '2002-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_04_station on t2002_04(station);
CREATE INDEX t2002_04_valid_idx on t2002_04(valid);
GRANT SELECT on t2002_04 to nobody,apache;


 create table t2002_05( 
  CONSTRAINT __t2002_05_check 
  CHECK(valid >= '2002-05-01 00:00+00'::timestamptz 
        and valid < '2002-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_05_station on t2002_05(station);
CREATE INDEX t2002_05_valid_idx on t2002_05(valid);
GRANT SELECT on t2002_05 to nobody,apache;


 create table t2002_06( 
  CONSTRAINT __t2002_06_check 
  CHECK(valid >= '2002-06-01 00:00+00'::timestamptz 
        and valid < '2002-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_06_station on t2002_06(station);
CREATE INDEX t2002_06_valid_idx on t2002_06(valid);
GRANT SELECT on t2002_06 to nobody,apache;


 create table t2002_07( 
  CONSTRAINT __t2002_07_check 
  CHECK(valid >= '2002-07-01 00:00+00'::timestamptz 
        and valid < '2002-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_07_station on t2002_07(station);
CREATE INDEX t2002_07_valid_idx on t2002_07(valid);
GRANT SELECT on t2002_07 to nobody,apache;


 create table t2002_08( 
  CONSTRAINT __t2002_08_check 
  CHECK(valid >= '2002-08-01 00:00+00'::timestamptz 
        and valid < '2002-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_08_station on t2002_08(station);
CREATE INDEX t2002_08_valid_idx on t2002_08(valid);
GRANT SELECT on t2002_08 to nobody,apache;


 create table t2002_09( 
  CONSTRAINT __t2002_09_check 
  CHECK(valid >= '2002-09-01 00:00+00'::timestamptz 
        and valid < '2002-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_09_station on t2002_09(station);
CREATE INDEX t2002_09_valid_idx on t2002_09(valid);
GRANT SELECT on t2002_09 to nobody,apache;


 create table t2002_10( 
  CONSTRAINT __t2002_10_check 
  CHECK(valid >= '2002-10-01 00:00+00'::timestamptz 
        and valid < '2002-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_10_station on t2002_10(station);
CREATE INDEX t2002_10_valid_idx on t2002_10(valid);
GRANT SELECT on t2002_10 to nobody,apache;


 create table t2002_11( 
  CONSTRAINT __t2002_11_check 
  CHECK(valid >= '2002-11-01 00:00+00'::timestamptz 
        and valid < '2002-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_11_station on t2002_11(station);
CREATE INDEX t2002_11_valid_idx on t2002_11(valid);
GRANT SELECT on t2002_11 to nobody,apache;


 create table t2002_12( 
  CONSTRAINT __t2002_12_check 
  CHECK(valid >= '2002-12-01 00:00+00'::timestamptz 
        and valid < '2003-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2002_12_station on t2002_12(station);
CREATE INDEX t2002_12_valid_idx on t2002_12(valid);
GRANT SELECT on t2002_12 to nobody,apache;


 create table t2003_01( 
  CONSTRAINT __t2003_01_check 
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz 
        and valid < '2003-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_01_station on t2003_01(station);
CREATE INDEX t2003_01_valid_idx on t2003_01(valid);
GRANT SELECT on t2003_01 to nobody,apache;


 create table t2003_02( 
  CONSTRAINT __t2003_02_check 
  CHECK(valid >= '2003-02-01 00:00+00'::timestamptz 
        and valid < '2003-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_02_station on t2003_02(station);
CREATE INDEX t2003_02_valid_idx on t2003_02(valid);
GRANT SELECT on t2003_02 to nobody,apache;


 create table t2003_03( 
  CONSTRAINT __t2003_03_check 
  CHECK(valid >= '2003-03-01 00:00+00'::timestamptz 
        and valid < '2003-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_03_station on t2003_03(station);
CREATE INDEX t2003_03_valid_idx on t2003_03(valid);
GRANT SELECT on t2003_03 to nobody,apache;


 create table t2003_04( 
  CONSTRAINT __t2003_04_check 
  CHECK(valid >= '2003-04-01 00:00+00'::timestamptz 
        and valid < '2003-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_04_station on t2003_04(station);
CREATE INDEX t2003_04_valid_idx on t2003_04(valid);
GRANT SELECT on t2003_04 to nobody,apache;


 create table t2003_05( 
  CONSTRAINT __t2003_05_check 
  CHECK(valid >= '2003-05-01 00:00+00'::timestamptz 
        and valid < '2003-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_05_station on t2003_05(station);
CREATE INDEX t2003_05_valid_idx on t2003_05(valid);
GRANT SELECT on t2003_05 to nobody,apache;


 create table t2003_06( 
  CONSTRAINT __t2003_06_check 
  CHECK(valid >= '2003-06-01 00:00+00'::timestamptz 
        and valid < '2003-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_06_station on t2003_06(station);
CREATE INDEX t2003_06_valid_idx on t2003_06(valid);
GRANT SELECT on t2003_06 to nobody,apache;


 create table t2003_07( 
  CONSTRAINT __t2003_07_check 
  CHECK(valid >= '2003-07-01 00:00+00'::timestamptz 
        and valid < '2003-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_07_station on t2003_07(station);
CREATE INDEX t2003_07_valid_idx on t2003_07(valid);
GRANT SELECT on t2003_07 to nobody,apache;


 create table t2003_08( 
  CONSTRAINT __t2003_08_check 
  CHECK(valid >= '2003-08-01 00:00+00'::timestamptz 
        and valid < '2003-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_08_station on t2003_08(station);
CREATE INDEX t2003_08_valid_idx on t2003_08(valid);
GRANT SELECT on t2003_08 to nobody,apache;


 create table t2003_09( 
  CONSTRAINT __t2003_09_check 
  CHECK(valid >= '2003-09-01 00:00+00'::timestamptz 
        and valid < '2003-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_09_station on t2003_09(station);
CREATE INDEX t2003_09_valid_idx on t2003_09(valid);
GRANT SELECT on t2003_09 to nobody,apache;


 create table t2003_10( 
  CONSTRAINT __t2003_10_check 
  CHECK(valid >= '2003-10-01 00:00+00'::timestamptz 
        and valid < '2003-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_10_station on t2003_10(station);
CREATE INDEX t2003_10_valid_idx on t2003_10(valid);
GRANT SELECT on t2003_10 to nobody,apache;


 create table t2003_11( 
  CONSTRAINT __t2003_11_check 
  CHECK(valid >= '2003-11-01 00:00+00'::timestamptz 
        and valid < '2003-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_11_station on t2003_11(station);
CREATE INDEX t2003_11_valid_idx on t2003_11(valid);
GRANT SELECT on t2003_11 to nobody,apache;


 create table t2003_12( 
  CONSTRAINT __t2003_12_check 
  CHECK(valid >= '2003-12-01 00:00+00'::timestamptz 
        and valid < '2004-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_12_station on t2003_12(station);
CREATE INDEX t2003_12_valid_idx on t2003_12(valid);
GRANT SELECT on t2003_12 to nobody,apache;


 create table t2004_01( 
  CONSTRAINT __t2004_01_check 
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz 
        and valid < '2004-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_01_station on t2004_01(station);
CREATE INDEX t2004_01_valid_idx on t2004_01(valid);
GRANT SELECT on t2004_01 to nobody,apache;


 create table t2004_02( 
  CONSTRAINT __t2004_02_check 
  CHECK(valid >= '2004-02-01 00:00+00'::timestamptz 
        and valid < '2004-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_02_station on t2004_02(station);
CREATE INDEX t2004_02_valid_idx on t2004_02(valid);
GRANT SELECT on t2004_02 to nobody,apache;


 create table t2004_03( 
  CONSTRAINT __t2004_03_check 
  CHECK(valid >= '2004-03-01 00:00+00'::timestamptz 
        and valid < '2004-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_03_station on t2004_03(station);
CREATE INDEX t2004_03_valid_idx on t2004_03(valid);
GRANT SELECT on t2004_03 to nobody,apache;


 create table t2004_04( 
  CONSTRAINT __t2004_04_check 
  CHECK(valid >= '2004-04-01 00:00+00'::timestamptz 
        and valid < '2004-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_04_station on t2004_04(station);
CREATE INDEX t2004_04_valid_idx on t2004_04(valid);
GRANT SELECT on t2004_04 to nobody,apache;


 create table t2004_05( 
  CONSTRAINT __t2004_05_check 
  CHECK(valid >= '2004-05-01 00:00+00'::timestamptz 
        and valid < '2004-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_05_station on t2004_05(station);
CREATE INDEX t2004_05_valid_idx on t2004_05(valid);
GRANT SELECT on t2004_05 to nobody,apache;


 create table t2004_06( 
  CONSTRAINT __t2004_06_check 
  CHECK(valid >= '2004-06-01 00:00+00'::timestamptz 
        and valid < '2004-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_06_station on t2004_06(station);
CREATE INDEX t2004_06_valid_idx on t2004_06(valid);
GRANT SELECT on t2004_06 to nobody,apache;


 create table t2004_07( 
  CONSTRAINT __t2004_07_check 
  CHECK(valid >= '2004-07-01 00:00+00'::timestamptz 
        and valid < '2004-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_07_station on t2004_07(station);
CREATE INDEX t2004_07_valid_idx on t2004_07(valid);
GRANT SELECT on t2004_07 to nobody,apache;


 create table t2004_08( 
  CONSTRAINT __t2004_08_check 
  CHECK(valid >= '2004-08-01 00:00+00'::timestamptz 
        and valid < '2004-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_08_station on t2004_08(station);
CREATE INDEX t2004_08_valid_idx on t2004_08(valid);
GRANT SELECT on t2004_08 to nobody,apache;


 create table t2004_09( 
  CONSTRAINT __t2004_09_check 
  CHECK(valid >= '2004-09-01 00:00+00'::timestamptz 
        and valid < '2004-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_09_station on t2004_09(station);
CREATE INDEX t2004_09_valid_idx on t2004_09(valid);
GRANT SELECT on t2004_09 to nobody,apache;


 create table t2004_10( 
  CONSTRAINT __t2004_10_check 
  CHECK(valid >= '2004-10-01 00:00+00'::timestamptz 
        and valid < '2004-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_10_station on t2004_10(station);
CREATE INDEX t2004_10_valid_idx on t2004_10(valid);
GRANT SELECT on t2004_10 to nobody,apache;


 create table t2004_11( 
  CONSTRAINT __t2004_11_check 
  CHECK(valid >= '2004-11-01 00:00+00'::timestamptz 
        and valid < '2004-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_11_station on t2004_11(station);
CREATE INDEX t2004_11_valid_idx on t2004_11(valid);
GRANT SELECT on t2004_11 to nobody,apache;


 create table t2004_12( 
  CONSTRAINT __t2004_12_check 
  CHECK(valid >= '2004-12-01 00:00+00'::timestamptz 
        and valid < '2005-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_12_station on t2004_12(station);
CREATE INDEX t2004_12_valid_idx on t2004_12(valid);
GRANT SELECT on t2004_12 to nobody,apache;


 create table t2005_01( 
  CONSTRAINT __t2005_01_check 
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz 
        and valid < '2005-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_01_station on t2005_01(station);
CREATE INDEX t2005_01_valid_idx on t2005_01(valid);
GRANT SELECT on t2005_01 to nobody,apache;


 create table t2005_02( 
  CONSTRAINT __t2005_02_check 
  CHECK(valid >= '2005-02-01 00:00+00'::timestamptz 
        and valid < '2005-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_02_station on t2005_02(station);
CREATE INDEX t2005_02_valid_idx on t2005_02(valid);
GRANT SELECT on t2005_02 to nobody,apache;


 create table t2005_03( 
  CONSTRAINT __t2005_03_check 
  CHECK(valid >= '2005-03-01 00:00+00'::timestamptz 
        and valid < '2005-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_03_station on t2005_03(station);
CREATE INDEX t2005_03_valid_idx on t2005_03(valid);
GRANT SELECT on t2005_03 to nobody,apache;


 create table t2005_04( 
  CONSTRAINT __t2005_04_check 
  CHECK(valid >= '2005-04-01 00:00+00'::timestamptz 
        and valid < '2005-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_04_station on t2005_04(station);
CREATE INDEX t2005_04_valid_idx on t2005_04(valid);
GRANT SELECT on t2005_04 to nobody,apache;


 create table t2005_05( 
  CONSTRAINT __t2005_05_check 
  CHECK(valid >= '2005-05-01 00:00+00'::timestamptz 
        and valid < '2005-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_05_station on t2005_05(station);
CREATE INDEX t2005_05_valid_idx on t2005_05(valid);
GRANT SELECT on t2005_05 to nobody,apache;


 create table t2005_06( 
  CONSTRAINT __t2005_06_check 
  CHECK(valid >= '2005-06-01 00:00+00'::timestamptz 
        and valid < '2005-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_06_station on t2005_06(station);
CREATE INDEX t2005_06_valid_idx on t2005_06(valid);
GRANT SELECT on t2005_06 to nobody,apache;


 create table t2005_07( 
  CONSTRAINT __t2005_07_check 
  CHECK(valid >= '2005-07-01 00:00+00'::timestamptz 
        and valid < '2005-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_07_station on t2005_07(station);
CREATE INDEX t2005_07_valid_idx on t2005_07(valid);
GRANT SELECT on t2005_07 to nobody,apache;


 create table t2005_08( 
  CONSTRAINT __t2005_08_check 
  CHECK(valid >= '2005-08-01 00:00+00'::timestamptz 
        and valid < '2005-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_08_station on t2005_08(station);
CREATE INDEX t2005_08_valid_idx on t2005_08(valid);
GRANT SELECT on t2005_08 to nobody,apache;


 create table t2005_09( 
  CONSTRAINT __t2005_09_check 
  CHECK(valid >= '2005-09-01 00:00+00'::timestamptz 
        and valid < '2005-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_09_station on t2005_09(station);
CREATE INDEX t2005_09_valid_idx on t2005_09(valid);
GRANT SELECT on t2005_09 to nobody,apache;


 create table t2005_10( 
  CONSTRAINT __t2005_10_check 
  CHECK(valid >= '2005-10-01 00:00+00'::timestamptz 
        and valid < '2005-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_10_station on t2005_10(station);
CREATE INDEX t2005_10_valid_idx on t2005_10(valid);
GRANT SELECT on t2005_10 to nobody,apache;


 create table t2005_11( 
  CONSTRAINT __t2005_11_check 
  CHECK(valid >= '2005-11-01 00:00+00'::timestamptz 
        and valid < '2005-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_11_station on t2005_11(station);
CREATE INDEX t2005_11_valid_idx on t2005_11(valid);
GRANT SELECT on t2005_11 to nobody,apache;


 create table t2005_12( 
  CONSTRAINT __t2005_12_check 
  CHECK(valid >= '2005-12-01 00:00+00'::timestamptz 
        and valid < '2006-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_12_station on t2005_12(station);
CREATE INDEX t2005_12_valid_idx on t2005_12(valid);
GRANT SELECT on t2005_12 to nobody,apache;


 create table t2006_01( 
  CONSTRAINT __t2006_01_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz 
        and valid < '2006-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_01_station on t2006_01(station);
CREATE INDEX t2006_01_valid_idx on t2006_01(valid);
GRANT SELECT on t2006_01 to nobody,apache;


 create table t2006_02( 
  CONSTRAINT __t2006_02_check 
  CHECK(valid >= '2006-02-01 00:00+00'::timestamptz 
        and valid < '2006-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_02_station on t2006_02(station);
CREATE INDEX t2006_02_valid_idx on t2006_02(valid);
GRANT SELECT on t2006_02 to nobody,apache;


 create table t2006_03( 
  CONSTRAINT __t2006_03_check 
  CHECK(valid >= '2006-03-01 00:00+00'::timestamptz 
        and valid < '2006-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_03_station on t2006_03(station);
CREATE INDEX t2006_03_valid_idx on t2006_03(valid);
GRANT SELECT on t2006_03 to nobody,apache;


 create table t2006_04( 
  CONSTRAINT __t2006_04_check 
  CHECK(valid >= '2006-04-01 00:00+00'::timestamptz 
        and valid < '2006-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_04_station on t2006_04(station);
CREATE INDEX t2006_04_valid_idx on t2006_04(valid);
GRANT SELECT on t2006_04 to nobody,apache;


 create table t2006_05( 
  CONSTRAINT __t2006_05_check 
  CHECK(valid >= '2006-05-01 00:00+00'::timestamptz 
        and valid < '2006-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_05_station on t2006_05(station);
CREATE INDEX t2006_05_valid_idx on t2006_05(valid);
GRANT SELECT on t2006_05 to nobody,apache;


 create table t2006_06( 
  CONSTRAINT __t2006_06_check 
  CHECK(valid >= '2006-06-01 00:00+00'::timestamptz 
        and valid < '2006-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_06_station on t2006_06(station);
CREATE INDEX t2006_06_valid_idx on t2006_06(valid);
GRANT SELECT on t2006_06 to nobody,apache;


 create table t2006_07( 
  CONSTRAINT __t2006_07_check 
  CHECK(valid >= '2006-07-01 00:00+00'::timestamptz 
        and valid < '2006-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_07_station on t2006_07(station);
CREATE INDEX t2006_07_valid_idx on t2006_07(valid);
GRANT SELECT on t2006_07 to nobody,apache;


 create table t2006_08( 
  CONSTRAINT __t2006_08_check 
  CHECK(valid >= '2006-08-01 00:00+00'::timestamptz 
        and valid < '2006-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_08_station on t2006_08(station);
CREATE INDEX t2006_08_valid_idx on t2006_08(valid);
GRANT SELECT on t2006_08 to nobody,apache;


 create table t2006_09( 
  CONSTRAINT __t2006_09_check 
  CHECK(valid >= '2006-09-01 00:00+00'::timestamptz 
        and valid < '2006-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_09_station on t2006_09(station);
CREATE INDEX t2006_09_valid_idx on t2006_09(valid);
GRANT SELECT on t2006_09 to nobody,apache;


 create table t2006_10( 
  CONSTRAINT __t2006_10_check 
  CHECK(valid >= '2006-10-01 00:00+00'::timestamptz 
        and valid < '2006-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_10_station on t2006_10(station);
CREATE INDEX t2006_10_valid_idx on t2006_10(valid);
GRANT SELECT on t2006_10 to nobody,apache;


 create table t2006_11( 
  CONSTRAINT __t2006_11_check 
  CHECK(valid >= '2006-11-01 00:00+00'::timestamptz 
        and valid < '2006-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_11_station on t2006_11(station);
CREATE INDEX t2006_11_valid_idx on t2006_11(valid);
GRANT SELECT on t2006_11 to nobody,apache;


 create table t2006_12( 
  CONSTRAINT __t2006_12_check 
  CHECK(valid >= '2006-12-01 00:00+00'::timestamptz 
        and valid < '2007-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_12_station on t2006_12(station);
CREATE INDEX t2006_12_valid_idx on t2006_12(valid);
GRANT SELECT on t2006_12 to nobody,apache;


 create table t2007_01( 
  CONSTRAINT __t2007_01_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz 
        and valid < '2007-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_01_station on t2007_01(station);
CREATE INDEX t2007_01_valid_idx on t2007_01(valid);
GRANT SELECT on t2007_01 to nobody,apache;


 create table t2007_02( 
  CONSTRAINT __t2007_02_check 
  CHECK(valid >= '2007-02-01 00:00+00'::timestamptz 
        and valid < '2007-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_02_station on t2007_02(station);
CREATE INDEX t2007_02_valid_idx on t2007_02(valid);
GRANT SELECT on t2007_02 to nobody,apache;


 create table t2007_03( 
  CONSTRAINT __t2007_03_check 
  CHECK(valid >= '2007-03-01 00:00+00'::timestamptz 
        and valid < '2007-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_03_station on t2007_03(station);
CREATE INDEX t2007_03_valid_idx on t2007_03(valid);
GRANT SELECT on t2007_03 to nobody,apache;


 create table t2007_04( 
  CONSTRAINT __t2007_04_check 
  CHECK(valid >= '2007-04-01 00:00+00'::timestamptz 
        and valid < '2007-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_04_station on t2007_04(station);
CREATE INDEX t2007_04_valid_idx on t2007_04(valid);
GRANT SELECT on t2007_04 to nobody,apache;


 create table t2007_05( 
  CONSTRAINT __t2007_05_check 
  CHECK(valid >= '2007-05-01 00:00+00'::timestamptz 
        and valid < '2007-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_05_station on t2007_05(station);
CREATE INDEX t2007_05_valid_idx on t2007_05(valid);
GRANT SELECT on t2007_05 to nobody,apache;


 create table t2007_06( 
  CONSTRAINT __t2007_06_check 
  CHECK(valid >= '2007-06-01 00:00+00'::timestamptz 
        and valid < '2007-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_06_station on t2007_06(station);
CREATE INDEX t2007_06_valid_idx on t2007_06(valid);
GRANT SELECT on t2007_06 to nobody,apache;


 create table t2007_07( 
  CONSTRAINT __t2007_07_check 
  CHECK(valid >= '2007-07-01 00:00+00'::timestamptz 
        and valid < '2007-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_07_station on t2007_07(station);
CREATE INDEX t2007_07_valid_idx on t2007_07(valid);
GRANT SELECT on t2007_07 to nobody,apache;


 create table t2007_08( 
  CONSTRAINT __t2007_08_check 
  CHECK(valid >= '2007-08-01 00:00+00'::timestamptz 
        and valid < '2007-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_08_station on t2007_08(station);
CREATE INDEX t2007_08_valid_idx on t2007_08(valid);
GRANT SELECT on t2007_08 to nobody,apache;


 create table t2007_09( 
  CONSTRAINT __t2007_09_check 
  CHECK(valid >= '2007-09-01 00:00+00'::timestamptz 
        and valid < '2007-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_09_station on t2007_09(station);
CREATE INDEX t2007_09_valid_idx on t2007_09(valid);
GRANT SELECT on t2007_09 to nobody,apache;


 create table t2007_10( 
  CONSTRAINT __t2007_10_check 
  CHECK(valid >= '2007-10-01 00:00+00'::timestamptz 
        and valid < '2007-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_10_station on t2007_10(station);
CREATE INDEX t2007_10_valid_idx on t2007_10(valid);
GRANT SELECT on t2007_10 to nobody,apache;


 create table t2007_11( 
  CONSTRAINT __t2007_11_check 
  CHECK(valid >= '2007-11-01 00:00+00'::timestamptz 
        and valid < '2007-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_11_station on t2007_11(station);
CREATE INDEX t2007_11_valid_idx on t2007_11(valid);
GRANT SELECT on t2007_11 to nobody,apache;


 create table t2007_12( 
  CONSTRAINT __t2007_12_check 
  CHECK(valid >= '2007-12-01 00:00+00'::timestamptz 
        and valid < '2008-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_12_station on t2007_12(station);
CREATE INDEX t2007_12_valid_idx on t2007_12(valid);
GRANT SELECT on t2007_12 to nobody,apache;


 create table t2008_01( 
  CONSTRAINT __t2008_01_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2008-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_01_station on t2008_01(station);
CREATE INDEX t2008_01_valid_idx on t2008_01(valid);
GRANT SELECT on t2008_01 to nobody,apache;


 create table t2008_02( 
  CONSTRAINT __t2008_02_check 
  CHECK(valid >= '2008-02-01 00:00+00'::timestamptz 
        and valid < '2008-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_02_station on t2008_02(station);
CREATE INDEX t2008_02_valid_idx on t2008_02(valid);
GRANT SELECT on t2008_02 to nobody,apache;


 create table t2008_03( 
  CONSTRAINT __t2008_03_check 
  CHECK(valid >= '2008-03-01 00:00+00'::timestamptz 
        and valid < '2008-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_03_station on t2008_03(station);
CREATE INDEX t2008_03_valid_idx on t2008_03(valid);
GRANT SELECT on t2008_03 to nobody,apache;


 create table t2008_04( 
  CONSTRAINT __t2008_04_check 
  CHECK(valid >= '2008-04-01 00:00+00'::timestamptz 
        and valid < '2008-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_04_station on t2008_04(station);
CREATE INDEX t2008_04_valid_idx on t2008_04(valid);
GRANT SELECT on t2008_04 to nobody,apache;


 create table t2008_05( 
  CONSTRAINT __t2008_05_check 
  CHECK(valid >= '2008-05-01 00:00+00'::timestamptz 
        and valid < '2008-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_05_station on t2008_05(station);
CREATE INDEX t2008_05_valid_idx on t2008_05(valid);
GRANT SELECT on t2008_05 to nobody,apache;


 create table t2008_06( 
  CONSTRAINT __t2008_06_check 
  CHECK(valid >= '2008-06-01 00:00+00'::timestamptz 
        and valid < '2008-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_06_station on t2008_06(station);
CREATE INDEX t2008_06_valid_idx on t2008_06(valid);
GRANT SELECT on t2008_06 to nobody,apache;


 create table t2008_07( 
  CONSTRAINT __t2008_07_check 
  CHECK(valid >= '2008-07-01 00:00+00'::timestamptz 
        and valid < '2008-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_07_station on t2008_07(station);
CREATE INDEX t2008_07_valid_idx on t2008_07(valid);
GRANT SELECT on t2008_07 to nobody,apache;


 create table t2008_08( 
  CONSTRAINT __t2008_08_check 
  CHECK(valid >= '2008-08-01 00:00+00'::timestamptz 
        and valid < '2008-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_08_station on t2008_08(station);
CREATE INDEX t2008_08_valid_idx on t2008_08(valid);
GRANT SELECT on t2008_08 to nobody,apache;


 create table t2008_09( 
  CONSTRAINT __t2008_09_check 
  CHECK(valid >= '2008-09-01 00:00+00'::timestamptz 
        and valid < '2008-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_09_station on t2008_09(station);
CREATE INDEX t2008_09_valid_idx on t2008_09(valid);
GRANT SELECT on t2008_09 to nobody,apache;


 create table t2008_10( 
  CONSTRAINT __t2008_10_check 
  CHECK(valid >= '2008-10-01 00:00+00'::timestamptz 
        and valid < '2008-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_10_station on t2008_10(station);
CREATE INDEX t2008_10_valid_idx on t2008_10(valid);
GRANT SELECT on t2008_10 to nobody,apache;


 create table t2008_11( 
  CONSTRAINT __t2008_11_check 
  CHECK(valid >= '2008-11-01 00:00+00'::timestamptz 
        and valid < '2008-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_11_station on t2008_11(station);
CREATE INDEX t2008_11_valid_idx on t2008_11(valid);
GRANT SELECT on t2008_11 to nobody,apache;


 create table t2008_12( 
  CONSTRAINT __t2008_12_check 
  CHECK(valid >= '2008-12-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_12_station on t2008_12(station);
CREATE INDEX t2008_12_valid_idx on t2008_12(valid);
GRANT SELECT on t2008_12 to nobody,apache;


 create table t2009_01( 
  CONSTRAINT __t2009_01_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2009-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_01_station on t2009_01(station);
CREATE INDEX t2009_01_valid_idx on t2009_01(valid);
GRANT SELECT on t2009_01 to nobody,apache;


 create table t2009_02( 
  CONSTRAINT __t2009_02_check 
  CHECK(valid >= '2009-02-01 00:00+00'::timestamptz 
        and valid < '2009-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_02_station on t2009_02(station);
CREATE INDEX t2009_02_valid_idx on t2009_02(valid);
GRANT SELECT on t2009_02 to nobody,apache;


 create table t2009_03( 
  CONSTRAINT __t2009_03_check 
  CHECK(valid >= '2009-03-01 00:00+00'::timestamptz 
        and valid < '2009-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_03_station on t2009_03(station);
CREATE INDEX t2009_03_valid_idx on t2009_03(valid);
GRANT SELECT on t2009_03 to nobody,apache;


 create table t2009_04( 
  CONSTRAINT __t2009_04_check 
  CHECK(valid >= '2009-04-01 00:00+00'::timestamptz 
        and valid < '2009-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_04_station on t2009_04(station);
CREATE INDEX t2009_04_valid_idx on t2009_04(valid);
GRANT SELECT on t2009_04 to nobody,apache;


 create table t2009_05( 
  CONSTRAINT __t2009_05_check 
  CHECK(valid >= '2009-05-01 00:00+00'::timestamptz 
        and valid < '2009-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_05_station on t2009_05(station);
CREATE INDEX t2009_05_valid_idx on t2009_05(valid);
GRANT SELECT on t2009_05 to nobody,apache;


 create table t2009_06( 
  CONSTRAINT __t2009_06_check 
  CHECK(valid >= '2009-06-01 00:00+00'::timestamptz 
        and valid < '2009-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_06_station on t2009_06(station);
CREATE INDEX t2009_06_valid_idx on t2009_06(valid);
GRANT SELECT on t2009_06 to nobody,apache;


 create table t2009_07( 
  CONSTRAINT __t2009_07_check 
  CHECK(valid >= '2009-07-01 00:00+00'::timestamptz 
        and valid < '2009-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_07_station on t2009_07(station);
CREATE INDEX t2009_07_valid_idx on t2009_07(valid);
GRANT SELECT on t2009_07 to nobody,apache;


 create table t2009_08( 
  CONSTRAINT __t2009_08_check 
  CHECK(valid >= '2009-08-01 00:00+00'::timestamptz 
        and valid < '2009-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_08_station on t2009_08(station);
CREATE INDEX t2009_08_valid_idx on t2009_08(valid);
GRANT SELECT on t2009_08 to nobody,apache;


 create table t2009_09( 
  CONSTRAINT __t2009_09_check 
  CHECK(valid >= '2009-09-01 00:00+00'::timestamptz 
        and valid < '2009-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_09_station on t2009_09(station);
CREATE INDEX t2009_09_valid_idx on t2009_09(valid);
GRANT SELECT on t2009_09 to nobody,apache;


 create table t2009_10( 
  CONSTRAINT __t2009_10_check 
  CHECK(valid >= '2009-10-01 00:00+00'::timestamptz 
        and valid < '2009-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_10_station on t2009_10(station);
CREATE INDEX t2009_10_valid_idx on t2009_10(valid);
GRANT SELECT on t2009_10 to nobody,apache;


 create table t2009_11( 
  CONSTRAINT __t2009_11_check 
  CHECK(valid >= '2009-11-01 00:00+00'::timestamptz 
        and valid < '2009-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_11_station on t2009_11(station);
CREATE INDEX t2009_11_valid_idx on t2009_11(valid);
GRANT SELECT on t2009_11 to nobody,apache;


 create table t2009_12( 
  CONSTRAINT __t2009_12_check 
  CHECK(valid >= '2009-12-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_12_station on t2009_12(station);
CREATE INDEX t2009_12_valid_idx on t2009_12(valid);
GRANT SELECT on t2009_12 to nobody,apache;


 create table t2010_01( 
  CONSTRAINT __t2010_01_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2010-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_01_station on t2010_01(station);
CREATE INDEX t2010_01_valid_idx on t2010_01(valid);
GRANT SELECT on t2010_01 to nobody,apache;


 create table t2010_02( 
  CONSTRAINT __t2010_02_check 
  CHECK(valid >= '2010-02-01 00:00+00'::timestamptz 
        and valid < '2010-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_02_station on t2010_02(station);
CREATE INDEX t2010_02_valid_idx on t2010_02(valid);
GRANT SELECT on t2010_02 to nobody,apache;


 create table t2010_03( 
  CONSTRAINT __t2010_03_check 
  CHECK(valid >= '2010-03-01 00:00+00'::timestamptz 
        and valid < '2010-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_03_station on t2010_03(station);
CREATE INDEX t2010_03_valid_idx on t2010_03(valid);
GRANT SELECT on t2010_03 to nobody,apache;


 create table t2010_04( 
  CONSTRAINT __t2010_04_check 
  CHECK(valid >= '2010-04-01 00:00+00'::timestamptz 
        and valid < '2010-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_04_station on t2010_04(station);
CREATE INDEX t2010_04_valid_idx on t2010_04(valid);
GRANT SELECT on t2010_04 to nobody,apache;


 create table t2010_05( 
  CONSTRAINT __t2010_05_check 
  CHECK(valid >= '2010-05-01 00:00+00'::timestamptz 
        and valid < '2010-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_05_station on t2010_05(station);
CREATE INDEX t2010_05_valid_idx on t2010_05(valid);
GRANT SELECT on t2010_05 to nobody,apache;


 create table t2010_06( 
  CONSTRAINT __t2010_06_check 
  CHECK(valid >= '2010-06-01 00:00+00'::timestamptz 
        and valid < '2010-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_06_station on t2010_06(station);
CREATE INDEX t2010_06_valid_idx on t2010_06(valid);
GRANT SELECT on t2010_06 to nobody,apache;


 create table t2010_07( 
  CONSTRAINT __t2010_07_check 
  CHECK(valid >= '2010-07-01 00:00+00'::timestamptz 
        and valid < '2010-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_07_station on t2010_07(station);
CREATE INDEX t2010_07_valid_idx on t2010_07(valid);
GRANT SELECT on t2010_07 to nobody,apache;


 create table t2010_08( 
  CONSTRAINT __t2010_08_check 
  CHECK(valid >= '2010-08-01 00:00+00'::timestamptz 
        and valid < '2010-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_08_station on t2010_08(station);
CREATE INDEX t2010_08_valid_idx on t2010_08(valid);
GRANT SELECT on t2010_08 to nobody,apache;


 create table t2010_09( 
  CONSTRAINT __t2010_09_check 
  CHECK(valid >= '2010-09-01 00:00+00'::timestamptz 
        and valid < '2010-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_09_station on t2010_09(station);
CREATE INDEX t2010_09_valid_idx on t2010_09(valid);
GRANT SELECT on t2010_09 to nobody,apache;


 create table t2010_10( 
  CONSTRAINT __t2010_10_check 
  CHECK(valid >= '2010-10-01 00:00+00'::timestamptz 
        and valid < '2010-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_10_station on t2010_10(station);
CREATE INDEX t2010_10_valid_idx on t2010_10(valid);
GRANT SELECT on t2010_10 to nobody,apache;


 create table t2010_11( 
  CONSTRAINT __t2010_11_check 
  CHECK(valid >= '2010-11-01 00:00+00'::timestamptz 
        and valid < '2010-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_11_station on t2010_11(station);
CREATE INDEX t2010_11_valid_idx on t2010_11(valid);
GRANT SELECT on t2010_11 to nobody,apache;


 create table t2010_12( 
  CONSTRAINT __t2010_12_check 
  CHECK(valid >= '2010-12-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_12_station on t2010_12(station);
CREATE INDEX t2010_12_valid_idx on t2010_12(valid);
GRANT SELECT on t2010_12 to nobody,apache;


 create table t2011_01( 
  CONSTRAINT __t2011_01_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2011-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_01_station on t2011_01(station);
CREATE INDEX t2011_01_valid_idx on t2011_01(valid);
GRANT SELECT on t2011_01 to nobody,apache;


 create table t2011_02( 
  CONSTRAINT __t2011_02_check 
  CHECK(valid >= '2011-02-01 00:00+00'::timestamptz 
        and valid < '2011-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_02_station on t2011_02(station);
CREATE INDEX t2011_02_valid_idx on t2011_02(valid);
GRANT SELECT on t2011_02 to nobody,apache;


 create table t2011_03( 
  CONSTRAINT __t2011_03_check 
  CHECK(valid >= '2011-03-01 00:00+00'::timestamptz 
        and valid < '2011-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_03_station on t2011_03(station);
CREATE INDEX t2011_03_valid_idx on t2011_03(valid);
GRANT SELECT on t2011_03 to nobody,apache;


 create table t2011_04( 
  CONSTRAINT __t2011_04_check 
  CHECK(valid >= '2011-04-01 00:00+00'::timestamptz 
        and valid < '2011-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_04_station on t2011_04(station);
CREATE INDEX t2011_04_valid_idx on t2011_04(valid);
GRANT SELECT on t2011_04 to nobody,apache;


 create table t2011_05( 
  CONSTRAINT __t2011_05_check 
  CHECK(valid >= '2011-05-01 00:00+00'::timestamptz 
        and valid < '2011-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_05_station on t2011_05(station);
CREATE INDEX t2011_05_valid_idx on t2011_05(valid);
GRANT SELECT on t2011_05 to nobody,apache;


 create table t2011_06( 
  CONSTRAINT __t2011_06_check 
  CHECK(valid >= '2011-06-01 00:00+00'::timestamptz 
        and valid < '2011-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_06_station on t2011_06(station);
CREATE INDEX t2011_06_valid_idx on t2011_06(valid);
GRANT SELECT on t2011_06 to nobody,apache;


 create table t2011_07( 
  CONSTRAINT __t2011_07_check 
  CHECK(valid >= '2011-07-01 00:00+00'::timestamptz 
        and valid < '2011-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_07_station on t2011_07(station);
CREATE INDEX t2011_07_valid_idx on t2011_07(valid);
GRANT SELECT on t2011_07 to nobody,apache;


 create table t2011_08( 
  CONSTRAINT __t2011_08_check 
  CHECK(valid >= '2011-08-01 00:00+00'::timestamptz 
        and valid < '2011-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_08_station on t2011_08(station);
CREATE INDEX t2011_08_valid_idx on t2011_08(valid);
GRANT SELECT on t2011_08 to nobody,apache;


 create table t2011_09( 
  CONSTRAINT __t2011_09_check 
  CHECK(valid >= '2011-09-01 00:00+00'::timestamptz 
        and valid < '2011-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_09_station on t2011_09(station);
CREATE INDEX t2011_09_valid_idx on t2011_09(valid);
GRANT SELECT on t2011_09 to nobody,apache;


 create table t2011_10( 
  CONSTRAINT __t2011_10_check 
  CHECK(valid >= '2011-10-01 00:00+00'::timestamptz 
        and valid < '2011-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_10_station on t2011_10(station);
CREATE INDEX t2011_10_valid_idx on t2011_10(valid);
GRANT SELECT on t2011_10 to nobody,apache;


 create table t2011_11( 
  CONSTRAINT __t2011_11_check 
  CHECK(valid >= '2011-11-01 00:00+00'::timestamptz 
        and valid < '2011-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_11_station on t2011_11(station);
CREATE INDEX t2011_11_valid_idx on t2011_11(valid);
GRANT SELECT on t2011_11 to nobody,apache;


 create table t2011_12( 
  CONSTRAINT __t2011_12_check 
  CHECK(valid >= '2011-12-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_12_station on t2011_12(station);
CREATE INDEX t2011_12_valid_idx on t2011_12(valid);
GRANT SELECT on t2011_12 to nobody,apache;


 create table t2012_01( 
  CONSTRAINT __t2012_01_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2012-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_01_station on t2012_01(station);
CREATE INDEX t2012_01_valid_idx on t2012_01(valid);
GRANT SELECT on t2012_01 to nobody,apache;


 create table t2012_02( 
  CONSTRAINT __t2012_02_check 
  CHECK(valid >= '2012-02-01 00:00+00'::timestamptz 
        and valid < '2012-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_02_station on t2012_02(station);
CREATE INDEX t2012_02_valid_idx on t2012_02(valid);
GRANT SELECT on t2012_02 to nobody,apache;


 create table t2012_03( 
  CONSTRAINT __t2012_03_check 
  CHECK(valid >= '2012-03-01 00:00+00'::timestamptz 
        and valid < '2012-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_03_station on t2012_03(station);
CREATE INDEX t2012_03_valid_idx on t2012_03(valid);
GRANT SELECT on t2012_03 to nobody,apache;


 create table t2012_04( 
  CONSTRAINT __t2012_04_check 
  CHECK(valid >= '2012-04-01 00:00+00'::timestamptz 
        and valid < '2012-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_04_station on t2012_04(station);
CREATE INDEX t2012_04_valid_idx on t2012_04(valid);
GRANT SELECT on t2012_04 to nobody,apache;


 create table t2012_05( 
  CONSTRAINT __t2012_05_check 
  CHECK(valid >= '2012-05-01 00:00+00'::timestamptz 
        and valid < '2012-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_05_station on t2012_05(station);
CREATE INDEX t2012_05_valid_idx on t2012_05(valid);
GRANT SELECT on t2012_05 to nobody,apache;


 create table t2012_06( 
  CONSTRAINT __t2012_06_check 
  CHECK(valid >= '2012-06-01 00:00+00'::timestamptz 
        and valid < '2012-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_06_station on t2012_06(station);
CREATE INDEX t2012_06_valid_idx on t2012_06(valid);
GRANT SELECT on t2012_06 to nobody,apache;


 create table t2012_07( 
  CONSTRAINT __t2012_07_check 
  CHECK(valid >= '2012-07-01 00:00+00'::timestamptz 
        and valid < '2012-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_07_station on t2012_07(station);
CREATE INDEX t2012_07_valid_idx on t2012_07(valid);
GRANT SELECT on t2012_07 to nobody,apache;


 create table t2012_08( 
  CONSTRAINT __t2012_08_check 
  CHECK(valid >= '2012-08-01 00:00+00'::timestamptz 
        and valid < '2012-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_08_station on t2012_08(station);
CREATE INDEX t2012_08_valid_idx on t2012_08(valid);
GRANT SELECT on t2012_08 to nobody,apache;


 create table t2012_09( 
  CONSTRAINT __t2012_09_check 
  CHECK(valid >= '2012-09-01 00:00+00'::timestamptz 
        and valid < '2012-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_09_station on t2012_09(station);
CREATE INDEX t2012_09_valid_idx on t2012_09(valid);
GRANT SELECT on t2012_09 to nobody,apache;


 create table t2012_10( 
  CONSTRAINT __t2012_10_check 
  CHECK(valid >= '2012-10-01 00:00+00'::timestamptz 
        and valid < '2012-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_10_station on t2012_10(station);
CREATE INDEX t2012_10_valid_idx on t2012_10(valid);
GRANT SELECT on t2012_10 to nobody,apache;


 create table t2012_11( 
  CONSTRAINT __t2012_11_check 
  CHECK(valid >= '2012-11-01 00:00+00'::timestamptz 
        and valid < '2012-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_11_station on t2012_11(station);
CREATE INDEX t2012_11_valid_idx on t2012_11(valid);
GRANT SELECT on t2012_11 to nobody,apache;


 create table t2012_12( 
  CONSTRAINT __t2012_12_check 
  CHECK(valid >= '2012-12-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_12_station on t2012_12(station);
CREATE INDEX t2012_12_valid_idx on t2012_12(valid);
GRANT SELECT on t2012_12 to nobody,apache;


 create table t2013_01( 
  CONSTRAINT __t2013_01_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2013-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_01_station on t2013_01(station);
CREATE INDEX t2013_01_valid_idx on t2013_01(valid);
GRANT SELECT on t2013_01 to nobody,apache;


 create table t2013_02( 
  CONSTRAINT __t2013_02_check 
  CHECK(valid >= '2013-02-01 00:00+00'::timestamptz 
        and valid < '2013-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_02_station on t2013_02(station);
CREATE INDEX t2013_02_valid_idx on t2013_02(valid);
GRANT SELECT on t2013_02 to nobody,apache;


 create table t2013_03( 
  CONSTRAINT __t2013_03_check 
  CHECK(valid >= '2013-03-01 00:00+00'::timestamptz 
        and valid < '2013-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_03_station on t2013_03(station);
CREATE INDEX t2013_03_valid_idx on t2013_03(valid);
GRANT SELECT on t2013_03 to nobody,apache;


 create table t2013_04( 
  CONSTRAINT __t2013_04_check 
  CHECK(valid >= '2013-04-01 00:00+00'::timestamptz 
        and valid < '2013-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_04_station on t2013_04(station);
CREATE INDEX t2013_04_valid_idx on t2013_04(valid);
GRANT SELECT on t2013_04 to nobody,apache;


 create table t2013_05( 
  CONSTRAINT __t2013_05_check 
  CHECK(valid >= '2013-05-01 00:00+00'::timestamptz 
        and valid < '2013-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_05_station on t2013_05(station);
CREATE INDEX t2013_05_valid_idx on t2013_05(valid);
GRANT SELECT on t2013_05 to nobody,apache;


 create table t2013_06( 
  CONSTRAINT __t2013_06_check 
  CHECK(valid >= '2013-06-01 00:00+00'::timestamptz 
        and valid < '2013-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_06_station on t2013_06(station);
CREATE INDEX t2013_06_valid_idx on t2013_06(valid);
GRANT SELECT on t2013_06 to nobody,apache;


 create table t2013_07( 
  CONSTRAINT __t2013_07_check 
  CHECK(valid >= '2013-07-01 00:00+00'::timestamptz 
        and valid < '2013-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_07_station on t2013_07(station);
CREATE INDEX t2013_07_valid_idx on t2013_07(valid);
GRANT SELECT on t2013_07 to nobody,apache;


 create table t2013_08( 
  CONSTRAINT __t2013_08_check 
  CHECK(valid >= '2013-08-01 00:00+00'::timestamptz 
        and valid < '2013-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_08_station on t2013_08(station);
CREATE INDEX t2013_08_valid_idx on t2013_08(valid);
GRANT SELECT on t2013_08 to nobody,apache;


 create table t2013_09( 
  CONSTRAINT __t2013_09_check 
  CHECK(valid >= '2013-09-01 00:00+00'::timestamptz 
        and valid < '2013-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_09_station on t2013_09(station);
CREATE INDEX t2013_09_valid_idx on t2013_09(valid);
GRANT SELECT on t2013_09 to nobody,apache;


 create table t2013_10( 
  CONSTRAINT __t2013_10_check 
  CHECK(valid >= '2013-10-01 00:00+00'::timestamptz 
        and valid < '2013-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_10_station on t2013_10(station);
CREATE INDEX t2013_10_valid_idx on t2013_10(valid);
GRANT SELECT on t2013_10 to nobody,apache;


 create table t2013_11( 
  CONSTRAINT __t2013_11_check 
  CHECK(valid >= '2013-11-01 00:00+00'::timestamptz 
        and valid < '2013-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_11_station on t2013_11(station);
CREATE INDEX t2013_11_valid_idx on t2013_11(valid);
GRANT SELECT on t2013_11 to nobody,apache;


 create table t2013_12( 
  CONSTRAINT __t2013_12_check 
  CHECK(valid >= '2013-12-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_12_station on t2013_12(station);
CREATE INDEX t2013_12_valid_idx on t2013_12(valid);
GRANT SELECT on t2013_12 to nobody,apache;


 create table t2014_01( 
  CONSTRAINT __t2014_01_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2014-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_01_station on t2014_01(station);
CREATE INDEX t2014_01_valid_idx on t2014_01(valid);
GRANT SELECT on t2014_01 to nobody,apache;


 create table t2014_02( 
  CONSTRAINT __t2014_02_check 
  CHECK(valid >= '2014-02-01 00:00+00'::timestamptz 
        and valid < '2014-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_02_station on t2014_02(station);
CREATE INDEX t2014_02_valid_idx on t2014_02(valid);
GRANT SELECT on t2014_02 to nobody,apache;


 create table t2014_03( 
  CONSTRAINT __t2014_03_check 
  CHECK(valid >= '2014-03-01 00:00+00'::timestamptz 
        and valid < '2014-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_03_station on t2014_03(station);
CREATE INDEX t2014_03_valid_idx on t2014_03(valid);
GRANT SELECT on t2014_03 to nobody,apache;


 create table t2014_04( 
  CONSTRAINT __t2014_04_check 
  CHECK(valid >= '2014-04-01 00:00+00'::timestamptz 
        and valid < '2014-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_04_station on t2014_04(station);
CREATE INDEX t2014_04_valid_idx on t2014_04(valid);
GRANT SELECT on t2014_04 to nobody,apache;


 create table t2014_05( 
  CONSTRAINT __t2014_05_check 
  CHECK(valid >= '2014-05-01 00:00+00'::timestamptz 
        and valid < '2014-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_05_station on t2014_05(station);
CREATE INDEX t2014_05_valid_idx on t2014_05(valid);
GRANT SELECT on t2014_05 to nobody,apache;


 create table t2014_06( 
  CONSTRAINT __t2014_06_check 
  CHECK(valid >= '2014-06-01 00:00+00'::timestamptz 
        and valid < '2014-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_06_station on t2014_06(station);
CREATE INDEX t2014_06_valid_idx on t2014_06(valid);
GRANT SELECT on t2014_06 to nobody,apache;


 create table t2014_07( 
  CONSTRAINT __t2014_07_check 
  CHECK(valid >= '2014-07-01 00:00+00'::timestamptz 
        and valid < '2014-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_07_station on t2014_07(station);
CREATE INDEX t2014_07_valid_idx on t2014_07(valid);
GRANT SELECT on t2014_07 to nobody,apache;


 create table t2014_08( 
  CONSTRAINT __t2014_08_check 
  CHECK(valid >= '2014-08-01 00:00+00'::timestamptz 
        and valid < '2014-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_08_station on t2014_08(station);
CREATE INDEX t2014_08_valid_idx on t2014_08(valid);
GRANT SELECT on t2014_08 to nobody,apache;


 create table t2014_09( 
  CONSTRAINT __t2014_09_check 
  CHECK(valid >= '2014-09-01 00:00+00'::timestamptz 
        and valid < '2014-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_09_station on t2014_09(station);
CREATE INDEX t2014_09_valid_idx on t2014_09(valid);
GRANT SELECT on t2014_09 to nobody,apache;


 create table t2014_10( 
  CONSTRAINT __t2014_10_check 
  CHECK(valid >= '2014-10-01 00:00+00'::timestamptz 
        and valid < '2014-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_10_station on t2014_10(station);
CREATE INDEX t2014_10_valid_idx on t2014_10(valid);
GRANT SELECT on t2014_10 to nobody,apache;


 create table t2014_11( 
  CONSTRAINT __t2014_11_check 
  CHECK(valid >= '2014-11-01 00:00+00'::timestamptz 
        and valid < '2014-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_11_station on t2014_11(station);
CREATE INDEX t2014_11_valid_idx on t2014_11(valid);
GRANT SELECT on t2014_11 to nobody,apache;


 create table t2014_12( 
  CONSTRAINT __t2014_12_check 
  CHECK(valid >= '2014-12-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_12_station on t2014_12(station);
CREATE INDEX t2014_12_valid_idx on t2014_12(valid);
GRANT SELECT on t2014_12 to nobody,apache;

create table t2015_01( 
  CONSTRAINT __t2015_01_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2015-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_01_station on t2015_01(station);
CREATE INDEX t2015_01_valid_idx on t2015_01(valid);
GRANT SELECT on t2015_01 to nobody,apache;


 create table t2015_02( 
  CONSTRAINT __t2015_02_check 
  CHECK(valid >= '2015-02-01 00:00+00'::timestamptz 
        and valid < '2015-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_02_station on t2015_02(station);
CREATE INDEX t2015_02_valid_idx on t2015_02(valid);
GRANT SELECT on t2015_02 to nobody,apache;


 create table t2015_03( 
  CONSTRAINT __t2015_03_check 
  CHECK(valid >= '2015-03-01 00:00+00'::timestamptz 
        and valid < '2015-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_03_station on t2015_03(station);
CREATE INDEX t2015_03_valid_idx on t2015_03(valid);
GRANT SELECT on t2015_03 to nobody,apache;


 create table t2015_04( 
  CONSTRAINT __t2015_04_check 
  CHECK(valid >= '2015-04-01 00:00+00'::timestamptz 
        and valid < '2015-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_04_station on t2015_04(station);
CREATE INDEX t2015_04_valid_idx on t2015_04(valid);
GRANT SELECT on t2015_04 to nobody,apache;


 create table t2015_05( 
  CONSTRAINT __t2015_05_check 
  CHECK(valid >= '2015-05-01 00:00+00'::timestamptz 
        and valid < '2015-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_05_station on t2015_05(station);
CREATE INDEX t2015_05_valid_idx on t2015_05(valid);
GRANT SELECT on t2015_05 to nobody,apache;


 create table t2015_06( 
  CONSTRAINT __t2015_06_check 
  CHECK(valid >= '2015-06-01 00:00+00'::timestamptz 
        and valid < '2015-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_06_station on t2015_06(station);
CREATE INDEX t2015_06_valid_idx on t2015_06(valid);
GRANT SELECT on t2015_06 to nobody,apache;


 create table t2015_07( 
  CONSTRAINT __t2015_07_check 
  CHECK(valid >= '2015-07-01 00:00+00'::timestamptz 
        and valid < '2015-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_07_station on t2015_07(station);
CREATE INDEX t2015_07_valid_idx on t2015_07(valid);
GRANT SELECT on t2015_07 to nobody,apache;


 create table t2015_08( 
  CONSTRAINT __t2015_08_check 
  CHECK(valid >= '2015-08-01 00:00+00'::timestamptz 
        and valid < '2015-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_08_station on t2015_08(station);
CREATE INDEX t2015_08_valid_idx on t2015_08(valid);
GRANT SELECT on t2015_08 to nobody,apache;


 create table t2015_09( 
  CONSTRAINT __t2015_09_check 
  CHECK(valid >= '2015-09-01 00:00+00'::timestamptz 
        and valid < '2015-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_09_station on t2015_09(station);
CREATE INDEX t2015_09_valid_idx on t2015_09(valid);
GRANT SELECT on t2015_09 to nobody,apache;


 create table t2015_10( 
  CONSTRAINT __t2015_10_check 
  CHECK(valid >= '2015-10-01 00:00+00'::timestamptz 
        and valid < '2015-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_10_station on t2015_10(station);
CREATE INDEX t2015_10_valid_idx on t2015_10(valid);
GRANT SELECT on t2015_10 to nobody,apache;


 create table t2015_11( 
  CONSTRAINT __t2015_11_check 
  CHECK(valid >= '2015-11-01 00:00+00'::timestamptz 
        and valid < '2015-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_11_station on t2015_11(station);
CREATE INDEX t2015_11_valid_idx on t2015_11(valid);
GRANT SELECT on t2015_11 to nobody,apache;


 create table t2015_12( 
  CONSTRAINT __t2015_12_check 
  CHECK(valid >= '2015-12-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_12_station on t2015_12(station);
CREATE INDEX t2015_12_valid_idx on t2015_12(valid);
GRANT SELECT on t2015_12 to nobody,apache;
create table t2016_01( 
  CONSTRAINT __t2016_01_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2016-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_01_station on t2016_01(station);
CREATE INDEX t2016_01_valid_idx on t2016_01(valid);
GRANT SELECT on t2016_01 to nobody,apache;


 create table t2016_02( 
  CONSTRAINT __t2016_02_check 
  CHECK(valid >= '2016-02-01 00:00+00'::timestamptz 
        and valid < '2016-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_02_station on t2016_02(station);
CREATE INDEX t2016_02_valid_idx on t2016_02(valid);
GRANT SELECT on t2016_02 to nobody,apache;


 create table t2016_03( 
  CONSTRAINT __t2016_03_check 
  CHECK(valid >= '2016-03-01 00:00+00'::timestamptz 
        and valid < '2016-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_03_station on t2016_03(station);
CREATE INDEX t2016_03_valid_idx on t2016_03(valid);
GRANT SELECT on t2016_03 to nobody,apache;


 create table t2016_04( 
  CONSTRAINT __t2016_04_check 
  CHECK(valid >= '2016-04-01 00:00+00'::timestamptz 
        and valid < '2016-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_04_station on t2016_04(station);
CREATE INDEX t2016_04_valid_idx on t2016_04(valid);
GRANT SELECT on t2016_04 to nobody,apache;


 create table t2016_05( 
  CONSTRAINT __t2016_05_check 
  CHECK(valid >= '2016-05-01 00:00+00'::timestamptz 
        and valid < '2016-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_05_station on t2016_05(station);
CREATE INDEX t2016_05_valid_idx on t2016_05(valid);
GRANT SELECT on t2016_05 to nobody,apache;


 create table t2016_06( 
  CONSTRAINT __t2016_06_check 
  CHECK(valid >= '2016-06-01 00:00+00'::timestamptz 
        and valid < '2016-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_06_station on t2016_06(station);
CREATE INDEX t2016_06_valid_idx on t2016_06(valid);
GRANT SELECT on t2016_06 to nobody,apache;


 create table t2016_07( 
  CONSTRAINT __t2016_07_check 
  CHECK(valid >= '2016-07-01 00:00+00'::timestamptz 
        and valid < '2016-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_07_station on t2016_07(station);
CREATE INDEX t2016_07_valid_idx on t2016_07(valid);
GRANT SELECT on t2016_07 to nobody,apache;


 create table t2016_08( 
  CONSTRAINT __t2016_08_check 
  CHECK(valid >= '2016-08-01 00:00+00'::timestamptz 
        and valid < '2016-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_08_station on t2016_08(station);
CREATE INDEX t2016_08_valid_idx on t2016_08(valid);
GRANT SELECT on t2016_08 to nobody,apache;


 create table t2016_09( 
  CONSTRAINT __t2016_09_check 
  CHECK(valid >= '2016-09-01 00:00+00'::timestamptz 
        and valid < '2016-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_09_station on t2016_09(station);
CREATE INDEX t2016_09_valid_idx on t2016_09(valid);
GRANT SELECT on t2016_09 to nobody,apache;


 create table t2016_10( 
  CONSTRAINT __t2016_10_check 
  CHECK(valid >= '2016-10-01 00:00+00'::timestamptz 
        and valid < '2016-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_10_station on t2016_10(station);
CREATE INDEX t2016_10_valid_idx on t2016_10(valid);
GRANT SELECT on t2016_10 to nobody,apache;


 create table t2016_11( 
  CONSTRAINT __t2016_11_check 
  CHECK(valid >= '2016-11-01 00:00+00'::timestamptz 
        and valid < '2016-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_11_station on t2016_11(station);
CREATE INDEX t2016_11_valid_idx on t2016_11(valid);
GRANT SELECT on t2016_11 to nobody,apache;


 create table t2016_12( 
  CONSTRAINT __t2016_12_check 
  CHECK(valid >= '2016-12-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_12_station on t2016_12(station);
CREATE INDEX t2016_12_valid_idx on t2016_12(valid);
GRANT SELECT on t2016_12 to nobody,apache;
create table t2017_01( 
  CONSTRAINT __t2017_01_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2017-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_01_station on t2017_01(station);
CREATE INDEX t2017_01_valid_idx on t2017_01(valid);
GRANT SELECT on t2017_01 to nobody,apache;


 create table t2017_02( 
  CONSTRAINT __t2017_02_check 
  CHECK(valid >= '2017-02-01 00:00+00'::timestamptz 
        and valid < '2017-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_02_station on t2017_02(station);
CREATE INDEX t2017_02_valid_idx on t2017_02(valid);
GRANT SELECT on t2017_02 to nobody,apache;


 create table t2017_03( 
  CONSTRAINT __t2017_03_check 
  CHECK(valid >= '2017-03-01 00:00+00'::timestamptz 
        and valid < '2017-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_03_station on t2017_03(station);
CREATE INDEX t2017_03_valid_idx on t2017_03(valid);
GRANT SELECT on t2017_03 to nobody,apache;


 create table t2017_04( 
  CONSTRAINT __t2017_04_check 
  CHECK(valid >= '2017-04-01 00:00+00'::timestamptz 
        and valid < '2017-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_04_station on t2017_04(station);
CREATE INDEX t2017_04_valid_idx on t2017_04(valid);
GRANT SELECT on t2017_04 to nobody,apache;


 create table t2017_05( 
  CONSTRAINT __t2017_05_check 
  CHECK(valid >= '2017-05-01 00:00+00'::timestamptz 
        and valid < '2017-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_05_station on t2017_05(station);
CREATE INDEX t2017_05_valid_idx on t2017_05(valid);
GRANT SELECT on t2017_05 to nobody,apache;


 create table t2017_06( 
  CONSTRAINT __t2017_06_check 
  CHECK(valid >= '2017-06-01 00:00+00'::timestamptz 
        and valid < '2017-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_06_station on t2017_06(station);
CREATE INDEX t2017_06_valid_idx on t2017_06(valid);
GRANT SELECT on t2017_06 to nobody,apache;


 create table t2017_07( 
  CONSTRAINT __t2017_07_check 
  CHECK(valid >= '2017-07-01 00:00+00'::timestamptz 
        and valid < '2017-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_07_station on t2017_07(station);
CREATE INDEX t2017_07_valid_idx on t2017_07(valid);
GRANT SELECT on t2017_07 to nobody,apache;


 create table t2017_08( 
  CONSTRAINT __t2017_08_check 
  CHECK(valid >= '2017-08-01 00:00+00'::timestamptz 
        and valid < '2017-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_08_station on t2017_08(station);
CREATE INDEX t2017_08_valid_idx on t2017_08(valid);
GRANT SELECT on t2017_08 to nobody,apache;


 create table t2017_09( 
  CONSTRAINT __t2017_09_check 
  CHECK(valid >= '2017-09-01 00:00+00'::timestamptz 
        and valid < '2017-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_09_station on t2017_09(station);
CREATE INDEX t2017_09_valid_idx on t2017_09(valid);
GRANT SELECT on t2017_09 to nobody,apache;


 create table t2017_10( 
  CONSTRAINT __t2017_10_check 
  CHECK(valid >= '2017-10-01 00:00+00'::timestamptz 
        and valid < '2017-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_10_station on t2017_10(station);
CREATE INDEX t2017_10_valid_idx on t2017_10(valid);
GRANT SELECT on t2017_10 to nobody,apache;


 create table t2017_11( 
  CONSTRAINT __t2017_11_check 
  CHECK(valid >= '2017-11-01 00:00+00'::timestamptz 
        and valid < '2017-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_11_station on t2017_11(station);
CREATE INDEX t2017_11_valid_idx on t2017_11(valid);
GRANT SELECT on t2017_11 to nobody,apache;


 create table t2017_12( 
  CONSTRAINT __t2017_12_check 
  CHECK(valid >= '2017-12-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_12_station on t2017_12(station);
CREATE INDEX t2017_12_valid_idx on t2017_12(valid);
GRANT SELECT on t2017_12 to nobody,apache;

create table t2018_01( 
  CONSTRAINT __t2018_01_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz 
        and valid < '2018-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_01_station on t2018_01(station);
CREATE INDEX t2018_01_valid_idx on t2018_01(valid);
GRANT SELECT on t2018_01 to nobody,apache;


 create table t2018_02( 
  CONSTRAINT __t2018_02_check 
  CHECK(valid >= '2018-02-01 00:00+00'::timestamptz 
        and valid < '2018-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_02_station on t2018_02(station);
CREATE INDEX t2018_02_valid_idx on t2018_02(valid);
GRANT SELECT on t2018_02 to nobody,apache;


 create table t2018_03( 
  CONSTRAINT __t2018_03_check 
  CHECK(valid >= '2018-03-01 00:00+00'::timestamptz 
        and valid < '2018-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_03_station on t2018_03(station);
CREATE INDEX t2018_03_valid_idx on t2018_03(valid);
GRANT SELECT on t2018_03 to nobody,apache;


 create table t2018_04( 
  CONSTRAINT __t2018_04_check 
  CHECK(valid >= '2018-04-01 00:00+00'::timestamptz 
        and valid < '2018-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_04_station on t2018_04(station);
CREATE INDEX t2018_04_valid_idx on t2018_04(valid);
GRANT SELECT on t2018_04 to nobody,apache;


 create table t2018_05( 
  CONSTRAINT __t2018_05_check 
  CHECK(valid >= '2018-05-01 00:00+00'::timestamptz 
        and valid < '2018-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_05_station on t2018_05(station);
CREATE INDEX t2018_05_valid_idx on t2018_05(valid);
GRANT SELECT on t2018_05 to nobody,apache;


 create table t2018_06( 
  CONSTRAINT __t2018_06_check 
  CHECK(valid >= '2018-06-01 00:00+00'::timestamptz 
        and valid < '2018-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_06_station on t2018_06(station);
CREATE INDEX t2018_06_valid_idx on t2018_06(valid);
GRANT SELECT on t2018_06 to nobody,apache;


 create table t2018_07( 
  CONSTRAINT __t2018_07_check 
  CHECK(valid >= '2018-07-01 00:00+00'::timestamptz 
        and valid < '2018-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_07_station on t2018_07(station);
CREATE INDEX t2018_07_valid_idx on t2018_07(valid);
GRANT SELECT on t2018_07 to nobody,apache;


 create table t2018_08( 
  CONSTRAINT __t2018_08_check 
  CHECK(valid >= '2018-08-01 00:00+00'::timestamptz 
        and valid < '2018-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_08_station on t2018_08(station);
CREATE INDEX t2018_08_valid_idx on t2018_08(valid);
GRANT SELECT on t2018_08 to nobody,apache;


 create table t2018_09( 
  CONSTRAINT __t2018_09_check 
  CHECK(valid >= '2018-09-01 00:00+00'::timestamptz 
        and valid < '2018-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_09_station on t2018_09(station);
CREATE INDEX t2018_09_valid_idx on t2018_09(valid);
GRANT SELECT on t2018_09 to nobody,apache;


 create table t2018_10( 
  CONSTRAINT __t2018_10_check 
  CHECK(valid >= '2018-10-01 00:00+00'::timestamptz 
        and valid < '2018-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_10_station on t2018_10(station);
CREATE INDEX t2018_10_valid_idx on t2018_10(valid);
GRANT SELECT on t2018_10 to nobody,apache;


 create table t2018_11( 
  CONSTRAINT __t2018_11_check 
  CHECK(valid >= '2018-11-01 00:00+00'::timestamptz 
        and valid < '2018-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_11_station on t2018_11(station);
CREATE INDEX t2018_11_valid_idx on t2018_11(valid);
GRANT SELECT on t2018_11 to nobody,apache;


 create table t2018_12( 
  CONSTRAINT __t2018_12_check 
  CHECK(valid >= '2018-12-01 00:00+00'::timestamptz 
        and valid < '2019-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_12_station on t2018_12(station);
CREATE INDEX t2018_12_valid_idx on t2018_12(valid);
GRANT SELECT on t2018_12 to nobody,apache;

create table t2019_01( 
  CONSTRAINT __t2019_01_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz 
        and valid < '2019-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_01_station on t2019_01(station);
CREATE INDEX t2019_01_valid_idx on t2019_01(valid);
GRANT SELECT on t2019_01 to nobody,apache;


 create table t2019_02( 
  CONSTRAINT __t2019_02_check 
  CHECK(valid >= '2019-02-01 00:00+00'::timestamptz 
        and valid < '2019-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_02_station on t2019_02(station);
CREATE INDEX t2019_02_valid_idx on t2019_02(valid);
GRANT SELECT on t2019_02 to nobody,apache;


 create table t2019_03( 
  CONSTRAINT __t2019_03_check 
  CHECK(valid >= '2019-03-01 00:00+00'::timestamptz 
        and valid < '2019-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_03_station on t2019_03(station);
CREATE INDEX t2019_03_valid_idx on t2019_03(valid);
GRANT SELECT on t2019_03 to nobody,apache;


 create table t2019_04( 
  CONSTRAINT __t2019_04_check 
  CHECK(valid >= '2019-04-01 00:00+00'::timestamptz 
        and valid < '2019-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_04_station on t2019_04(station);
CREATE INDEX t2019_04_valid_idx on t2019_04(valid);
GRANT SELECT on t2019_04 to nobody,apache;


 create table t2019_05( 
  CONSTRAINT __t2019_05_check 
  CHECK(valid >= '2019-05-01 00:00+00'::timestamptz 
        and valid < '2019-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_05_station on t2019_05(station);
CREATE INDEX t2019_05_valid_idx on t2019_05(valid);
GRANT SELECT on t2019_05 to nobody,apache;


 create table t2019_06( 
  CONSTRAINT __t2019_06_check 
  CHECK(valid >= '2019-06-01 00:00+00'::timestamptz 
        and valid < '2019-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_06_station on t2019_06(station);
CREATE INDEX t2019_06_valid_idx on t2019_06(valid);
GRANT SELECT on t2019_06 to nobody,apache;


 create table t2019_07( 
  CONSTRAINT __t2019_07_check 
  CHECK(valid >= '2019-07-01 00:00+00'::timestamptz 
        and valid < '2019-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_07_station on t2019_07(station);
CREATE INDEX t2019_07_valid_idx on t2019_07(valid);
GRANT SELECT on t2019_07 to nobody,apache;


 create table t2019_08( 
  CONSTRAINT __t2019_08_check 
  CHECK(valid >= '2019-08-01 00:00+00'::timestamptz 
        and valid < '2019-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_08_station on t2019_08(station);
CREATE INDEX t2019_08_valid_idx on t2019_08(valid);
GRANT SELECT on t2019_08 to nobody,apache;


 create table t2019_09( 
  CONSTRAINT __t2019_09_check 
  CHECK(valid >= '2019-09-01 00:00+00'::timestamptz 
        and valid < '2019-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_09_station on t2019_09(station);
CREATE INDEX t2019_09_valid_idx on t2019_09(valid);
GRANT SELECT on t2019_09 to nobody,apache;


 create table t2019_10( 
  CONSTRAINT __t2019_10_check 
  CHECK(valid >= '2019-10-01 00:00+00'::timestamptz 
        and valid < '2019-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_10_station on t2019_10(station);
CREATE INDEX t2019_10_valid_idx on t2019_10(valid);
GRANT SELECT on t2019_10 to nobody,apache;


 create table t2019_11( 
  CONSTRAINT __t2019_11_check 
  CHECK(valid >= '2019-11-01 00:00+00'::timestamptz 
        and valid < '2019-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_11_station on t2019_11(station);
CREATE INDEX t2019_11_valid_idx on t2019_11(valid);
GRANT SELECT on t2019_11 to nobody,apache;


 create table t2019_12( 
  CONSTRAINT __t2019_12_check 
  CHECK(valid >= '2019-12-01 00:00+00'::timestamptz 
        and valid < '2020-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_12_station on t2019_12(station);
CREATE INDEX t2019_12_valid_idx on t2019_12(valid);
GRANT SELECT on t2019_12 to nobody,apache;