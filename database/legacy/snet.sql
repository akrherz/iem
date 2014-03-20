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
GRANT SELECT on t2014_03 to nobody,apache;

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
