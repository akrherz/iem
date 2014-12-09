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
