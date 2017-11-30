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